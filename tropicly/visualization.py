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
from math import sqrt, isclose


path = '/home/tobi/Documents/driver_normalized_scaled_asia.shp'
vec = fiona.open(path)

# # CALCULATE DRIVERS SCALING
# schema = vec.schema
# schema['properties']['impact'] = 'int:10'
# schema['properties']['im/co'] = 'float:10.8'
# schema['properties']['linear'] = 'float:10.8'
# schema['properties']['normalized'] = 'float:10.8'
#
# for key in schema['properties']:
#     if key in ['10', '25', '30', '40', '50', '60', '70', '80', '90', '100']:
#         schema['properties'][key] = 'int:10'
#
# with fiona.open('/home/tobi/Documents/driverr_asia.shp', 'w', schema=schema, driver=vec.driver,
#                 crs=vec.crs) as dst:
#     for feature in vec:
#         properties = feature['properties']
#         impact = 0
#
#         for key in properties:
#             if key == 'covered':
#                 continue
#             properties[key] = int(properties[key])
#             impact += properties[key]
#
#         properties['impact'] = impact
#
#         ratio = impact / properties['covered']
#         linear = (ratio - .00005036) / (.25007996 - .00005036)
#         normalized = ((1. - .6) / (.25007996 - .00005036)) * (ratio - .25007996) + 1.
#
#         properties['im/co'] = impact / properties['covered']
#         properties['linear'] = linear
#         properties['normalized'] = normalized
#         feature['properties'] = properties
#
#         if impact > 0:
#             dst.write(feature)


# # SCALE DRIVERS
# with fiona.open('/home/tobi/Documents/driver_normalized_scaled_asia.shp',
#                 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
#     for feature in vec:
#         scaling = feature['properties']['normalized']
#         feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling,
#                                     yfact=scaling).__geo_interface__
#         src.write(feature)


# CALCULATE DRIVER HEXAGON SEGMENTS
def error_gen(actual, rounded):
    divisor = sqrt(1.0 if actual < 1.0 else actual)
    return abs(rounded - actual) ** 2 / divisor


def round_to_100(percents):
    if not isclose(sum(percents), 100):
        raise ValueError

    rounded = [int(val) for val in percents]
    up_count = 100 - sum(rounded)

    errors = [
        (error_gen(per, rnd + 1) - error_gen(per, rnd), idx)
        for idx, (per, rnd) in enumerate(zip(percents, rounded))
    ]

    rank = sorted(errors)

    for i in range(up_count):
        rounded[rank[i][1]] += 1

    return rounded


schema = {
    'geometry': 'Polygon',
    'properties': OrderedDict([
        ('id', 'int:10'),
        ('class', 'str:10'),
        ('ratio', 'int:10'),
        ('covered', 'int:10'),
        ('impact', 'int:10'),
        ('im/co', 'float:10.8')
    ])
}

with fiona.open('/home/tobi/Documents/driver_normalized_scaled_ratio_asia.shp', 'w', schema=schema, driver=vec.driver, crs=vec.crs) as dst:
    for idx, feature in enumerate(vec):
        hexagon = SegmentedHexagon(asShape(feature['geometry']))
        properties = feature['properties']
        impact = properties['impact']

        ratios = []
        for driver in ['10', '25', '30', '40', '50', '60', '70', '80', '90', '100']:
            if driver in properties:
                if properties[driver] > 0:
                    ratio = (properties[driver]/impact)*100
                    ratios.append([driver, ratio])

        driv, rat = list(zip(*ratios))
        rat = round_to_100(rat)
        ratios = sorted(zip(driv, rat), key=lambda x: x[1], reverse=True)
        for driver, ratio in filter(lambda x: x[1] > 0, ratios):
            segment = hexagon.get_segment(ratio)
            feat = {
                'geometry': segment.__geo_interface__,
                'properties': OrderedDict([
                    ('id', idx),
                    ('class', driver),
                    ('ratio', ratio),
                    ('covered', properties['covered']),
                    ('impact', properties['impact']),
                    ('im/co', properties['im/co'])
                ])
            }
            dst.write(feat)


# CALCULATE COVER SCALING AND SCALE
# with fiona.open('/home/tobi/Documents/cover_scaled_asia.shp',
#                 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
#     for feature in vec:
#         if feature['properties']['covered'] != 0:
#             ratio = feature['properties']['covered'] / feature['properties']['count']
#             scaling = int(ratio * 10 + 1) / 10
#             feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling, yfact=scaling).__geo_interface__
#             src.write(feature)