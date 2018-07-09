import numpy as np
import geopandas as gpd
from rasterio import open
from rasterio.windows import Window
from rasterio.coords import BoundingBox
from shapely.geometry import Polygon
from shapely.affinity import translate
from tropicly.raster import polygon_from


def y(start, end, step):
    start, end = 0, abs(start-end)
    scalar = 0

    while start <= end:
        yield scalar
        start += step
        scalar += step


def grid(bounds, size):
    grid = []
    polygon = polygon_from(BoundingBox(bounds.left, bounds.top-size, bounds.left+size, bounds.top))

    for i in y(bounds.top, bounds.bottom, size):
        for j in y(bounds.left, bounds.right, 2):
            grid.append(translate(polygon, xoff=j, yoff=-i))

    return grid

path = '/media/ilex/StorageOne/docs/code/python/projects/Master/data/proc/agg/cover_asia.tif'

with open(path) as src:
    print(src.bounds)
    geo = gpd.GeoSeries(grid(src.bounds, 2))
    layer = gpd.GeoDataFrame(geometry=geo)
    layer.crs = {'init':'epsg:4326'}
    layer.to_file('/home/ilex/Documents/test.shp')
    # data = src.read(1, window=Window(0, 0, col_n, row_n))
    # print(data.shape)
    # data = src.read(1, window=Window(col_n, 0, col_n, row_n))
    # print(data.shape)



