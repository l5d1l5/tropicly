"""
raster.py

Author: Tobias Seydewitz
Date: 14.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from rasterio import open, band
from rasterio.merge import merge
from shapely.geometry import Polygon
from rasterio.io import DatasetReader
from rasterio.warp import reproject, calculate_default_transform


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
    with open(in_path, 'r') as src:
        affine, width, height = calculate_default_transform(
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

        with open(out_path, 'w', **kwargs) as dst:
            for idx in src.indexes:
                reproject(
                    source=band(src, idx),
                    destination=band(dst, idx)
                )

        return out_path


def reproject_like(in_path, out_path, **kwargs):
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
