"""
agb_emissions.py

Author: Tobias Seydewitz
Date: 14.05.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
import rasterio as rio
from tropicly.utils import write
from tropicly.distance import Distance


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def worker(driver, biomass, filename):
    """
    Worker function for parallel execution.

    :param driver: str
        Path to deforestation driver image.
    :param biomass: str
        Path to above ground biomass image.
    :param filename: str
        Out path.
    """
    with rio.open(driver, 'r') as h1, rio.open(biomass, 'r') as h2:
        driver_data = h1.read(1)
        biomass_data = h2.read(1)

        profile = h1.profile
        transform = h1.transform

    haversine = Distance('hav')
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)

    emissions = agb_emissions(driver_data, biomass_data, area=area)

    write(emissions, filename, **profile)


def agb_emissions(driver, biomass, area=900, co2=3.7, gl30=(10, 25, 30, 40, 50, 60, 70, 80, 90, 100)):
    """
    Computes the emissions trough above ground biomass removals. Requires deforestation data
    per pixel and a equal shaped biomass per pixel map.

    :param driver: np.array
        A 2-dimensional numpy array.
    :param biomass: np.array
        A 2-dimensional numpy array.
    :param area: numeric
        Area in square meter.
    :param co2: numeric
        Carbon to carbon dioxide conversion factor.
    :param gl30: tuple of int
        GL30 classes to consider for emissions computation
    :return: np.array
        Above ground biomass emissions per pixel.
    """
    ha_per_px = area * 0.0001

    mask = np.zeros(driver.shape, dtype=np.uint8)
    mask[np.isin(driver, gl30)] = 1

    emissions = ha_per_px * co2 * mask * biomass
    emissions = np.round(emissions, decimals=2)

    return emissions.astype(np.float32)
