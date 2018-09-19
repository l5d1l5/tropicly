"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import fiona
import pandas as pd
import geopandas as gpd
from bisect import bisect_left
from math import sqrt, isclose
from shapely.affinity import scale
from shapely.geometry import asShape
from tropicly.grid import SegmentedHexagon


def visual_treecover(path, out, bins=None, unit=1000000, scaling='relative'):
    properties = []
    geometries = []
    scaled_geometries = []
    max_count = 0

    if not bins:
        bins = [i/10 for i in range(1, 11)]

    with fiona.open(path, 'r') as src:
        crs = src.crs

        for feat in src:
            prop, geo = feat['properties'], feat['geometry']

            if prop['count'] > max_count:
                max_count = prop['count']

            geometries.append(geo)
            properties.append(prop)

    for prop, geo in zip(properties, geometries):
        area = (prop['covered'] * prop['px_area']) / unit

        if scaling == 'relative':
            ratio = prop['covered'] / max_count
        else:
            ratio = area / ((max_count * prop['px_area']) / unit)

        factor = bins[bisect_left(bins, ratio)]
        poly = scale(asShape(geo), xfact=factor, yfact=factor)

        prop['area'] = area
        prop['ratio'] = ratio
        prop['scaling'] = factor

        scaled_geometries.append(poly)

    df = pd.DataFrame(properties)
    gdf = gpd.GeoDataFrame(df, geometry=scaled_geometries)
    gdf.crs = crs
    gdf.to_file(out)



# REFACTOR THIS SHIT TO REUSEABLE FUNCTIONS


# path = '/home/tobi/Documents/driver_africa_filtered.shp'
# path = '/home/tobi/Documents/driver_filtered_africa.shp'
# path = '/home/tobi/Documents/driver_normalized_scaled_filtered_africa.shp'
# vec = fiona.open(path)

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
# with fiona.open('/home/tobi/Documents/driver_filtered_africa.shp', 'w', schema=schema, driver=vec.driver,
#                 crs=vec.crs) as dst:
#     for feature in vec:
#         properties = feature['properties']
#         impact = 0
#
#         for key in properties:
#             if key in ['10', '25', '30', '40', '50', '60', '70', '80', '90', '100']:
#                 properties[key] = int(properties[key])
#                 impact += properties[key]
#
#         properties['impact'] = impact
#
#         ratio = impact / properties['covered']
#         linear = (ratio - .00018060) / (.11331036 - .00018060)
#         normalized = ((1. - .5) / (.11331036 - .00018060)) * (ratio - .11331036) + 1.
#         normalized = (int(normalized * 10) + 1) / 10
#
#         if normalized > 1.0:
#             normalized = 1.0
#
#         properties['im/co'] = impact / properties['covered']
#         properties['linear'] = linear
#         properties['normalized'] = normalized
#         feature['properties'] = properties
#
#         if impact > 0:
#             dst.write(feature)


# # SCALE DRIVERS
# with fiona.open('/home/tobi/Documents/driver_normalized_scaled_filtered_africa.shp',
#                 'w', driver=vec.driver, schema=vec.schema, crs=vec.crs) as src:
#     for feature in vec:
#         scaling = feature['properties']['normalized']
#         feature['geometry'] = scale(asShape(feature['geometry']), xfact=scaling,
#                                     yfact=scaling).__geo_interface__
#         src.write(feature)


