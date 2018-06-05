"""
raster.py

Author: Tobias Seydewitz
Date: 14.04.18
Mail: tobi.seyde@gmail.com
"""
import shapely
import rasterio as rio
import geopandas as gpd
from rasterio import features


def ifl_rasterize():
    # TODO bounds of tile
    # TODO select in ifl vector polygons in bounds
    # TODO rasterize selected polygons with transform of tile
    pass


def clip():
    # TODO receive a
    pass


if __name__ == '__main__':
    mask = gpd.read_file('/home/tobi/Documents/Master/code/python/Master/data/auxiliary/masks/final_region_mask.shp')
    ifl = gpd.read_file('/home/tobi/Documents/Master/code/python/Master/data/core/ifl/ifl_tropic.shp')

    for idx, row in mask.iterrows():
        bounds = row.geometry.bounds
        interface = row.geometry.__geo_interface__
        print(bounds)
        print(interface)
