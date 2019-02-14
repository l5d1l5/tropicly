from tropicly.utils import get_data_dir, cache_directories
import pandas as pd
import geopandas as gpd


def to_area(row, unit=1000000, columns=('10', '20', '25', '30', '40', '50', '60', '80', '90')):
    area = row['area'] / unit
    columns = columns

    absolute = [
        round(row[idx] * area, 1)
        for idx in columns
    ]

    columns = ['region'] + list(columns)
    absolute = [row['region']] + absolute

    return pd.Series(data=absolute, index=columns)


def to_relative(row, columns=('10', '20', '25', '30', '40', '50', '60', '80', '90')):
    total = sum(
        [row[idx] for idx in columns]
    )

    if total != 0:
        for idx in columns:
            row[idx] = '{}({}\\%)'.format(row[idx], round((row[idx] / total)*100, 1))

    else:
        for idx in columns:
            row[idx] = '-'

    return row


def to_tex(df, path):
    lines = ['&'.join(df.columns.tolist()) + '\\\\']

    for idx, row in df.iterrows():
        lines.append('&'.join(map(str, row)) + '\\\\')

    with open(path, 'w') as dst:
        dst.write('\n'.join(lines))


DIRS = cache_directories(get_data_dir())

countries = gpd.read_file(DIRS.masks / 'earth.shp')
driver = pd.read_csv(DIRS.textual / 'driver.csv')

region = 'Australia'

country_selection = list(countries[countries.REGION == region].NAME)
selection = driver[driver['region'].isin(country_selection)]
selection = selection.sort_values(by=['region'])

selection = selection.apply(to_area, axis=1)

total = selection.sum()
total['region'] = region

selection = selection.append([total], ignore_index=True)

selection.to_csv(DIRS.textual / 'driver_{}.csv'.format(region), index=False)

selection = selection.apply(to_relative, axis=1)

to_tex(selection, '/home/tobi/Documents/{}.tex'.format(region))
