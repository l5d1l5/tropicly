"""
masking.py

Author: Tobias Seydewitz
Date: 26.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
import sys

import geopandas as gpd
import pandas as pd
from pyproj import Proj
from pyproj import transform
from rasterio import open
from rasterio.coords import BoundingBox
from rasterio.env import Env
from shapely.geometry import Polygon

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
        soc(SETTINGS['data'], SETTINGS['wgs84'])

    elif strata == 'aism':
        aism()

    else:
        gfc(SETTINGS['data'], SETTINGS['wgs84'])
        gl30(SETTINGS['data'], SETTINGS['wgs84'])
        agb(SETTINGS['data'])
        soc(SETTINGS['data'], SETTINGS['wgs84'])
        aism()


if __name__ == '__main__':
    name, *args = sys.argv
    main(*args)
