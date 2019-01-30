import numpy as np
from rasterio import open

from tropicly.distance import Distance
from tropicly.enums import GL30Classes
from tropicly.enums import SOCCCoefficients
from tropicly.enums import SOCClasses
from tropicly.factors import Coefficient
from tropicly.utils import write

# Inject alternatives SOCAlternativeFactors, SOCCFactors
SOCCFACTORS = SOCCCoefficients


# TODO doc


def worker(driver, soc, out_name, intact=None, **kwargs):
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

        emissions = soc_emissions(driver_data, soc_data, intact=intact_data, area=area, **kwargs)

    else:
        emissions = soc_emissions(driver_data, soc_data, area=area, **kwargs)

    write(emissions, out_name, **profile)


def soc_emissions(driver, soc, intact=None, method='mean', area=900, co2=3.7,
                  forest_type=SOCClasses.secondary_forest):
    ha_per_px = area * 0.0001
    # prevent zero overflow (soc raster contain pixel values 0.1e^-x and -3.e^x)
    soc[soc < 0] = 0

    factors = factor_map(driver, intact=intact, attr=method, forest_type=forest_type)

    emissions = ha_per_px * co2 * soc * factors
    emissions = np.round(emissions, decimals=2)

    return emissions.astype(np.float32)


def factor_map(driver, intact=None, attr='mean', forest_type=SOCClasses.secondary_forest):
    factors = np.zeros(driver.shape, dtype=np.float32)
    zero_factor = Coefficient('zero', 0, 0)

    if intact is not None:
        primary_forest = np.copy(driver)

        primary_forest[intact == 0] = 0
        driver[intact == 1] = 0

        factors = factor_map(primary_forest, attr=attr, forest_type=SOCClasses.primary_forest)

    for member in GL30Classes:
        factor = SOCCFACTORS.get((forest_type, member), zero_factor)
        factors[driver == member.value] = factor.__getattribute__(attr)

    return factors