# # CALCULATE DRIVER HEXAGON SEGMENTS
# def error_gen(actual, rounded):
#     divisor = sqrt(1.0 if actual < 1.0 else actual)
#     return abs(rounded - actual) ** 2 / divisor
#
#
# def round_to_100(percents):
#     if not isclose(sum(percents), 100):
#         raise ValueError
#
#     rounded = [int(val) for val in percents]
#     up_count = 100 - sum(rounded)
#
#     errors = [
#         (error_gen(per, rnd + 1) - error_gen(per, rnd), idx)
#         for idx, (per, rnd) in enumerate(zip(percents, rounded))
#     ]
#
#     rank = sorted(errors)
#
#     for i in range(up_count):
#         rounded[rank[i][1]] += 1
#
#     return rounded
#
#
# schema = {
#     'geometry': 'Polygon',
#     'properties': OrderedDict([
#         ('id', 'int:10'),
#         ('class', 'str:10'),
#         ('ratio', 'int:10'),
#         ('covered', 'int:10'),
#         ('impact', 'int:10'),
#         ('im/co', 'float:10.8')
#     ])
# }
#
# with fiona.open('/home/tobi/Documents/driver_normalized_scaled_ratio_filtered_africa.shp', 'w', schema=schema,
#                 driver=vec.driver, crs=vec.crs) as dst:
#     for idx, feature in enumerate(vec):
#         hexagon = SegmentedHexagon(asShape(feature['geometry']))
#         properties = feature['properties']
#         impact = properties['impact']
#
#         ratios = []
#         for driver in ['10', '25', '30', '40', '50', '60', '70', '80', '90', '100']:
#             if driver in properties:
#                 if properties[driver] > 0:
#                     ratio = (properties[driver]/impact)*100
#                     ratios.append([driver, ratio])
#
#         driv, rat = list(zip(*ratios))
#         rat = round_to_100(rat)
#         ratios = sorted(zip(driv, rat), key=lambda x: x[1], reverse=True)
#         for driver, ratio in filter(lambda x: x[1] > 0, ratios):
#             segment = hexagon.get_segment(ratio)
#             feat = {
#                 'geometry': segment.__geo_interface__,
#                 'properties': OrderedDict([
#                     ('id', idx),
#                     ('class', driver),
#                     ('ratio', ratio),
#                     ('covered', properties['covered']),
#                     ('impact', properties['impact']),
#                     ('im/co', properties['im/co'])
#                 ])
#             }
#             dst.write(feat)


if __name__ == '__main__':
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/americas_cover.shp',
        '/home/tobi/Documents/americas_cover_absolute_scaled_10bins.shp',
        scaling='absolute'
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/africa_cover.shp',
        '/home/tobi/Documents/africa_cover_absolute_scaled_10bins.shp',
        scaling='absolute'
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/asia_cover.shp',
        '/home/tobi/Documents/asia_cover_absolute_scaled_10bins.shp',
        scaling='absolute'
    )

    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/americas_cover.shp',
        '/home/tobi/Documents/americas_cover_absolute_scaled_5bins.shp',
        scaling='absolute',
        bins=[.2, .4, .6, .8, 1.]
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/africa_cover.shp',
        '/home/tobi/Documents/africa_cover_absolute_scaled_10bins.shp',
        scaling='absolute',
        bins=[.2, .4, .6, .8, 1.]
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/asia_cover.shp',
        '/home/tobi/Documents/asia_cover_absolute_scaled_5bins.shp',
        scaling='absolute',
        bins=[.2, .4, .6, .8, 1.]
    )

    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/americas_cover.shp',
        '/home/tobi/Documents/americas_cover_relative_scaled_10bins.shp',
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/africa_cover.shp',
        '/home/tobi/Documents/africa_cover_relative_scaled_10bins.shp',
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/asia_cover.shp',
        '/home/tobi/Documents/asia_cover_relative_scaled_10bins.shp',
    )

    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/americas_cover.shp',
        '/home/tobi/Documents/americas_cover_relative_scaled_5bins.shp',
        bins=[.2, .4, .6, .8, 1.]
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/africa_cover.shp',
        '/home/tobi/Documents/africa_cover_relative_scaled_5bins.shp',
        bins=[.2, .4, .6, .8, 1.]
    )
    visual_treecover(
        '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/treecover/asia_cover.shp',
        '/home/tobi/Documents/asia_cover_relative_scaled_5bins.shp',
        bins=[.2, .4, .6, .8, 1.]
    )