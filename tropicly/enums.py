"""
python.py

Author: Tobias Seydewitz
Date: 16.05.18
Mail: tobi.seyde@gmail.com
"""
from enum import Enum
from tropicly.factors import Coefficient


class SOCClasses(Enum):
    """
    Soil organic carbon change classes. Don et al. (2011)
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


# Full depth soil organic carbon change factors
# Don et al. (2011) Impact of tropical land-use change on soil organic
# carbon stocks - a meta-analysis, Global Change Biology
SOCC_data = [
    Coefficient((SOCClasses.primary_forest, SOCClasses.grassland), .121, .023),
    Coefficient((SOCClasses.primary_forest, SOCClasses.cropland), .252, .033),
    Coefficient((SOCClasses.primary_forest, SOCClasses.perennial_crops), .303, .027),
    Coefficient((SOCClasses.primary_forest, SOCClasses.secondary_forest), .086, .02),
    Coefficient((SOCClasses.secondary_forest, SOCClasses.grassland), .064, .025),
    Coefficient((SOCClasses.secondary_forest, SOCClasses.cropland), .213, .041),
    Coefficient((SOCClasses.secondary_forest, SOCClasses.perennial_crops), .024, .042),
]

SOCCFactors = {
    (SOCClasses.primary_forest, GL30Classes.cropland): SOCC_data[1],
    (SOCClasses.primary_forest, GL30Classes.regrowth): SOCC_data[3],
    (SOCClasses.primary_forest, GL30Classes.grassland): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.shrubland): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.tundra): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.bareland): SOCC_data[0],
    (SOCClasses.secondary_forest, GL30Classes.cropland): SOCC_data[-2],
    (SOCClasses.secondary_forest, GL30Classes.grassland): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.shrubland): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.tundra): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.bareland): SOCC_data[-3],
}

SOCCAlternativeFactors = {
    (SOCClasses.primary_forest, GL30Classes.cropland): SOCC_data[1],
    (SOCClasses.primary_forest, GL30Classes.regrowth): SOCC_data[3],
    (SOCClasses.primary_forest, GL30Classes.grassland): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.shrubland): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.tundra): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.bareland): SOCC_data[0],
    (SOCClasses.primary_forest, GL30Classes.artificial): SOCC_data[1],
    (SOCClasses.secondary_forest, GL30Classes.cropland): SOCC_data[-2],
    (SOCClasses.secondary_forest, GL30Classes.regrowth): SOCC_data[3],
    (SOCClasses.secondary_forest, GL30Classes.grassland): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.shrubland): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.tundra): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.bareland): SOCC_data[-3],
    (SOCClasses.secondary_forest, GL30Classes.artificial): SOCC_data[1],
}

ESV_costanza = {}
ESV_deGroot = {}
ESV_worldbank = {}
