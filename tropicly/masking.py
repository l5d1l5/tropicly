"""
Module: masking
****

:Author: Tobias Seydewitz
:Date: 26.04.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import re
from collections import defaultdict
from sys import argv

import geopandas as gpd
import pandas as pd
from pyproj import Proj
from pyproj import transform
from rasterio import open
from rasterio.coords import BoundingBox
from rasterio.env import Env
from shapely.geometry import Polygon

from raster import orient_to_int
from settings import SETTINGS
from sheduler import progress


def polygon_from(bounds):
    """Creates a rectangular Polygon from an BoundingBox object.

    Args:
        bounds (rasterio.coords.BoundingBox): The bounding box of a raster image.

    Returns:
        shapely.geometry.Polygon: A rectangular polygon.
    """
    x_points = ['left', 'left', 'right', 'right']
    y_points = ['top', 'bottom', 'bottom', 'top']

    polygon_bounds = [
        (bounds.__getattribute__(x), bounds.__getattribute__(y))
        for x, y in zip(x_points, y_points)
    ]

    return Polygon(polygon_bounds)


def reproject_bounds(bounds, source_crs, target_crs):
    """Reproject BoundingBox from source crs to target crs.

    Args:
        bounds (rasterio.coords.BoundingBox): The BoundingBox as object.
        source_crs (rasterio.crs.CRS): Source crs of the BoundingBox.
        target_crs (rasterio.crs.CRS): Target crs of the BoundingBox.

    Returns:
        rasterio.coords.BoundingBox: The reprojected BoundingBox.
    """
    p1 = Proj(**source_crs)
    p2 = Proj(**target_crs)

    left, bottom = transform(p1, p2, bounds.left, bounds.bottom)
    right, top = transform(p1, p2, bounds.right, bounds.top)

    return BoundingBox(left, bottom, right, top)


def tiles(strata, target_crs):
    """Create rectangular polygons in required crs from raster bounds.

    Args:
        strata (list of str/Path): Full qualified path to raster files.
        target_crs (rasterio.crs.CRS): Reproject raster bounds to this crs.

    Returns:
        geopandas.GeoSeries: The convex hull of the rasters as a GeoSeries.
    """
    total = len(strata)
    polygons = []

    for idx, raster in enumerate(strata):
        with Env():
            with open(raster) as src:
                crs = src.crs
                bounds = src.bounds

            if crs != target_crs:
                bounds = reproject_bounds(bounds, crs, target_crs)

        polygon = polygon_from(bounds)
        polygons.append(polygon)

        progress(pending=total-(idx+1), total=total)

    geometry = gpd.GeoSeries(polygons)
    geometry.crs = target_crs

    return geometry


def tile_index(strata, crs, **kwargs):
    """Creates a tile index layer (bounds of each raster strata).

    Args:
        strata (list of str/Path): Full qualified path to raster files.:
        crs (rasterio.crs.CRS): Reproject raster bounds to this crs.
        **kwargs: Attribute table of the tile index layer.

    Returns:
        geopandas.GeoDataFrame: The tile index as a GeoDataFrame.
    """
    geometry = tiles(strata, crs)
    features = pd.DataFrame(kwargs)

    return gpd.GeoDataFrame(features, geometry=geometry)


def gfc(dirs, crs):
    """Create mask for Global Forest Change dataset.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        crs (rasterio.crs.CRS): Tile index layer will use the defined crs.
    """
    strata = sorted(dirs.gfc.glob('*.tif'))
    strata_set_length = int(len(strata) / 3)

    names = ('gain', 'loss', 'cover')
    intervals = (
        slice(0, strata_set_length),
        slice(strata_set_length, 2*strata_set_length),
        slice(2*strata_set_length, len(strata))
    )

    # attribute table
    kwargs = {
        name: [stratum.name for stratum in strata[interval]]
        for name, interval in zip(names, intervals)
    }

    gfc_mask = tile_index(strata[intervals[0]], crs, **kwargs)
    gfc_mask.to_file(str(dirs.masks / 'gfc.shp'))


def gl30(dirs, crs):
    """Create mask for GlobeLand30 dataset.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        crs (rasterio.crs.CRS): Tile index layer will use the defined crs.
    """
    strata = sorted(dirs.gl30.glob('*.tif'), key=lambda key: (key.name[7:11], key.name[0:6]))

    # filter tiles located in UTM Zone 1 and 60 (crs issues with these tiles, tile bounds exceed UTM Zone bounds)
    strata = list(filter(lambda stratum: int(stratum.name[1:3]) not in (1, 60), strata))

    strata_set_length = int(len(strata) / 2)
    names = ('gl30_00', 'gl30_10')
    intervals = (
        slice(0, strata_set_length),
        slice(strata_set_length, len(strata))
    )

    # attribute table
    kwargs = {
        name: [stratum.name for stratum in strata[interval]]
        for name, interval in zip(names, intervals)
    }
    kwargs['key'] = [stratum.name[:6] for stratum in strata[intervals[1]]]

    # we use the raster tile bounds of the gl30_2010 dataset (surprisingly 2000 and 2010 have differing bounds)
    gl30_mask = tile_index(strata[intervals[1]], crs, **kwargs)
    gl30_mask.to_file(str(dirs.masks / 'gl30.shp'))


def agb(dirs):
    """Create mask for Above-ground Woody Biomass Density dataset.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
    """
    strata = gpd.read_file(str(dirs.biomass / 'biomass.geojson'))
    strata.drop(strata.columns[[0, 1, 3, 4, 5, 6]], axis=1, inplace=True)
    strata.columns = ['biomass', 'geometry']

    for idx, row in strata.iterrows():
        row.biomass = row.biomass.split('/')[-1]

    strata.to_file(str(dirs.masks / 'biomass.shp'))


def soc(dirs, crs):
    """Create mask for GSOCmap dataset.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        crs (rasterio.crs.CRS): Tile index layer will use the defined crs.
    """
    strata = sorted(dirs.gsocmap.glob('*.tif'))

    names = ('soc',)

    # attribute table
    kwargs = {
        name: [stratum.name for stratum in strata]
        for name in names
    }

    gfc_mask = tile_index(strata, crs, **kwargs)
    gfc_mask.to_file(str(dirs.masks / 'soc.shp'))


def aism(dirs, crs):
    """Create mask for Aligned Image Stack Mosaic (AISM).

    The aism can be created with scripts provided in the alignment.py.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        crs (rasterio.crs.CRS): Tile index layer will use the defined crs.
    """
    strata_sets = defaultdict(dict)
    regex = re.compile(r'(\w+)_((\d{2}[NS])_(\d{3}[WE]))\.tif')
    strata = sorted(dirs.aism.glob('*.tif'), key=lambda f: regex.match(f.name).group(2))

    for f in strata:
        match = regex.match(f.name)
        name, key = match.group(1), match.group(2)
        lng, lat = orient_to_int(match.group(4), match.group(3))

        strata_sets[key][name] = f.name
        strata_sets[key]['key'] = key

        if -114 <= lng <= -36:
            strata_sets[key]['region'] = 'South America'

        elif -30 <= lng <= 54:
            strata_sets[key]['region'] = 'Africa'

        elif 66 <= lng <= 168:
            strata_sets[key]['region'] = 'Asia/Australia'

        else:
            strata_sets[key]['region'] = 'Unknown'

    df = pd.DataFrame(strata_sets).T
    df.reset_index(drop=True, inplace=True)

    gdf = gpd.GeoDataFrame(
        df,
        geometry=tile_index([dirs.aism / f for f in df['gl30_10']], crs)['geometry']
    )

    gdf.to_file(str(dirs.masks / 'aism.shp'))


def driver(dirs, crs):
    """Create mask for Proximated Deforestation Driver stratum.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        crs (rasterio.crs.CRS): Tile index layer will use the defined crs.
    """
    strata = list(dirs.driver.glob('*.tif'))
    regex = re.compile(r'\w+_(\d{2}[NS]_\d{3}[WE])\.tif')

    # attribute table
    kwargs = {
        'driver': [regex.match(stratum.name).group(0) for stratum in strata],
        'key': [regex.match(stratum.name).group(1) for stratum in strata]
    }

    driver_mask = tile_index(list(strata), crs, **kwargs)
    driver_mask.to_file(str(dirs.masks / 'driver.shp'))


def main(strata):
    """Entry point for strata masking.

    Creates a tile mask of the selected strata. Mask will be stored as ``*.shp`` file
    in the ``/data/interim/masks`` folder. Defaults to error message.

    Args:
        strata (str): One of gfc, gl30, agb, soc, aism, or driver.
    """
    strata = strata.lower()

    if strata == 'gfc':
        gfc(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'gl30':
        gl30(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'agb':
        agb(SETTINGS['data'])

    elif strata == 'soc':
        soc(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'aism':
        aism(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'driver':
        driver(SETTINGS['data'], SETTINGS['wgs84'])

    else:
        print('Unknown strata \"%s\". Please, select one of [gfc, gl30, agb, soc, aism].' % strata)


if __name__ == '__main__':
    _, *args = argv
    main(*args)
