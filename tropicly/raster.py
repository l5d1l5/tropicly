"""
raster.py

Author: Tobias Seydewitz
Date: 14.04.18
Mail: tobi.seyde@gmail.com
"""
import re
import numpy as np
from rasterio import open, band
from rasterio.merge import merge
from shapely.geometry import Polygon
from rasterio.io import DatasetReader
from tropicly.distance import Distance
from rasterio.mask import raster_geometry_mask, mask
from rasterio.coords import BoundingBox, disjoint_bounds
from rasterio.warp import reproject, calculate_default_transform


def make_warp_profile(template, crs):
    with open(template, 'r') as src:
        affine, width, height = calculate_default_transform(
            src_crs=src.crs,
            dst_crs=crs,
            width=src.width,
            height=src.height,
            **src.bounds._asdict(),
        )
        kwargs = src.profile.copy()

    kwargs.update(
        transform=affine,
        width=width,
        height=height,
        compress='lzw',
        crs=crs,
        res=(abs(affine[0]), abs(affine[4])),
        bounds=BoundingBox(affine.xoff, affine.yoff+(height*affine[4]),
                           affine.xoff+(width*affine[0]), affine.yoff)
    )

    return kwargs


def reproject_like(in_path, out_path, **kwargs):
    # TODO reproject should return dataset
    with open(in_path, 'r') as src:
        out_kwargs = src.profile.copy()
        out_kwargs.update({
            'crs': kwargs['crs'],
            'transform': kwargs['transform'],
            'width': kwargs['width'],
            'height': kwargs['height']
        })

        with open(out_path, 'w', **out_kwargs) as dst:
            reproject(source=band(src, list(range(1, src.count + 1))),
                      destination=band(dst, list(range(1, src.count + 1))))

    return out_path


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

    dst, affine = merge(readers, **kwargs)

    [reader.close() for reader in readers]

    return dst, affine


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
    if isinstance(item, DatasetReader):
        return item

    else:
        try:
            path = str(item)  # Cast pathlib.Path to string
            return open(path, 'r')

        except:
            msg = 'Attr {}, Type {} is not a valid raster file'.format(item, type(item))
            raise ValueError(msg)


def clip_raster(raster, dst_bounds):
    # TODO doc
    src = read_raster(raster)
    src_bounds = src.bounds

    if disjoint_bounds(src_bounds, dst_bounds):
        msg = 'Raster bounds {} are not covered by clipping bounds {}'.format(src_bounds, dst_bounds)
        raise ValueError(msg)

    window = src.window(*dst_bounds)
    window = window.round_lengths(op='ceil')
    transform = src.window_transform(window)
    data = src.read(window=window, out_shape=(src.count, window.height, window.width))

    src.close()
    return data, transform


def clip(clipper, geometries):
    """
    Clips a list of geometries to extent of a clipper geometry.
    Uses intersection to do so.

    :param clipper: shapely geometry
    :param geometries: list of shapely geometries
    :return: list of shapely geometries
    """
    for geo in geometries:
        yield clipper.intersection(geo)


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

    return Polygon(polygon_bounds)


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

    with open(to_path, 'w', **kwargs) as dst:
        for i in range(idx):
            dst.write(data[i], i + 1)  # rasterio band index start at one, thus we increment by one

    return to_path


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


def orient_to_int(orient):
    # TODO doc
    coor, orient = re.match(r'(?P<coor>\d+)(?P<orient>[NSWE])', orient, re.I).groups()

    if orient.lower() in ('n', 'e'):
        return int(coor)

    else:
        return -1 * int(coor)


def round_bounds(bounds):
    # TODO doc, round method ceil, floor
    attrs = ('left', 'bottom', 'right', 'top')

    coords = []
    for attr in attrs:
        coord = bounds.__getattribute__(attr)
        coords.append(round(coord))

    return BoundingBox(*coords)


# TODO refactor, generalize
def worker(img, polygon, func, records):
    dist = Distance('hav')

    with open(img, 'r') as src:
        ma, *_ = raster_geometry_mask(src, [polygon], crop=True)
        data, transform = mask(src, [polygon], crop=True, indexes=1)
        count = np.ma.masked_equal(ma, True).count()

        kwargs = {
            'img': data,
            'transform': transform,
            'count': count,
            'geometry': polygon,
            'distance': dist,
        }

        rec = func(**kwargs)

    if rec:
        records.append(rec)


# TODO refactor, generalize
def compute_cover(**kwargs):
    transform = kwargs['transform']
    cover = np.ma.masked_less(kwargs['img'], 11)

    x = kwargs['distance']((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = kwargs['distance']((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))

    feature = {
        'mean': cover.mean(),
        'covered': cover.count(),
        'count': kwargs['count'],
        'px_area': round(x*y),
        'geometry': kwargs['geometry'],
    }

    if feature['covered'] > 0:
        return feature


def compute_driver(**kwargs):
    transform = kwargs['transform']

    x = kwargs['distance']((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = kwargs['distance']((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))

    ids, counts = np.unique(kwargs['img'], return_counts=True)
    feature = {str(key): int(value) for key, value in zip(ids, counts) if key not in [0, 20, 255]}

    if not feature:
        return

    loss = sum(feature.values())

    feature.update({
        'loss': loss,
        'px_area': round(x*y),
        'geometry': kwargs['geometry'],
    })

    return feature


def compute_emissions(**kwargs):
    emissions = np.ma.masked_less_equal(kwargs['img'], 0)

    feature = {
        'emission_px': emissions.count(),
        'count': kwargs['count'],
        'total': emissions.sum(),
        'geometry': kwargs['geometry'],
    }

    if feature['emission_px'] > 0:
        return feature
