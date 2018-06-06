"""
raster.py

Author: Tobias Seydewitz
Date: 14.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
import geopandas as gpd
from shapely.geometry import Polygon
from rasterio.features import rasterize
from tropicly.utils import write


def rasterize_vector(transform, bounds, shape, vector):
    """

    :param transform:
    :param bounds:
    :param vector:
    :return:
    """
    clipper = polygon_from(bounds)
    geometries = list(vector.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]].geometry)

    if geometries:
        clipped = clip(clipper, geometries)
        raster = rasterize(clipped, out_shape=shape, transform=transform, dtype=np.uint8)

        return raster

    return np.zeros(shape=shape, dtype=np.uint8)


def clip(clipper, geometries):
    """
    Clips a list of geometries to extent of a clipper geometry.
    Uses intersection to do so.

    :param clipper: shapely geometry
    :param geometries: list of shapely geometries
    :return: list of shapely geometries
    """
    return [clipper.intersection(geo) for geo in geometries]


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


if __name__ == '__main__':
    #mask = gpd.read_file('/home/tobi/Documents/Master/code/python/Master/data/auxiliary/masks/final_region_mask.shp')
    ifl = gpd.read_file('/home/tobi/Documents/Master/code/python/Master/data/core/ifl/ifl_tropic.shp')
    handle = rio.open('/home/tobi/Documents/Master/code/python/Master/data/driv/driver_10S_060W.tif')

    transform = handle.transform
    bounds = handle.bounds
    shape = handle.height, handle.width
    profile = handle.profile

    ra = rasterize_vector(transform, bounds, shape, ifl)
    print(np.unique(ra, return_counts=True))
    write(ra, '/home/tobi/Documents/clip.tif', **profile)
