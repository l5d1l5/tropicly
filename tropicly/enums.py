from enum import Enum

from tropicly.factors import Coefficient


# TODO doc


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

    The enum member values correspond to the pixel values of our
    proximate deforestation driver predictions.
    """
    cropland = 10
    forest = 20
    # not in Chen et al. introduced by us to represent Hansen et al. gain
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


# Full depth soil organic carbon change coefficients
# Don et al. (2011) Impact of tropical land-use change on soil organic
# carbon stocks - a meta-analysis, Global Change Biology
PRIMARY_FOREST_GRASSLAND_TRANSITION = Coefficient('primary forest -> grassland', .121, .023)
PRIMARY_FOREST_CROPLAND_TRANSITION = Coefficient('primary forest -> cropland', .252, .033)
PRIMARY_FOREST_PERENNIAL_CROPS_TRANSITION = Coefficient('primary forest -> perennial crops', .303, .027)
PRIMARY_FOREST_SECONDARY_FOREST_TRANSITION = Coefficient('primary forest -> secondary forest', .086, .02)
SECONDARY_FOREST_GRASSLAND_TRANSITION = Coefficient('secondary forest -> grassland', .064, .025)
SECONDARY_FOREST_CROPLAND_TRANSITION = Coefficient('secondary forest -> cropland', .213, .041)
SECONDARY_FOREST_PERENNIAL_CROPS_TRANSITION = Coefficient('secondary forest -> perennial crops', .024, .042)


# Mapping of soil organic carbon change coefficients to proximate deforestation driver classes
SOCCCoefficients = {
    (SOCClasses.primary_forest, GL30Classes.cropland): PRIMARY_FOREST_CROPLAND_TRANSITION,
    (SOCClasses.primary_forest, GL30Classes.regrowth): PRIMARY_FOREST_SECONDARY_FOREST_TRANSITION,
    (SOCClasses.primary_forest, GL30Classes.grassland): PRIMARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.primary_forest, GL30Classes.shrubland): PRIMARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.primary_forest, GL30Classes.tundra): PRIMARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.primary_forest, GL30Classes.bareland): PRIMARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.secondary_forest, GL30Classes.cropland): SECONDARY_FOREST_CROPLAND_TRANSITION,
    (SOCClasses.secondary_forest, GL30Classes.grassland): SECONDARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.secondary_forest, GL30Classes.shrubland): SECONDARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.secondary_forest, GL30Classes.tundra): SECONDARY_FOREST_GRASSLAND_TRANSITION,
    (SOCClasses.secondary_forest, GL30Classes.bareland): SECONDARY_FOREST_GRASSLAND_TRANSITION,
}


# ESV mappings should be dictionaries, dict key should be a member of the GL30classes enum
# dict value should be the corresponding ESV in monetary units (Int$/ha) as an instance of
# the Coefficient class

# Ecosystem service values per biome
# Costanza et al. (2014) Change in the global value of ecosystem services,
# Global Environmental Change
# 2011 values from supplementary table in 2007$/ha/yr
ESV_costanza = {
    'name': 'co',
    GL30Classes.cropland:   Coefficient('cropland', 5567, std=0),  # cropland 11 sub services
    GL30Classes.forest:     Coefficient('forest', 5382, std=0),  # forest tropical 17 sub services
    GL30Classes.regrowth:   Coefficient('forest', 5382, std=0),  # forest tropical 17 sub services
    GL30Classes.grassland:  Coefficient('grass', 4166, std=0),  # grassland/rangelands 15 sub services
    GL30Classes.shrubland:  Coefficient('shrub', 0, std=0),  # NEED A VALUE
    GL30Classes.wetland:    Coefficient('wet', 140174, std=0),  # Wetlands 15 sub services
    GL30Classes.water:      Coefficient('water', 12512, std=0),  # Lakes/Rivers 5 sub services
    GL30Classes.tundra:     Coefficient('tundra', 0, std=0),  # NEED A VALUE
    GL30Classes.artificial: Coefficient('artificial', 6661, std=0),  # urban 3 sub services
    GL30Classes.bareland:   Coefficient('bare', 0, std=0),  # NEED A VALUE
    GL30Classes.snow:       Coefficient('snow', 0, std=0),  # NEED A VALUE
    GL30Classes.no_data:    Coefficient('no_data', 0, std=0),
}

# Ecosystem service values per biome
# De Groot et al. (2012) Global estimates of the value of ecosystems
# and the services in monetary units, Ecosystem Services
# values from publication table in 2007$/ha/yr
ESV_deGroot = {
    'name': 'gr',
    GL30Classes.cropland:   Coefficient('cropland', 0, std=0),  # NEED A VALUE
    GL30Classes.forest:     Coefficient('forest', 5264, std=6526, med=2355, mini=1581, maxi=20851),  # trop. for. 17
    GL30Classes.regrowth:   Coefficient('forest', 5264, std=6526, med=2355, mini=1581, maxi=20851),  # trop. for. 17
    GL30Classes.grassland:  Coefficient('grass', 2871, std=3860, med=2698, mini=124, maxi=5930),  # grass 10
    GL30Classes.shrubland:  Coefficient('shrub', 0, std=0),  # NEED A Value
    GL30Classes.wetland:    Coefficient('wet', 25682, std=36585, med=16534, mini=3018, maxi=104925),  # inland 17
    GL30Classes.water:      Coefficient('water', 4267, std=2771, med=3938, mini=1446, maxi=7757),  # River/lake 4
    GL30Classes.tundra:     Coefficient('tundra', 0, std=0),  # NEED A VALUE
    GL30Classes.artificial: Coefficient('artificial', 0, std=0),  # NEED A VALUE
    GL30Classes.bareland:   Coefficient('bare', 0, std=0),  # NEED A VALUE
    GL30Classes.snow:       Coefficient('snow', 0, std=0),  # NEED A VALUE
    GL30Classes.no_data:    Coefficient('no_data', 0, std=0),
}

# Ecosystem service value of tropical forest
# Siikamäki et al. (2015) Global assessment of non-wood forest
# ecosystem services, PROFOR working paper
# from table 15
ESV_worldbank = {
    'name': 'wb',
    GL30Classes.cropland:   Coefficient('cropland', 0, std=0),  # ds per definition no value
    GL30Classes.forest:     Coefficient('forest', 1312, std=0),  # NWFP, water service, recreation, hunting/fishing
    GL30Classes.regrowth:   Coefficient('forest', 1312, std=0),  # NWFP, water service, recreation, hunting/fishing
    GL30Classes.grassland:  Coefficient('grass', 0, std=0),  # ds per definition no value
    GL30Classes.shrubland:  Coefficient('shrub', 0, std=0),  # ds per definition no value
    GL30Classes.wetland:    Coefficient('wet', 0, std=0),  # ds per definition no value
    GL30Classes.water:      Coefficient('water', 0, std=0),  # ds per definition no value
    GL30Classes.tundra:     Coefficient('tundra', 0, std=0),  # ds per definition no value
    GL30Classes.artificial: Coefficient('artificial', 0, std=0),  # ds per definition no value
    GL30Classes.bareland:   Coefficient('bare', 0, std=0),  # ds per definition no value
    GL30Classes.snow:       Coefficient('snow', 0, std=0),  # ds per definition no value
    GL30Classes.no_data:    Coefficient('no_data', 0, std=0),
}
