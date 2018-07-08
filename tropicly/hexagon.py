import numpy as np
from rasterio import open
from rasterio.windows import Window
from PIL import Image, ImageDraw
from math import tan, atan, pi
from shapely.geometry import Polygon
from shapely.affinity import translate
import geopandas as gpd


def hexagonal_mask(width, height):
    # TODO solve even odd issue
    angle = atan(height/width) - pi/12

    if angle <= 0:
        raise ValueError

    rx = width/2
    ry = height/2

    polygon = [
        (0, -rx*tan(pi+angle)+ry),
        (rx, 0),
        (2*rx, rx*tan(2*pi-angle)+ry),
        (2*rx, rx*tan(angle)+ry),
        (rx, 2*ry),
        (0, -rx*tan(pi-angle)+ry),
        (0, -rx*tan(pi+angle)+ry)
    ]

    return polygon


if __name__ == '__main__':
    poly = Polygon(hexagonal_mask(2, 2))
    poly2 = translate(poly, 2)
    poly3 = translate(poly, 1, -1.577350269189626)
    poly4 = translate(poly, 3, -1.577350269189626)
    geoseries = gpd.GeoSeries([poly, poly2, poly3, poly4])
    layer = gpd.GeoDataFrame(geometry=geoseries)
    layer.crs={'init':'epsg:4326'}
    layer.to_file('/home/ilex/Documents/hex.shp')