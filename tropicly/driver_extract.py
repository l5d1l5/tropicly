import rasterio as rio
import pandas as pd
from tropicly.frequency import frequency
from tropicly.distance import Distance
from tropicly.utils import get_data_dir, cache_directories
import re
import os
import gc


DIRS = cache_directories(get_data_dir())
haversine = Distance('hav')

names = [
    (re.match(r'driver_(.+)\.tif', name).group(1), name)
    for name in os.listdir(str(DIRS.driver))
    if not (re.match(r'driver_\d{2}[NS]_\d{3}[WE]\.tif', name)
            or re.match(r'driver_(americas|asia|africa)\.tif', name))
]

driver_countries = {
    re.sub(r'_', ' ', values[0]).title(): DIRS.driver / values[1]
    for values in names
}

total = len(driver_countries)
records = []
for idx, items in enumerate(driver_countries.items()):
    key, value = items

    with rio.open(value, 'r') as src:
        data = src.read(1)

        try:
            pdd = frequency(data)

        except:
            print('Error on: ', key)
            continue

        finally:
            del data
            gc.collect()

        transform = src.profile['transform']

        x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
        y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
        area = round(x * y)

    pdd['region'] = key
    pdd['area'] = area

    records.append(pdd)

    print('{} % finished: {}'.format(((idx+1) / total)*100, key))

df = pd.DataFrame.from_records(records)
df.to_csv(DIRS.driver / 'driver.csv', index=False)
