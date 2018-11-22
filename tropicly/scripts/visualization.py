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
from collections import OrderedDict
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


def error_gen(actual, rounded):
    # refer to stack overflow
    divisor = sqrt(1.0 if actual < 1.0 else actual)
    return abs(rounded - actual) ** 2 / divisor


def round_to_100(percents):
    # refer to stack overflow
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


def visual_segmented(path, out, scaling=None):
    # id, class, ratio, loss, covered, px_area
    with fiona.open(path, 'r') as src:
        crs = src.crs
        records = []
        geometry = []

        for idx, feat in enumerate(src):
            prop, geo = feat['properties'], feat['geometry']

            poly = asShape(geo) if not scaling else scale(asShape(geo), xfact=scaling, yfact=scaling)
            poly = SegmentedHexagon(poly)

            # extract driver ratios (cls, ratio) and sort in decreasing order
            ratios = sorted(
                [
                    (str(cls), (prop[str(cls)]/prop['loss'])*100)
                    for cls in range(10, 105, 5) if str(cls) in prop
                ],
                key=lambda tup: tup[1],
                reverse=True
            )
            cls, ratios = list(zip(*ratios))
            ratios = list(zip(cls, round_to_100(ratios)))

            for cls, ratio in filter(lambda x: x[1] > 0, ratios):
                records.append(OrderedDict([
                    ('id', idx),
                    ('cls', cls),
                    ('loss', prop['loss']),
                    ('total', prop[str(cls)]),
                    ('covered', prop['covered']),
                    ('ratio', ratio),
                    ('px_area', prop['px_area'])
                ]))
                geometry.append(poly.get_segment(ratio))

        df = pd.DataFrame.from_records(records)
        gdf = gpd.GeoDataFrame(df, geometry=geometry)
        gdf.crs = crs
        gdf.to_file(out)


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


if __name__ == '__main__':
    # visual_segmented(
    #     '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/driver/americas_driver.shp',
    #     '/home/tobi/Documents/americas_driver_segmented.shp',
    #     0.8
    # )
    # visual_segmented(
    #     '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/vector/driver/africa_driver.shp',
    #     '/home/tobi/Documents/africa_driver_segmented.shp',
    #     0.8
    # )
    # visual_segmented(
    #      '/home/tobi/Documents/Master/code/python/susa/driver_peru_cleaned.shp',
    #      '/home/tobi/Documents/Master/code/python/susa/driver_peru_segmented.shp',
    #      0.8
    # )
    visual_treecover('/home/tobi/Documents/Master/code/python/susa/legend.shp',
                     '/home/tobi/Documents/Master/code/python/susa/legend_scaled.shp',
                     scaling='relative')
