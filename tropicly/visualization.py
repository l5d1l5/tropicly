"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import fiona
from collections import OrderedDict
from shapely.affinity import scale
from shapely.geometry import asShape
from tropicly.grid import SegmentedHexagon


path = '/home/ilex/Dropbox/shp/cover_normalized_scaled_americas.shp'
vec = fiona.open(path)

schema = {'geometry': 'Polygon',
          'properties': OrderedDict([('class', 'str:10'), ('ratio', 'float:4.2'), ('id', 'int:10')])}

with fiona.open('/home/ilex/Documents/driver_normalized_scaled_americas.shp', 'w', schema=schema, driver=vec.driver, crs=vec.crs) as dst:
    for idx, feature in enumerate(vec):
        hexagon = SegmentedHexagon(asShape(feature['geometry']))
        properties = feature['properties']
        impact = properties['impact']

        ratios = []
        for driver in ['10', '25', '30', '40', '50', '60', '70', '80', '90', '100']:
            if driver in properties:
                if properties[driver] > 0:
                    ratio = round((properties[driver]/impact)*100)
                    if ratio > 10:
                        ratios.append([driver, ratio])

        ratios = sorted(ratios, key=lambda x: x[1], reverse=True)
        for driver, ratio in ratios:
            segment = hexagon.get_segment(ratio)
            feat = {'geometry': segment.__geo_interface__,
                    'properties': OrderedDict([('class', driver), ('ratio', ratio), ('id', idx)])}
            dst.write(feat)


# SCALE DRIVERS
# with fiona.open('/home/ilex/Documents/cover_normalized_scaled_americas.shp',
#                 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
#     for feature in vec:
#         scaling = feature['properties']['normalized']
#         feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling,
#                                     yfact=scaling).__geo_interface__
#         src.write(feature)

# CALCULATE DRIVERS SCALING
# with fiona.open('/home/ilex/Documents/driver_scaled_americas.shp', 'w', schema=schema, driver=vec.driver, crs=vec.crs) as dst:
#     for feature in vec:
#         properties = feature['properties']
#         impact = 0
#         for key in properties:
#             if key == 'covered':
#                 continue
#             properties[key] = int(properties[key])
#             impact += properties[key]
#         properties['impact'] = impact
#         ratio = impact / properties['covered']
#         linear = (ratio-0.000051)/(0.233429-0.000051)
#         normalized = ((1.0-0.6)/(0.233429-0.000051))*(ratio-0.233429)+1.0
#         properties['im/co'] = impact / properties['covered']
#         if ratio >= 0.2:
# properties['scaling'] = 1.0
# elif ratio >= 0.1:
# properties['scaling'] = 0.9
# else:
# properties['scaling'] = 0.8
# properties['linear'] = linear
# properties['normalized'] = normalized
# feature['properties'] = properties
# if impact > 0:
# dst.write(feature)

# CALCULATE COVER SCALING AND SCALE
# with fiona.open('/home/tobi/Documents/cover_scaled_asia.shp',
#                 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
#     for feature in vec:
#         if feature['properties']['covered'] != 0:
#             ratio = feature['properties']['covered'] / feature['properties']['count']
#             scaling = int(ratio * 10 + 1) / 10
#             feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling, yfact=scaling).__geo_interface__
#             src.write(feature)