"""
utils.py

Author: Tobias Seydewitz
Date: 20.10.17
Mail: tobi.seyde@gmail.com

Description:
"""
import os
import re
import math
import time
import copy
import pyproj
import logging
import urllib.request
import shapely.geometry

import numpy as np
import pandas as pd
import rasterio as rio
import geopandas as gpd
from pathlib import Path

from collections import namedtuple
from contextlib import contextmanager
from rasterio import warp, merge, coords


__all__ = [
    'LOGGER',
    'get_data_dir',
    'execute_threads',
    'download',
    'write_binary',
    'tile_index',
    'clip_worker',
    'download_worker',
    'alignment_worker',
    'harmonization_worker',
]

LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


# Common
def get_data_dir(path: str) -> namedtuple:
    # TODO doc
    dir_structure = {
        os.path.split(root)[-1]: Path(root)
        for root, *_ in os.walk(path)
    }
    Directories = namedtuple('Directories', dir_structure.keys())
    return Directories(**dir_structure)


@contextmanager
def benchmark():
    """
    Benchmark functions or else with a
    context manager e.g.

    with benchmark():
        do()
        foo()

    >> 2
    """
    start = time.time()
    try:
        yield None
    finally:
        print(time.time() - start)


def ratio(numerator, denominator):
    """
    Compute ratio of scaled to 100.

    :param numerator: numeric
    :param denominator: numeric
    :return: float
        Ratio rounded to tenth and scaled to 100
    """
    return round((numerator / denominator) * 100, 1)


def default(*args):
    """
    Default callback for execute_threads. A custom callback must accept two
    parameters, message and ratio.
    """
    pass


def execute_threads(to_execute, max_threads, msg='{} of 100 %', callback=default):
    """


    :param to_execute: list or iterable
        An iterable of thread objects.
    :param max_threads: int
        Maximum number of threads to start respectively run.
    :param msg: str
        Message to emit after a set of threads finished.
    :param callback: func
        Function to call after a set of threads is finished.
        Must accept a message (str) and a numeric (float) as
        parameter. Numeric is ratio of finished threads in
        percent.
    """
    stack = copy.copy(to_execute)
    current = []

    if len(stack) % max_threads != 0:
        reminder = len(stack) % max_threads
        execute_threads(stack[-reminder:], reminder, msg='', callback=default)
        stack = stack[:-reminder]

    while stack:
        thread = stack.pop()
        thread.start()
        current.append(thread)

        if len(current) == max_threads:
            [thread.join() for thread in current]
            callback(msg, ratio((len(to_execute) - len(stack)), len(to_execute)))
            current = []


# Download
def download(url, **kwargs):
    # TODO doc
    request = urllib.request.Request(url, **kwargs)
    response = None

    try:
        response = urllib.request.urlopen(request)

    except:
        pass  # log error -> unable to download URL

    if response is not None:
        return response.read()

    return response


def write_binary(content, to_path):
    # TODO doc
    with open(to_path, 'wb') as dst:
        dst.write(content)


# GIS
def read_raster(item):
    """
    Helper method to return a raster file as a opened instance of
    rasterio.io.DatasetReader in read mode.

    :param item: str, pathlib.Path or rasterio.io.DatasetReader
        Should be the path to the raster file on filesystem as a string
        or pathlib.Path object. If item is a instance of DatasetReader
        the function returns immediately.
    :return: rasterio.io.DatasetReader
        Returns an instance of rasterio.io.DatasetReader in read mode.
    """
    if isinstance(item, rio.io.DatasetReader):
        return item

    else:
        try:
            path = str(item)  # Cast pathlib.Path to string
            return rio.open(path, 'r')

        except:
            msg = 'Attr {}, Type {} is not a valid raster file'.format(item, type(item))
            raise ValueError(msg)


def fetch_metadata(from_path_or_reader, *args):
    # TODO doc
    """
    This method fetches user selected metadata features from a raster file and
    returns them as a named tuple where the attribute name is the selected
    metadata feature key and the assigned value the corresponding metadata
    feature. Please, refer to the documentation of rasterio for a comprehensive
    list of metadata features provided by a raster file.

    :param from_path_or_reader: str, pathlib.Path or rasterio.io.DatasetReader
        Path to the raster file on drive as string or pathlib.Path object or a
        opened raster dataset.
    :param args: str

    :return: namedtuple
        The requested metadata features as a namedtuple where the attribute
        name is the selected metadata feature key and the assigned value the
        corresponding metadata feature.
        Example:
        fetch_metadata(('bounds', 'crs'), path)
        (bounds=value, crs=value)
    """
    reader = read_raster(from_path_or_reader)

    values = []
    for f in args:
        value = reader.__getattribute__(f)

        if value is not None:
            values.append(value)

        else:
            raise ValueError('{} is not set'.format(f))

    # Warning closes raster reader can be a huge pitfall
    reader.close()

    if len(values) > 1:
        Metadata = namedtuple('Metadata', args)
        return Metadata(*values)

    return values[0]


