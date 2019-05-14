"""
alignment
****

:Author: Tobias Seydewitz
:Date: 30.04.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import logging
import os
import re
from sys import argv
from threading import Thread
from time import time

import geopandas as gpd
import numpy as np
from rasterio.features import rasterize

from raster import clip
from raster import clip_raster
from raster import int_to_orient
from raster import make_warp_profile
from raster import merge_from
from raster import polygon_from
from raster import reproject_like
from raster import round_bounds
from raster import write
from settings import SETTINGS
from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress

LOGGER = logging.getLogger(__name__)


def raster_clip(to_clip, bounds, **kwargs):
    """Documentation pending

    Args:
        to_clip:
        bounds:
        **kwargs:

    Returns:
        dict:
    """
    orientation = int_to_orient(bounds.left, bounds.top)
    out = {}

    for key, value in to_clip.items():
        name = '{}_{}.tif'.format(key, orientation)
        path = str(kwargs['out'] / name)

        data, transform = clip_raster(value, bounds)
        kwargs.update({'transform': transform})
        out[key] = write(data, path, **kwargs)

    return out


def rasterize_vector(vector, transform, bounds, shape):
    """Documentation pending

    Args:
        vector:
        transform:
        bounds:
        shape:

    Returns:

    """
    clipper = polygon_from(bounds)
    geometries = list(vector.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]].geometry)

    if geometries:
        clipped = clip(clipper, geometries)
        raster = rasterize(clipped, out_shape=shape, transform=transform, dtype=np.uint8)

        return raster

    return np.zeros(shape=shape, dtype=np.uint8)


def raster_alignment(strata, **kwargs):
    """Documentation pending

    Args:
        strata (dict): Strata
        **kwargs (dict): Warp profile

    Returns:
        dict: A dict of str
    """
    out = {}

    for key, values in strata.items():
        length = len(values)
        # create a name for intermediate stratum
        tmp_name = '{}{:x}.tif'.format(key, abs(hash(''.join(values) + str(time()))))
        tmp_name = str(kwargs['out'] / tmp_name)

        # strata set just one stratum reproject with warp profile
        if length == 1:
            try:
                out[key] = reproject_like(*values, tmp_name, **kwargs)

            except Exception:
                LOGGER.error('Failed strata %s includes these files %s', key, values)

        # strata set greater > 1 merge and reproject
        elif length > 1:
            try:
                data, affine = merge_from(values, bounds=kwargs['bounds'], res=kwargs['res'])
                out[key] = write(data, tmp_name, **kwargs)

            except Exception:
                LOGGER.error('Failed strata %s includes these files %s', key, values)

        else:
            LOGGER.warning('Strata %s is empty', key)

    return out


def alignment_worker(template_stratum, strata, ifl, crs, out_path):
    """Worker function to parallelize alignment process.

    First, create a warp profile for ``template_stratum`` with ``crs``. After, apply this profile to all strata sets
    in ``strata`` (should contain a path to template stratum as well). Next, rasterize IFL stratum by applying
    warp profile. Finally, round bounds of strata and clip them all and write the final product.

    Args:
        template_stratum (Path): Template raster stratum.
        strata (dict): Strata which will be aligned with the template stratum. Dict key must be a string and value
            should be a list of paths to strata.
        ifl (geopandas.GeoDataFrame): The Intact Forest Landscape stratum as vector layer.
        crs (rasterio.crs.CRS): Each stratum will be reprojected to this CRS.
        out_path (Path): Final and intermediate layers will stored here.
    """
    # make a warp profile for the template stratum by using the requested CRS
    kwargs = make_warp_profile(template_stratum, crs)
    # intermediate strata will be stored in out_path
    kwargs['out'] = out_path

    # align all strata by applying the warp profile
    out = raster_alignment(strata, **kwargs)

    # rasterize ifl vector by applying warp profile
    data = rasterize_vector(ifl, kwargs['transform'], kwargs['bounds'], (kwargs['height'], kwargs['width']))
    name = 'ifl{:x}.tif'.format(id(data))
    out['ifl'] = write(data, str(out_path / name), **kwargs)

    # round strata bounds to int degrees
    kwargs['bounds'] = round_bounds(kwargs['bounds'])

    # clip strata to this bounds
    raster_clip(out, **kwargs)


def align(dirs, sheduler, crs):
    """Creates the AISM

    Requires the ``/data/interim/masks/intersection.shp``. The AISM is stored in
    the ``/data/interim/aism`` folder.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel alignment.
        crs: crs (rasterio.crs.CRS): Alignment will use the defined crs.
    """
    intersection = gpd.read_file(str(dirs.masks / 'intersection.shp'))
    ifl = gpd.read_file(str(dirs.ifl / 'ifl_2000.shp'))

    for key, strata in intersection.groupby(by='key', sort=False):

        # key will be used as the name of the AISM stratum
        strata_mapping = {
            'gl30_00': {str(dirs.gl30 / stratum) for stratum in strata.gl30_00},
            'gl30_10': {str(dirs.gl30 / stratum) for stratum in strata.gl30_10},
            'cover': {str(dirs.gfc / stratum) for stratum in strata.cover},
            'loss': {str(dirs.gfc / stratum) for stratum in strata.loss},
            'gain': {str(dirs.gfc / stratum) for stratum in strata.gain},
            'soc': {str(dirs.gsocmap / stratum) for stratum in strata.soc},
            'biomass': {str(dirs.biomass / stratum) for stratum in strata.biomass}
        }

        sheduler.add_task(
            Thread(
                target=alignment_worker,
                args=(list(strata_mapping['gl30_10'])[0], strata_mapping, ifl, crs, dirs.aism)
            )
        )


def intersect(dirs):
    """Creates a intersection layer of the downloaded strata.

    The intersection layer is fundamental for the alignment process.
    The intersection layer will be stored in the ``/data/interim/masks`` folder.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
    """
    soc = gpd.read_file(str(dirs.masks / 'soc.shp'))
    gfc = gpd.read_file(str(dirs.masks / 'gfc.shp'))
    gl30 = gpd.read_file(str(dirs.masks / 'gl30.shp'))
    biomass = gpd.read_file(str(dirs.masks / 'biomass.shp'))

    intersection = gpd.overlay(soc, gl30)
    intersection = gpd.overlay(intersection, gfc, how='intersection')
    intersection = gpd.overlay(intersection, biomass, how='intersection')

    intersection.to_file(str(dirs.masks / 'intersection.shp'))


def clean_temporary(dirs, sheduler):
    """Deletes temporary files created during the alignment process.

    Files are deleted from ``/data/interim/aism`` directory.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel cleanup.
    """
    for f in dirs.aism.glob('*.tif'):
        if not re.match(r'\w+_\d{2}[NS]_\d{3}[WE]\.tif', f.name):
            sheduler.add_task(Thread(target=os.remove, args=(str(f),)))


def main(operation, threads):
    """Entry point for strata alignment to create the Aligned Image Stack Mosaic (AISM).

    Defaults to error message.

    Args:
        operation (str): One of intersect, align, or clean.
        threads (int): umber of threads to spawn for the alignment or clean process.
    """
    operation = operation.lower()

    sheduler = TaskSheduler('alignment', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    LOGGER.setLevel(logging.WARNING)
    handler = logging.FileHandler(str(SETTINGS['data'].log / 'alignment.log'), mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    if operation == 'intersect':
        intersect(SETTINGS['data'])

    elif operation == 'align':
        align(SETTINGS['data'], sheduler, SETTINGS['wgs84'])

    elif operation == 'clean':
        clean_temporary(SETTINGS['data'], sheduler)

    else:
        print('Unknown operation \"%s\". Please, select one of [intersect, align, clean].' % operation)

    sheduler.quite()


if __name__ == '__main__':
    _, *args = argv
    main(*args)

