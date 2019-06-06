"""
emissions
*********

:Author: Tobias Seydewitz
:Date: 21.05.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import sys
from threading import Thread

import geopandas as gpd
import numpy as np
from rasterio import open

from distance import Distance
from factors import Coefficient
from raster import write
from settings import GL30Classes
from settings import SETTINGS
from settings import SOCCCoefficients
from settings import SOCClasses
from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress


def soc_emissions(driver, soc, intact=None, area=900, forest_type=SOCClasses.secondary_forest):
    ha_per_px = area * 0.0001

    # prevent zero overflow (soc raster contain pixel values 0.1e^-x and -3.e^x)
    soc[soc < 0] = 0

    factors = factor_map(driver, intact=intact, forest_type=forest_type)

    emissions = ha_per_px * soc * factors
    emissions = np.round(emissions, decimals=2)

    return emissions.astype(np.float32)


def factor_map(driver, intact=None, forest_type=SOCClasses.secondary_forest):
    factors = np.zeros([3]+list(driver.shape), dtype=np.float32)
    zero_factor = Coefficient('zero', 0, 0, 0, 0, 0)

    if intact is not None:
        primary_forest = np.copy(driver)

        primary_forest[intact == 0] = 0
        driver[intact == 1] = 0

        factors = factor_map(primary_forest, forest_type=SOCClasses.primary_forest)

    for idx, attr in enumerate(['min', 'mean', 'max']):

        for member in GL30Classes:
            if member == GL30Classes.zero:  # TODO(Hack) if zero is included it sets factors from primary_forest to zero
                continue

            factor = SOCCCoefficients.get((forest_type, member), zero_factor)
            factors[idx][driver == member.value] = factor.__getattribute__(attr)

    return factors


def soc_worker(driver, soc, intact, out_name, forest_type):
    """
    Worker function for parallel execution.

    :param driver: str
        Path to driver raster image.
    :param soc: str
        Path to soil organic carbon content image.
    :param out_name: str
        Out path of emission image.
    :param intact: str
        Path to intact forest raster image.
    :param kwargs:
        Parameters for soc_emissions function. Please,
        refer to the function thesis for a list of possible
        parameter.
    """
    with open(driver, 'r') as h1, open(soc, 'r') as h2:
        driver_data = h1.read(1)
        soc_data = h2.read(1)

        profile = h1.profile
        transform = h1.transform

    haversine = Distance('hav')
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)

    if intact:
        with open(intact, 'r') as h3:
            intact_data = h3.read(1)

        emissions = soc_emissions(driver_data, soc_data, intact=intact_data, area=area, forest_type=forest_type)

    else:
        emissions = soc_emissions(driver_data, soc_data, area=area, forest_type=forest_type)

    write(emissions, out_name, **profile)


def soc(dirs, sheduler, forest_type, include_ifl=False):
    aism = gpd.read_file(str(dirs.masks / 'aism.shp'))
    pdd = gpd.read_file(str(dirs.masks / 'driver.shp'))

    strata = aism.merge(pdd, on='key')

    for idx, row in strata.iterrows():
        soc = dirs.aism / row.soc
        driver = dirs.driver / row.driver
        intact = None
        out_name = dirs.soc_sc1 / 'soc_sc1_{}.tif'.format(row.key)

        if include_ifl:
            intact = dirs.aism / row.ifl
            out_name = dirs.soc_sc2 / 'soc_sc2_{}.tif'.format(row.key)

        sheduler.add_task(Thread(target=soc_worker, args=(driver, soc, intact, out_name, forest_type)))


def biomass_emissions(driver, biomass, area=900, deforestation=SETTINGS['deforestation']):
    """Computes the emissions by biomass removal.

    Args:
        driver (ndarray): Proximate Deforestation Driver stratum.
        biomass (ndarray): Above-ground Woody Biomass Density stratum.
        area (float, optional): The area a pixel covers on ground in square meter.
        deforestation (float, optional): Conversion factor for carbon to carbon-dioxide

    Returns:
        ndarray: The Carbon loss per pixel (Mg/pixel).
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

    elif operation == 'soc_sc1':
        soc(SETTINGS['data'], sheduler, SOCClasses.primary_forest, include_ifl=False)

    elif operation == 'soc_sc2':
        soc(SETTINGS['data'], sheduler, SOCClasses.secondary_forest, include_ifl=True)

    else:
        print('err')

    sheduler.quite()


if __name__ == '__main__':
    _, *args = sys.argv
    main(*args)
