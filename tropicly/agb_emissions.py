import numpy as np
from rasterio import open

from tropicly.distance import Distance
from tropicly.utils import write


def worker(pdd, agb, out_name, distance='hav'):
    """Worker function for parallel execution.

    Computes the Above-ground Biomass Emissions by using ``agb_emissions`` function.
    Further, the pixel resolution in square meter is computed and delegated to ``agb_emissions``.
    Result is stored on disk as raster image by using the metadata profile of the first argument.

    Args:
        pdd (str or Path): Path to Proximate Deforestation Driver tile.
        agb (str or Path): Path to Above-ground Biomass tile.
        out_name (str or Path): Path plus name of out file.
        distance (str, optional): Default is Haversine equation.
    """
    with open(pdd, 'r') as h1, open(agb, 'r') as h2:
        driver_data = h1.read(1)
        biomass_data = h2.read(1)

        profile = h1.profile
        transform = h1.transform

    haversine = Distance(distance)
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))
    area = round(x * y)

    emissions = agb_emissions(driver_data, biomass_data, area=area)

    # write updates the dtype corresponding to the array dtype
    write(emissions, out_name, **profile)


def agb_emissions(pdd, agb, area=900, co2=1, pdd_classes=(10, 25, 30, 40, 70, 80, 90)):
    """Computes the emissions trough Above-ground Biomass removal.

    Args:
        pdd (np.ndarray): Proximate Deforestation Driver raster image as 2D numpy array.
        agb (np.ndarray): Above-ground Biomass raster image as 2D numpy array.
        area (float, optional): The area a pixel covers on ground in square meter.
        co2 (float, optional): Conversion factor for carbon to carbon-dioxide
        pdd_classes (list, optional): PDD classes to consider as deforested.

    Returns:
        np.ndarray: The computed CO2 emissions per pixel.
    """
    ha_per_px = area * 0.0001

    mask = np.zeros(pdd.shape, dtype=np.uint8)
    mask[np.isin(pdd, pdd_classes)] = 1

    agb[agb < 0] = 0  # prevent negative values

    emissions = ha_per_px * co2 * mask * agb
    emissions = np.round(emissions, decimals=2)

    return emissions.astype(np.float32)