def reproject_from(in_path, to_crs, out_path):
    """
    This method re-projects a raster file to a selected coordinate
    reference system.

    :param in_path: str
        Path to raster file on drive
    :param to_crs: dict
        Target coordinate reference system for re-projection
    :param out_path: str
        Path where the reprojected raster file should be stored
    :return: str
        Path where the reprojected raster file is stored
    """
    with rio.open(in_path, 'r') as src:
        affine, width, height = rio.warp.calculate_default_transform(
            src_crs=src.crs,
            dst_crs=to_crs,
            width=src.width,
            height=src.height,
            **src.bounds._asdict(),
        )

        kwargs = src.profile.copy()
        kwargs.update(
            transform=affine,
            width=width,
            height=height,
            crs=to_crs
        )

        with rio.open(out_path, 'w', **kwargs) as dst:
            for idx in src.indexes:
                rio.warp.reproject(
                    source=rio.band(src, idx),
                    destination=rio.band(dst, idx)
                )

        return out_path


def reproject_like(template, in_path, out_path: str):
    # TODO doc
    crs, transform, width, height = fetch_metadata(template, 'crs', 'transform', 'width', 'height')

    with rio.open(in_path, 'r') as src:
        out_kwargs = src.profile.copy()
        out_kwargs.update({
            'crs': crs,
            'transform': transform,
            'width': width,
            'height': height
        })

        with rio.open(out_path, 'w', **out_kwargs) as dst:
            rio.warp.reproject(source=rio.band(src, list(range(1, src.count + 1))),
                               destination=rio.band(dst, list(range(1, src.count + 1))))

    return out_path


def reproject_bounds(bounds, source_crs, target_crs):
    """
    This method re-projects the coordinates of an bounds object to the requested
    coordinate system.

    :param bounds: namedtuple
        Should be a namedtuple containing the attributes
        left, right, top and bottom.
    :param source_crs: dict
        The coordinate reference system of the bounds object as a dictionary
        with the following shape:
        {'init': 'epsg:<id>'} where <id> is the epsg number of the crs
    :param target_crs: dict
        The coordinates system for the re-projection of the bounds object.
        Shape should be equal to source_crs.
    :return: namedtuple(left, right, top, bottom)
        Reprojected bounds object
    """
    p1 = pyproj.Proj(**source_crs)
    p2 = pyproj.Proj(**target_crs)

    left, bottom = pyproj.transform(p1, p2, bounds.left, bounds.bottom)
    right, top = pyproj.transform(p1, p2, bounds.right, bounds.top)

    BoundingBox = namedtuple('BoundingBox', 'left bottom right top')
    return BoundingBox(left, bottom, right, top)


def merge_from(rasters, **kwargs):
    """
    Merges a list of raster files to one single raster dataset.
    This method is wrapped around the rasterio.merge.merge method
    therefore this method accept keyword arguments as well.

    :param rasters: list
        A list of strings or pathlib.Path objects where each list element reference a path to a
        raster file on drive.
    :param kwargs:
        Please refer to the rasterio documentation for a full list
        of possible keyword arguments.
    :return: namedtuple(data, affine)
        A namedtuple with the attributes data and affine, where the parameter
        data contains the merged data of the raster files as a numpy.ndarray
        and affine an affine transformation matrix.
    """
    readers = [read_raster(raster) for raster in rasters]

    dst, affine = rio.merge.merge(readers, **kwargs)

    [reader.close() for reader in readers]
    Merge = namedtuple('Merge', 'data affine')
    return Merge(dst, affine)


def merge_alike(with_template, to_merge):
    """
    Merges the input raster files like a template raster, hence the output
    dataset has same bounds and resolution as the template raster. Both sets
    must have the same coordinate reference system.

    :param with_template: str
        Path to the template raster file
    :param to_merge: list
        A list of strings where each list element reference a path to a
        raster file on drive.
    :return: namedtuple(data, affine)
        A namedtuple with the attributes data and affine, where the parameter
        data contains the merged data of the raster files as a numpy.ndarray
        and affine an affine transformation matrix.
    """
    bounds, res = fetch_metadata(with_template, 'bounds', 'res')
    return merge_from(to_merge, bounds=bounds, res=res)


