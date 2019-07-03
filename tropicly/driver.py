"""
Module: driver
****

:Author: Tobias Seydewitz
:Date: 05.06.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
from raster import merge
# merge regions
# select aism and driver mask join on key select all tiles south america, africa, asia and merge
# merge per countries
# grid
# create grid for regional layers


def merge_regions():
    aism = gpd.read_file(dirs.masks / 'aism.shp')
    pdd = gpd.read_file(dirs.masks / 'driver.shp')

    merged = aism.merge(pdd, on='key')

    for group, df in merged.groupby('region'):
        pass


def merge_countries():
    pass


def create_grid():
    pass