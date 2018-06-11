"""
soc_emissions.py

Author: Tobias Seydewitz
Date: 14.05.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
from rasterio import open
from tropicly.utils import write
from tropicly.distance import Distance
from tropicly.factors import SOCCFactors, SOCCFactor
from tropicly.enums import SOCClasses, GL30Classes


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


# TODO intact convert to raster

def worker(driver, soc, out_name, intact=None, method='mean'):
    """
    Worker function for parallel execution.

    :param driver: str
        Path to driver raster image.
    :param soc: str
        Path to soil organic carbon content image.
    :param out_name: str
        Out path of emission image
    :param intact: optional, str
        Mask for intact primary forest.
    :param method: str, min, mean or max
        Method to compute soil organic carbon emissions.
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

    emissions = soc_emissions(driver_data, soc_data, intact=intact, method=method, area=area)

    write(emissions, out_name, **profile)


def soc_emissions(driver, soc, intact=None, method='mean', area=900, co2=3.7):
    """
    Des

    :param driver: np.array

    :param soc: np.array
    :param intact: np.array
    :param method: str
    :param area: numeric
    :param co2: numeric
    :return: np.array
    """
    ha_per_px = area * 0.0001
    # prevent overflow
    soc[soc < 0] = 0

    factors = factor_map(driver, intact=intact, attr=method)

    emissions = ha_per_px * co2 * soc * factors
    emissions = np.round(emissions, decimals=2)

    return emissions.astype(np.float32)


def factor_map(driver, intact=None, attr='mean', forest_type=SOCClasses.secondary_forest):
    """

    :param driver: np.array
    :param intact: np.array
    :param attr: str
    :param forest_type: enum.member
    :return: np.array
    """
    factors = np.zeros(driver.shape, dtype=np.float32)
    zero_factor = SOCCFactor('zero', 0, 0)

    if intact is not None:
        primary_forest = np.copy(driver)

        primary_forest[intact == 0] = 0
        driver[intact == 1] = 0

        factors = factor_map(primary_forest, attr=attr, forest_type=SOCClasses.primary_forest)

    for member in GL30Classes:
        factor = SOCCFactors.get((forest_type, member), zero_factor)
        factors[driver == member.value] = factor.__getattribute__(attr)

    return factors
