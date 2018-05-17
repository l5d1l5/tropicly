"""
soc_emissions.py

Author: Tobias Seydewitz
Date: 14.05.18
Mail: tobi.seyde@gmail.com
"""
from tropicly.enums import SOCClasses, GL30Classes
from tropicly.factors import Factors, SOCCFactor
from tropicly.distance import Distance
from tropicly.utils import write
import rasterio as rio
import numpy as np



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

mapping = {
    (SOCClasses.primary_forest, GL30Classes.cropland): (SOCClasses.primary_forest, SOCClasses.cropland),
    (SOCClasses.primary_forest, GL30Classes.regrowth): (SOCClasses.primary_forest, SOCClasses.secondary_forest),
    (SOCClasses.primary_forest, GL30Classes.grassland): (SOCClasses.primary_forest, SOCClasses.grassland),
    (SOCClasses.primary_forest, GL30Classes.shrubland): (SOCClasses.primary_forest, SOCClasses.grassland),
    (SOCClasses.primary_forest, GL30Classes.tundra): (SOCClasses.primary_forest, SOCClasses.grassland),
    (SOCClasses.primary_forest, GL30Classes.bareland): (SOCClasses.primary_forest, SOCClasses.grassland),
    (SOCClasses.secondary_forest, GL30Classes.cropland): (SOCClasses.secondary_forest, SOCClasses.cropland),
    (SOCClasses.secondary_forest, GL30Classes.grassland): (SOCClasses.secondary_forest, SOCClasses.grassland),
    (SOCClasses.secondary_forest, GL30Classes.shrubland): (SOCClasses.secondary_forest, SOCClasses.grassland),
    (SOCClasses.secondary_forest, GL30Classes.tundra): (SOCClasses.secondary_forest, SOCClasses.grassland),
    (SOCClasses.secondary_forest, GL30Classes.bareland): (SOCClasses.secondary_forest, SOCClasses.grassland),
}


def soc(driver, s, intact):
    factors = Factors('SOCCFactors', *SOCC_data)
    hav = Distance('hav')
    px = 0.09

    socppx = np.copy(s) * 0.09

    # create factor map
    factormap = np.zeros(driver.shape, dtype=np.float)
    for i in GL30Classes:
        factor = factors.get(mapping.get((SOCClasses.primary_forest, i), None), SOCCFactor(1, 0, 0))
        factormap[driver == i.value] = factor.value

    emission = socppx * factormap * (44/12)

    return emission


class SOCChange:
    def __init__(self, driver, soc, intact=None, soccfm=mapping, dist='hav',
                 co2=3.7, areaf=0.0001, f=('min', 'value', 'max')):
        # raster
        self.driver = driver
        self.intact = intact
        self.soc = soc

        self.factors = Factors('SOCCFactors', *SOCC_data)
        self.soccfm = soccfm
        self.f = f

        self.co2 = co2
        self.areaf = areaf
        self.dist = Distance(dist)

        self.driver_handle = None
        self.soc_handle = None
        self.intact_handle = None

        self.driver_data = None
        self.soc_data = None
        self.intact_data = None

    def _factor_map(self, attr):
        factormap = np.zeros(self.driver_data.shape, dtype=np.float)

        for member in GL30Classes:
            alias = mapping.get((SOCClasses.secondary_forest, member), None)
            factor = self.factors.get(alias, SOCCFactor('default', 0, 0))

            factormap[self.driver_data == member.value] = factor.__getattribute__(attr)

        return factormap

    def _handle_raster_open(self, *args):
        pass

    def run(self):
        pass

        for attr in self.f:
            factormap = self._factor_map(attr)


if __name__ == '__main__':
    driver = rio.open('/home/tobi/Documents/Master/code/python/Master/data/driv/driver_10S_060W.tif').read(1)
    s = rio.open('/home/tobi/Documents/Master/code/python/Master/data/proc/6_10S_060W.tif').read(1)

    profile = rio.open('/home/tobi/Documents/Master/code/python/Master/data/driv/driver_10S_060W.tif').profile

    emission = soc(driver, s, None)
    write(emission, '/home/tobi/Documents/em.tif', **profile)