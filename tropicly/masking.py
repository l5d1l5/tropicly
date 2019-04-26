"""
masking.py

Author: Tobias Seydewitz
Date: 26.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
import sys

import geopandas as gpd

from settings import SETTINGS
import pandas as pd


def polygoniz(rasters, target_crs):
    """
    This function creates a tile index from a list of raster files.

    :param rasters: list
        Pending
    :param target_crs: dict
        If the raster files have different coordinate reference systems
        this argument prevents a messed up dataset.
    :return: geopandas.GeoSeries
        Each element of the series is a polygon
        covering the corresponding raster file.
    """
    polygons = []
    for raster in rasters:
        bounds, crs = fetch_metadata(raster, 'bounds', 'crs')

        with rio.Env():
            if crs != target_crs:
                bounds = reproject_bounds(bounds, crs, target_crs)

        polygon = polygon_from(bounds)
        polygons.append(polygon)

    geometry = gpd.GeoSeries(polygons)
    geometry.crs = target_crs

    return geometry


def tile_index(strata, crs, **kwargs):
    """

    Args:
        strata ():
        crs:
        **kwargs:

    Returns:
        geopandas.GeoDataFrame: The tile index
    """
    geometry = polygoniz(strata, crs)
    features = pd.DataFrame(kwargs)

    return gpd.GeoDataFrame(features, geometry=geometry)


def gfc(dirs, crs):
    strata = sorted(dirs.gfc.glob('*.tif'))
    strata_set_length = int(len(strata) / 3)

    names = ('gain', 'loss', 'cover')
    intervals = (
        slice(0, strata_set_length),
        slice(strata_set_length, 2*strata_set_length),
        slice(2*strata_set_length, len(strata))
    )

    kwargs = {
        name: [stratum.name for stratum in strata[interval]]
        for name, interval in zip(names, intervals)
    }

    gfc_mask = tile_index(strata[intervals[0]], crs, **kwargs)
    gfc_mask.to_file(str(dirs.masks / 'gfc.shp'))


def gl30(dirs, crs):
    strata = sorted(dirs.gl30.glob('*.tif'), key=lambda key: (key.name[7:11], key.name[0:6]))

    # filter tiles located in UTM Zone 1 and 60 (crs issues with these tiles, tile bounds exceed UTM Zone bounds)
    strata = list(filter(lambda stratum: int(stratum.name[1:3]) not in (1, 60), strata))

    strata_set_length = int(len(strata) / 2)
    names = ('gl30_00', 'gl30_10')
    intervals = (
        slice(0, strata_set_length),
        slice(strata_set_length, len(strata))
    )

    kwargs = {
        name: [stratum.name for stratum in strata[interval]]
        for name, interval in zip(names, intervals)
    }

    # we use the raster tile bounds of the gl30_2010 dataset (surprisingly 2000 and 2010 have differing bounds)
    gl30_mask = tile_index(strata[intervals[1]], crs, **kwargs)
    gl30_mask.to_file(str(dirs.masks / 'gl30.shp'))


def agb(dirs):
    strata = gpd.read_file(str(dirs.biomass / 'biomass.geojson'))
    strata.drop(strata.columns[[0, 1, 3, 4, 5, 6]], axis=1, inplace=True)
    strata.columns = ['biomass', 'geometry']

    for idx, row in strata.iterrows():
        row.biomass = row.biomass.split('/')[-1]

    strata.to_file(str(dirs.masks / 'biomass.shp'))


def soc():
    pass


def aism():
    pass


def main(strata):
    strata = strata.lower()

    if strata == 'gfc':
        gfc(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'gl30':
        gl30(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'agb':
        agb(SETTINGS['data'])

    elif strata == 'soc':
        soc()

    elif strata == 'aism':
        aism()

    else:
        gfc(SETTINGS['data'], SETTINGS['wgs84'])
        gl30(SETTINGS['data'], SETTINGS['wgs84'])
        agb(SETTINGS['data'])
        soc()
        aism()


if __name__ == '__main__':
    name, *args = sys.argv
    main(*args)
