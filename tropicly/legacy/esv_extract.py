import numpy as np
import geopandas as gpd
import rasterio as rio
from tropicly.utils import cache_directories, get_data_dir


DIRS = cache_directories(get_data_dir())

mask = gpd.read_file(DIRS.masks / 'aism_americas.shp')

esv = [0]*6
columns = ['co_loss', 'co_gain', 'gr_loss', 'gr_gain', 'wb_loss', 'wb_gain']

for _, row in mask.iterrows():

    for idx, key in enumerate(columns):
        with rio.open(DIRS.esv / row[key]) as src:
            data = src.read(1)

        esv[idx] += np.sum(data)


print('&'.join(columns))
print('&'.join(map(str, esv)))
