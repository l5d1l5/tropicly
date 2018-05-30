"""
soc_emissions.py

Author: Tobias Seydewitz
Date: 14.05.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
import rasterio as rio
from tropicly.utils import write
from tropicly.distance import Distance
from tropicly.factors import SOCCFactors, SOCCFactor
from tropicly.enums import SOCClasses, GL30Classes


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


# TODO intact convert to raster

def worker(driver, soc):
    with rio.open(driver, 'r') as h1, rio.open(soc, 'r') as h2:
        driver_data = h1.read(1)
        soc_data = h2.read(1)

        profile = driver.profile
        transform = driver.transform

    haversine = Distance('hav')
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)


def factor_map(driver, intact=None, attr='mean', forest_type=SOCClasses.secondary_forest):
    factors = np.zeros(driver.shape, dtype=np.float32)
    zero_factor = SOCCFactor('zero', 0, 0)

    if intact:
        pass

    for member in GL30Classes:
        factor = SOCCFactors.get((forest_type, member), zero_factor)
        factors[driver == member.value] = factor.__getattribute__(attr)

    return factors


if __name__ == '__main__':
    intact = np.random.randint(0,2, size=(10,10))
    driver = np.random.choice([i * 10 for i in range(11)], size=(10,10))
    print(driver)
    print(intact)
    print(factor_map(driver, intact))