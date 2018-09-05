"""
percentile_filter.py

Author: Tobias Seydewitz
Date: 04.09.18
Mail: tobi.seyde@gmail.com
"""
import fiona
import numpy as np
from math import log10


path = '/home/tobi/Documents/Master/code/python/Master/data/proc/agg/shp/driver_africa.shp'
vec = fiona.open(path)

impact = []
for feature in vec:
    impact.append(log10(feature['properties']['impact']))

impact = np.array(impact)
q25, q75 = np.percentile(impact, (25, 75))
iqr = q75 - q25

lower = q25 - iqr
upper = q75 + iqr

with fiona.open('/home/tobi/Documents/driver_africa_filtered.shp', 'w',
                driver=vec.driver, crs=vec.crs, schema=vec.schema) as dst:
    for feat, lg in zip(vec, impact):
        if lower <= lg <= upper:
            dst.write(feat)
