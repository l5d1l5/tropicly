import numpy as np
import pandas as pd
import rasterio as rio

from legacy.enums import GL30Classes
from tropicly.raster import write
from distance import Distance


# TODO doc


def worker(driver, esv, names, attr='mean', distance='hav', gl30=(10, 25, 30, 40, 70, 80, 90)):
    with rio.open(driver, 'r') as src:
        profile = src.profile
        data = src.read(1)

    transform = profile['transform']

    haversine = Distance(distance)
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)

    deficit = forest_loss(data, esv, attr=attr, area=area, gl30=gl30)
    gain = landcover_gain(data, esv, attr=attr, area=area, gl30=gl30)

    write(deficit, names[0], **profile)
    write(gain, names[1], **profile)


def landcover_gain(data, esv, attr='mean', area=900, gl30=(10, 25, 30, 40, 70, 80, 90)):
    ha_per_pixel = area * 0.0001

    if isinstance(data, np.ndarray):
        return landcover_gain_from_map(data, esv, attr=attr, area=ha_per_pixel, gl30=gl30)

    else:
        return landcover_gain_from_frame(data, esv, attr=attr, area=ha_per_pixel, gl30=gl30)


def forest_loss(data, esv, attr='mean', area=900, gl30=(10, 25, 30, 40, 70, 80, 90)):
    ha_per_pixel = area * 0.0001

    if isinstance(data, np.ndarray):
        return forest_loss_from_map(data, esv, attr=attr, area=ha_per_pixel, gl30=gl30)

    else:
        return forest_loss_from_frame(data, esv, attr=attr, area=ha_per_pixel, gl30=gl30)


# TODO refactor include area
def landcover_gain_from_map(driver, esv, attr=None, area=None, gl30=None):
    mask = np.zeros(driver.shape, dtype=np.float64)

    for i in gl30:
        coefficient = esv.get(GL30Classes(i)).__getattribute__(attr)
        mask[driver == i] = coefficient * area

    return mask


# TODO refactor include area
def forest_loss_from_map(driver, esv, attr=None, area=None, gl30=None):
    mask = np.zeros(driver.shape, dtype=np.uint8)
    mask[np.isin(driver, gl30)] = 1

    coefficient = esv.get(GL30Classes.forest).__getattribute__(attr)

    factor_map = mask * coefficient * area

    return factor_map


def forest_loss_from_frame(row, esv, attr=None, area=None, gl30=None):
    columns = []
    values = []
    total = 0

    if 'px_area' in row:
        area = row['px_area'] * 0.0001

    for i in gl30:
        if str(i) in row:
            loss = round(row[str(i)] * area * esv.get(GL30Classes.forest).__getattribute__(attr))
            total += loss

            columns.append(esv['name']+'_l_'+str(i))
            values.append(loss)

    columns.append(esv['name']+'_l_tot')
    values.append(total)

    return pd.Series(data=values, index=columns)


def landcover_gain_from_frame(row, esv, attr=None, area=None, gl30=None):
    columns = []
    values = []
    total = 0

    if 'px_area' in row:
        area = row['px_area'] * 0.0001

    for i in gl30:
        if str(i) in row:
            gain = round(row[str(i)] * area * esv.get(GL30Classes(i)).__getattribute__(attr))
            total += gain

            columns.append(esv['name']+'_g_'+str(i))
            values.append(gain)

    columns.append(esv['name']+'_g_tot')
    values.append(total)

    return pd.Series(data=values, index=columns)