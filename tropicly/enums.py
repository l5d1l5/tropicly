"""
python.py

Author: Tobias Seydewitz
Date: 16.05.18
Mail: tobi.seyde@gmail.com
"""
from enum import Enum


class SOCClasses(Enum):
    """
    Soil organic carbon change classes. Don et al. (2010)
    """
    primary_forest = 0
    secondary_forest = 1
    grassland = 2
    perennial_crops = 3
    cropland = 4
    no_data = 5


class GL30Classes(Enum):
    """
    GlobLand30 land cover classes. Chen et al. (2015)
    """
    cropland = 10
    forest = 20
    regrowth = 25
    grassland = 30
    shrubland = 40
    wetland = 50
    water = 60
    tundra = 70
    artificial = 80
    bareland = 90
    snow = 100
    no_data = 255