def clip_raster(raster, dst_bounds):
    # TODO doc
    src = read_raster(raster)
    src_bounds = src.bounds

    if coords.disjoint_bounds(src_bounds, dst_bounds):
        msg = 'Raster bounds {} are not covered by clipping bounds {}'.format(src_bounds, dst_bounds)
        raise ValueError(msg)

    window = src.window(*dst_bounds)
    window = window.round_lengths(op='ceil')
    transform = src.window_transform(window)
    data = src.read(window=window, out_shape=(src.count, window.height, window.width))

    src.close()
    return data, transform


def write(data, to_path, **kwargs):
    """
    Writes a multi-dimensional numpy.ndarray as a raster dataset to file.
    This method is wrapped around the rasterio.open method therefore
    you can modify the methods behavior with kwargs arguments provided
    by the rasterio documentation.

    :param data: numpy.ndarray
        A multi-dimensional numpy array. If array has three dimensions
        each dimension depict a raster band. If array has two dimensions
        the resulting raster file contains a single band.
    :param to_path: str
        Path where the new raster file should be stored
    :param kwargs:
        Keyword arguments consumed by the rasterio.open function.
        Please refer to the rasterio documentation for a comprehensive
        list of possible keyword arguments.
    :return: str
        Path where the raster file is stored
    """
    if len(data.shape) == 3:
        idx, height, width = data.shape  # z, y, x

    elif len(data.shape) == 2:
        idx = 1  # z
        height, width = data.shape  # y, x
        data = np.reshape(data.copy(), (idx, height, width))

    else:
        raise ValueError('Please, provide a valid dataset')

    dtype = data.dtype
    kwargs.update(
        count=idx,
        height=height,
        width=width,
        dtype=dtype
    )

    with rio.open(to_path, 'w', **kwargs) as dst:
        for i in range(idx):
            dst.write(data[i], i + 1)  # rasterio band index start at one, thus we increment by one

    return to_path


def polygon_from(bounds):
    """
    Creates a polygon object from a bounds object.

    :param bounds: namedtuple
        Should be a namedtuple containing the attributes
        left, right, top and bottom
    :return: shapely.geometry.Polygon
        The polygon object in extent of the provided bounds
        object.
    """
    x_points = ['left', 'left', 'right', 'right']
    y_points = ['top', 'bottom', 'bottom', 'top']

    polygon_bounds = [
        (bounds.__getattribute__(x), bounds.__getattribute__(y))
        for x, y in zip(x_points, y_points)
    ]

    return shapely.geometry.Polygon(polygon_bounds)


def polygoniz(rasters, target_crs):
    # TODO doc
    """
    This function creates a tile index from a list of raster files.

    :param rasters: list
        Pending
    :param target_crs: dict
        If the raster files have different coordinate reference systems
        this argument prevents a messed up dataset.
    :return: geopandas.GeoSeries
        Each element of the series is a polygon
        covering the corresponding raster file.
    """
    polygons = []
    for raster in rasters:
        bounds, crs = fetch_metadata(raster, 'bounds', 'crs')

        if crs != target_crs:
            bounds = reproject_bounds(bounds, crs, target_crs)

        polygon = polygon_from(bounds)
        polygons.append(polygon)

    geometry = gpd.GeoSeries(polygons)
    geometry.crs = target_crs

    return geometry


def tile_index(rasters, target_crs, **kwargs):
    # TODO doc
    """
    Description Pending

    :param rasters: list
        A list of str where each element is a path to a raster file
        on disk.
    :param target_crs: dict
        The coordinate reference system which should be applied on
        the tile index dataset.
    :param kwargs:
    :return: geopandas.GeoDataFrame
    """
    geometry = polygoniz(rasters, target_crs)
    features = pd.DataFrame(kwargs)

    return gpd.GeoDataFrame(features, geometry=geometry)


def orientation_to_int(orient):
    # TODO doc
    coor, orient = re.match(r'(?P<coor>\d+)(?P<orient>[NSWE])', orient, re.I).groups()

    if orient.lower() in ('n', 'e'):
        return int(coor)

    else:
        return -1 * int(coor)


