"""
esv.py

Author: Tobias Seydewitz
Date: 20.06.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
from tropicly.raster import write
from tropicly.enums import GL30Classes

from tropicly.enums import ESV_costanza, ESV_deGroot, ESV_worldbank
import geopandas as gpd
from tropicly.sheduler import TaskSheduler
from threading import Thread


def worker(driver, esv, names, **kwargs):
    with rio.open(driver, 'r') as src:
        profile = src.profile
        data = src.read(1)

    deficit = forest_deficit(data, esv, **kwargs)
    gain = landcover_gain(data, esv, **kwargs)

    write(deficit, names[0], **profile)
    write(gain, names[1], **profile)


def landcover_gain(driver, esv, attr='mean', gl30=(10, 25, 30, 40, 70, 80, 90)):
    mask = np.zeros(driver.shape, dtype=np.uint32)

    for i in gl30:
        coefficient = esv.get(GL30Classes(i)).__getattribute__(attr)
        mask[driver == i] = coefficient

    return mask


def forest_deficit(driver, esv, attr='mean', gl30=(10, 25, 30, 40, 70, 80, 90)):
    mask = np.zeros(driver.shape, dtype=np.uint32)
    mask[np.isin(driver, gl30)] = 1

    coefficient = esv.get(GL30Classes.forest).__getattribute__(attr)

    factor_map = mask * coefficient

    return factor_map


def progress(**kwargs):
    ratio = (kwargs['total'] - kwargs['pending']) / kwargs['total']
    ratio = round(ratio*100, 2)
    print('{} % of 100 %'.format(ratio))


if __name__ == '__main__':
    path = '/home/tobi/Documents/Master/code/python/Master/data/'
    out = path+'proc/esv/'

    sheduler = TaskSheduler('esv', 5)
    sheduler.on_progress.connect(progress)

    mask = gpd.read_file(path+'auxiliary/mask.shp')

    for idx, row in mask.iterrows():
        key = row.key
        driver = '{}proc/driver/{}'.format(path, row.driver)

        groot_names = [out+'groot_deficit_{}.tif'.format(key), out+'groot_gain_{}.tif'.format(key)]
        costa_names = [out+'costa_deficit_{}.tif'.format(key), out+'costa_gain_{}.tif'.format(key)]
        world_names = [out+'world_deficit_{}.tif'.format(key), out+'world_gain_{}.tif'.format(key)]

        sheduler.add_task(Thread(target=worker, args=(driver, ESV_deGroot, groot_names)))
        sheduler.add_task(Thread(target=worker, args=(driver, ESV_costanza, costa_names)))
        sheduler.add_task(Thread(target=worker, args=(driver, ESV_worldbank, world_names)))
