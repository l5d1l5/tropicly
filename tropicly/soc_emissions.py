"""
soc_emissions.py

Author: Tobias Seydewitz
Date: 14.05.18
Mail: tobi.seyde@gmail.com
"""
from tropicly.enums import SOCClasses
from tropicly.factors import Factors


# Full depth soil organic carbon change factors
# Don et al. (2011) Impact of tropical land-use change on soil organic
# carbon stocks - a meta-analysis, Global Change Biology
SOCC_data = [
    ((SOCClasses.primary_forest, SOCClasses.grassland), .121, .023),
    ((SOCClasses.primary_forest, SOCClasses.cropland), .252, .033),
    ((SOCClasses.primary_forest, SOCClasses.perennial_crops), .303, .027),
    ((SOCClasses.primary_forest, SOCClasses.secondary_forest), .086, .02),
    ((SOCClasses.secondary_forest, SOCClasses.grassland), .064, .025),
    ((SOCClasses.secondary_forest, SOCClasses.cropland), .213, .041),
    ((SOCClasses.secondary_forest, SOCClasses.perennial_crops), .024, .042),
]


GL30_SOCC_mapping = {
    (): (),
    (): (),
}