def int_to_orient(x, y):
    # TODO round method ceil, floor
    """
    Converts a x- and y-coordinate to an integer north/south,
    west/east string representation.
    Example: (x=-179.3457, y=80.2222) -> 80N_179W

    :param x: float
        Longitudinal coordinate
    :param y: float
        Latitudinal coordinate
    :return: str
        Lat/Lon coordinates as a integer string with the according
        orientation.
    """
    x = round(x)
    y = round(y)

    lng, we = (-1 * x, 'W') if x < 0 else (x, 'E')
    lat, ns = (-1 * y, 'S') if y < 0 else (y, 'N')

    return '{:02d}{}_{:03d}{}'.format(lat, ns, lng, we)


def round_bounds(bounds):
    # TODO doc, round method ceil, floor
    attrs = ('left', 'bottom', 'right', 'top')

    coors = []
    for attr in attrs:
        coord = bounds.__getattribute__(attr)
        coors.append(round(coord))

    BoundingBox = namedtuple('BoundingBox', attrs)
    return BoundingBox(*coors)


# Statistic/Compute
def binary_jaccard(arr1, arr2, return_matrix=False):
    """
    Calculates the Jaccard Index (JI) of two equal sized binary arrays or vectors.
    If return_matrix is set to true the method provides the JI and the necessary
    calculation matrix as a named tuple. Attention, this method does not work in-place!

    :param arr1, arr2: numpy.ndarray, list or tuple
        Both array alike objects sized in equal dimensions should contain exclusively
        binary data (1,0).
    :param return_matrix: boolean
        Optional, a boolean value determining the return of the calculation matrix.
    :return: float OR (float, namedtuple(m11, m01, m10, m00))
        Default, the method returns only the JI if, return_matrix is set to true the
        method returns the JI and the computation matrix.
        The Matrix contains the following attributes:
        m11 = total number of attributes where arr1 == 1 and arr2 == 1
        m10 = total number of attributes where arr1 == 1 and arr2 == 0
        m01 = total number of attributes where arr1 == 0 and arr2 == 1
        m00 = not required, set to 0
    """
    a, b = np.array(arr1, dtype=np.int8), np.array(arr2, dtype=np.int8)

    if np.sum(np.logical_or(a < 0, a > 1)) != 0 or np.sum(np.logical_or(b < 0, b > 1)) != 0:
        raise ValueError('Attributes should contain only binary values')

    c = a + b
    a = (b - c) + b  # a = (a - C) + a, m10 = a == 1
    b = (a - c) + a  # b = (b - C) + b, m01 = b == 1

    # Total number of attributes where a == 1 and b == 1
    m11 = np.sum(c == 2)
    # Total number of attributes where a == 1 and b == 0
    m10 = np.sum(a == -1)
    # Total number of attributes where a == 0 and b == 1
    m01 = np.sum(b == -1)

    # TODO prevent division by zero error
    jaccard = m11 / (m10 + m01 + m11)

    if return_matrix:
        Matrix = namedtuple('Matrix', 'm11 m10 m01 m00')
        return jaccard, Matrix(m11, m10, m01, 0)
    return jaccard


def simple_matching_coefficient(arr1, arr2, return_matrix=False):
    """
    Calculates the Simple Matching Coefficient (SMC) of two equal sized arrays or vectors.
    If return_matrix is set to true the method provides the SMC and the necessary calculation
    matrix as a named tuple. Attention, this method does not work in-place!

    :param arr1, arr2: numpy.ndarray, list, tuple
        Both array alike objects sized in equal dimensions should contain exclusively
        binary data (1,0).
    :param return_matrix: boolean
        Optional, a boolean value determining the return of the calculation matrix.
    :return: float OR (float, namedtuple(m11, m01, m10, m00))
        Default, the method returns only the SMC, if return_matrix is
        set to true the method returns the SMC and the computation matrix.
        The Matrix contains the following attributes:
        m11 = total number of attributes where arr1 == 1 and arr2 == 1
        m10 = total number of attributes where arr1 == 1 and arr2 == 0
        m01 = total number of attributes where arr1 == 0 and arr2 == 1
        m00 = total number of attributes where arr1 == 0 and arr2 == 0
    """
    _, matrix = binary_jaccard(arr1, arr2, True)
    a = np.array(arr1, dtype=np.int8)

    # Total number of attributes where a == 0 and B == 0
    m00 = a.size - sum(matrix)

    smc = (matrix.m11 + m00) / a.size

    if return_matrix:
        matrix = matrix._replace(m00=m00)
        return smc, matrix
    return smc


