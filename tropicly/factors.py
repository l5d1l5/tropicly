"""
factors.py

Author: Tobias Seydewitz
Date: 16.05.18
Mail: tobi.seyde@gmail.com
"""
from tropicly.enums import SOCClasses, GL30Classes


class SOCCFactor:
    def __init__(self, alias, mean, std):
        self.alias = alias
        self.mean = mean
        self.std = std  # standard deviation

    @property
    def min(self):
        return self.mean - self.std

    @property
    def max(self):
        return self.mean + self.std

    def __repr__(self):
        return '<{}(alias={}, mean={}, std={}) at {}>'.format(self.__class__.__name__, self.alias,
                                                              self.mean, self.std, hex(id(self)))


# Full depth soil organic carbon change factors
# Don et al. (2011) Impact of tropical land-use change on soil organic
# carbon stocks - a meta-analysis, Global Change Biology
SOCC_data = [
    SOCCFactor((SOCClasses.primary_forest, SOCClasses.grassland), .121, .023),
    SOCCFactor((SOCClasses.primary_forest, SOCClasses.cropland), .252, .033),
    SOCCFactor((SOCClasses.primary_forest, SOCClasses.perennial_crops), .303, .027),
    SOCCFactor((SOCClasses.primary_forest, SOCClasses.secondary_forest), .086, .02),
    SOCCFactor((SOCClasses.secondary_forest, SOCClasses.grassland), .064, .025),
    SOCCFactor((SOCClasses.secondary_forest, SOCClasses.cropland), .213, .041),
    SOCCFactor((SOCClasses.secondary_forest, SOCClasses.perennial_crops), .024, .042),
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
