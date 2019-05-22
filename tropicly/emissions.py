"""
Module: emissions.py
****

:Author: Tobias Seydewitz
:Date: 21.05.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
from threading import Thread

import geopandas as gpd
import numpy as np
from rasterio import open

from distance import Distance
from raster import write
from settings import SETTINGS
from sheduler import TaskSheduler, finish, progress
import sys


def biomass_emissions(driver, biomass, area=900, deforestation=SETTINGS['deforestation']):
    """Computes the emissions by biomass removal.

    Args:
        driver (ndarray): Proximate Deforestation Driver stratum.
        biomass (ndarray): Above-ground Woody Biomass Density stratum.
        area (float, optional): The area a pixel covers on ground in square meter.
        deforestation (float, optional): Conversion factor for carbon to carbon-dioxide

    Returns:
        ndarray: The Carbon loss per pixel.
    """
    ha_per_px = area * 0.0001

    mask = np.zeros(driver.shape, dtype=np.uint8)
    mask[np.isin(driver, deforestation)] = 1

    biomass[biomass < 0] = 0  # prevent negative values

    agb = ha_per_px * 0.5 * mask * biomass
    # Achard, F., Beuchle, R., Mayaux, P., Stibig, H.-J., Bodart, C., Brink, A., Simonetti, D. (2014).
    # Determination of tropical deforestation rates and related carbon losses from 1990 to 2010.
    # Global Change Biology, 20(8), 2540–2554. https://doi.org/10.1111/gcb.12605
    bgb = ha_per_px * 0.5 * mask * biomass**0.89

    carbon_emissions = np.round(agb + bgb, decimals=2)

    return carbon_emissions.astype(np.float32)


def biomass_worker(driver, biomass, out_name, distance='hav'):
    """Worker function for parallel execution.

    Computes the biomass emissions (AGB and BGB) by using ``biomass_emissions`` function.
    Further, the pixel resolution in square meter is computed and delegated to ``biomass_emissions``.
    Result is stored on disk as raster image by using the metadata profile of the first argument.

    Args:
        driver (str or Path): Path to Proximate Deforestation Driver tile.
        biomass (str or Path): Path to Above-ground Woody Biomass Density stratum.
        out_name (str or Path): Path plus name of out file.
        distance (str, optional): Default is Haversine equation.
    """
    with open(driver, 'r') as h1, open(biomass, 'r') as h2:
        driver_data = h1.read(1)
        biomass_data = h2.read(1)

        profile = h1.profile
        transform = h1.transform

    haversine = Distance(distance)
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)

    emissions = biomass_emissions(driver_data, biomass_data, area=area)

    # write updates the dtype corresponding to the array dtype
    write(emissions, out_name, **profile)


def biomass(dirs, sheduler):
    aism = gpd.read_file(str(dirs.masks / 'aism.shp'))
    pdd = gpd.read_file(str(dirs.masks / 'driver.shp'))

    strata = aism.merge(pdd, on='key')

    for idx, row in strata.iterrows():
        biomass = dirs.aism / row.biomass
        driver = dirs.driver / row.driver

        out_name = dirs.agbbgb / 'biomass_{}.tif'.format(row.key)

        sheduler.add_task(Thread(target=biomass_worker, args=(driver, biomass, out_name)))


def main(operation, threads):
    operation = operation.lower()

    sheduler = TaskSheduler('emissions', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    if operation == 'biomass':
        biomass(SETTINGS['data'], sheduler)

    elif operation == 'soc':
        pass

    else:
        print('err')

    sheduler.quite()


if __name__ == '__main__':
    _, *args = sys.argv
    main(*args)