def square_mask(mask_size, center, side_length):
    # TODO doc
    pass


def circle_mask(mask_size, center, radius):
    # TODO doc
    cx, cy = center
    sx, sy = mask_size

    y, x = np.ogrid[:sx, :sy]

    mask = (x-cx)**2 + (y-cy)**2 <= radius**2

    return mask


def haversine(coordinate1, coordinate2, scale='m'):
    # TODO doc
    scales = {
        'cm': lambda d: d * 100,
        'km': lambda d: d * 0.001,
    }
    earth_radius = 6378137  # meter

    px, py = map(math.radians, coordinate1)
    qx, qy = map(math.radians, coordinate2)

    term1 = (py - qy) * 0.5
    term2 = (px - qx) * 0.5
    term3 = math.sin(term1)**2 + math.cos(py) * math.cos(qy) * math.sin(term2)**2

    haversine_dist = 2 * earth_radius * math.asin(math.sqrt(term3))

    return scales.get(scale, haversine_dist)(haversine_dist)


def euclidean(coordinate1, coordinate2):
    # TODO doc
    pass


# Worker
def dispatch_name(val, key, idx):
    # TODO doc
    return {
        'merge_0': lambda: ('cover', '{}_{}.tif'.format(idx, key)),
        'merge_1': lambda: ('loss', '{}_{}.tif'.format(idx, key)),
        'merge_2': lambda: ('gain', '{}_{}.tif'.format(idx, key)),
        'merge_3': lambda: ('biomass', '{}_{}.tif'.format(idx, key)),
        'merge_4': lambda: ('confidence', '{}_{}.tif'.format(idx, key)),
        'reproject_0': lambda: ('gl30_10', '{}_{}.tif'.format(idx, key)),
        'reproject_1': lambda: ('gl30_00', '{}_{}.tif'.format(idx, key)),
        'reproject_2': lambda: ('soil', '{}_{}.tif'.format(idx, key)),
    }.get(val, None)()


def download_worker(url: str, to_path: str, **kwargs) -> None:
    # TODO doc
    content = download(url, **kwargs)

    if content is not None:
        write_binary(content, to_path)


def alignment_worker(to_reproject, to_crs, to_merge_alike, out_path, generic_name):
    # TODO doc
    template = None
    path = Path(out_path)

    for idx, raster in enumerate(to_reproject):
        out_path = str(path / 'reproject_{}_{}'.format(idx, generic_name))

        if idx == 0:
            try:
                template = reproject_from(raster, to_crs, out_path)
            except Exception as err:
                LOGGER.error('Fatal no template %s', raster, exc_info=err)
                raise err

        else:
            try:
                reproject_like(template, raster, out_path)
            except Exception as err:
                LOGGER.warning('Unable to reproject %s', raster, exc_info=err)

    kwargs = fetch_metadata(template, 'profile')

    for idx, rasters in enumerate(to_merge_alike):
        out_path = str(path / 'merge_{}_{}'.format(idx, generic_name))

        try:
            data, transform = merge_alike(template, rasters)
            kwargs.update({'transform': transform})
            write(data, out_path, **kwargs)

        except Exception as err:
            LOGGER.warning('Unable to merge %s, cant create %s', rasters, out_path)


def clip_worker(to_clip, bounds, profile, out_path):
    # TODO doc
    key = int_to_orient(bounds.left, bounds.top)
    path = Path(out_path)

    for idx, raster in enumerate(to_clip):
        data, transform = clip_raster(raster, bounds)
        opath = path / '{}_{}.tif'.format(idx, key)
        profile.update({'transform': transform})
        write(data, str(opath), **profile)


def harmonization_worker(gl30, cover, queue, *args):
    # TODO doc, refactor
    r1 = read_raster(gl30)
    r2 = read_raster(cover)

    d1 = r1.read(1)
    d2 = r2.read(1)

    r1.close()
    r2.close()

    d1[d1 == 20] = 1
    d1[d1 == 50] = 1
    d1[d1 != 1] = 0

    tmp = d2.copy()

    args = list(args)
    for i in [0, 10, 20, 30]:
        tmp[d2 <= i] = 0
        tmp[d2 > i] = 1

        args.append(binary_jaccard(d1, tmp))
        args.append(simple_matching_coefficient(d1, tmp))

    queue.put(args)
