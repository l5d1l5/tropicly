import pandas as pd
import geopandas as gpd


def driver(row):
    columns = []
    values = []
    area = row['px_area']

    for i in [10, 25, 30, 40, 50, 60, 70, 80, 90, 100, 'loss']:
        if str(i) in row:
            class_area = (row[str(i)] * area) / 1000000
            columns.append(str(i))
            columns.append(str(i)+'_area')
            values.append(row[str(i)])
            values.append(class_area)

    return pd.Series(data=values, index=columns)


vec = gpd.read_file('')
vec.drop(labels=['geometry'], axis=1, inplace=True)

agg = vec.apply(driver, axis=1)
agg = agg.apply(sum, axis=0)