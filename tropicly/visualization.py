"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import fiona
from shapely.affinity import scale
from shapely.geometry import asShape

path = '/home/ilex/Documents/cover_americas.shp'
vec = fiona.open(path)

with fiona.open('/home/ilex/Documents/test.shp', 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
    for feature in vec:
        if feature['properties']['covered'] != 0:
            ratio = feature['properties']['covered'] / feature['properties']['count']
            scaling = int(ratio * 10 + 1) / 10
            feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling, yfact=scaling).__geo_interface__
            src.write(feature)