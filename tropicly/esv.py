"""
esv.py

Author: Tobias Seydewitz
Date: 20.06.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
import pandas as pd
from tropicly.raster import write
from tropicly.enums import GL30Classes


def worker(driver, esv, names, **kwargs):
    with rio.open(driver, 'r') as src:
        profile = src.profile
        data = src.read(1)

    deficit = forest_loss(data, esv, **kwargs)
    gain = landcover_gain(data, esv, **kwargs)

    write(deficit, names[0], **profile)
    write(gain, names[1], **profile)


def landcover_gain(data, esv, attr='mean', gl30=(10, 25, 30, 40, 70, 80, 90)):
    if isinstance(data, np.ndarray):
        return landcover_gain_from_map(data, esv, attr=attr, gl30=gl30)

    else:
        return landcover_gain_from_frame(data, esv, attr=attr, gl30=gl30)


def forest_loss(data, esv, attr='mean', gl30=(10, 25, 30, 40, 70, 80, 90)):
    if isinstance(data, np.ndarray):
        return forest_loss_from_map(data, esv, attr=attr, gl30=gl30)

    else:
        return forest_loss_from_frame(data, esv, attr=attr, gl30=gl30)


def landcover_gain_from_map(driver, esv, attr=None, gl30=None):
    mask = np.zeros(driver.shape, dtype=np.uint32)

    for i in gl30:
        coefficient = esv.get(GL30Classes(i)).__getattribute__(attr)
        mask[driver == i] = coefficient

    return mask


def forest_loss_from_map(driver, esv, attr=None, gl30=None):
    mask = np.zeros(driver.shape, dtype=np.uint32)
    mask[np.isin(driver, gl30)] = 1

    coefficient = esv.get(GL30Classes.forest).__getattribute__(attr)

    factor_map = mask * coefficient

    return factor_map


def forest_loss_from_frame(row, esv, attr=None, gl30=None):
    columns = []
    values = []
    count = 0

    for i in gl30:
        if str(i) in row:
            columns.append(esv['name']+'_l_'+str(i))
            values.append(row[str(i)] * esv.get(GL30Classes.forest).__getattribute__(attr))

            count += row[str(i)]

    columns.append(esv['name']+'_l_tot')
    values.append(count * esv.get(GL30Classes.forest).__getattribute__(attr))

    return pd.Series(data=values, index=columns)


def landcover_gain_from_frame(row, esv, attr=None, gl30=None):
    columns = []
    values = []
    total = 0

    for i in gl30:
        if str(i) in row:
            gain = row[str(i)] * esv.get(GL30Classes(i)).__getattribute__(attr)
            total += gain

            columns.append(esv['name']+'_g_'+str(i))
            values.append(gain)

    columns.append(esv['name']+'_g_tot')
    values.append(total)

    return pd.Series(data=values, index=columns)
