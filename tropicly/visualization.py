"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import rasterio as rio
import geopandas as gpd
from rasterio.windows import Window
from shapely.affinity import affine_transform, translate
from tropicly.grid import PolygonGrid, GridPolygon
from tropicly.frequency import frequency


# Prototype design
path = '/home/tobi/Documents/Master/code/python/Master/'

raster = rio.open(path+'tests/res/visual.tif')

bounds = raster.bounds
r_transform = ~raster.transform

grid = PolygonGrid(bounds, GridPolygon.rectangular(2, 2), fit=True)

for poly in grid:
    xoff, yoff = (poly.bounds[0], poly.bounds[3])*r_transform
    width, height = (poly.bounds[2], poly.bounds[1])*r_transform
    print(xoff, yoff)
    print(poly.bounds)
    print(width, height)
