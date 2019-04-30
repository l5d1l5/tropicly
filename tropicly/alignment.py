"""
alignment.py

Author: Tobias Seydewitz
Date: 30.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
import logging
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
    clipper = polygon_from(bounds)
    geometries = list(vector.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]].geometry)

    if geometries:
        clipped = clip(clipper, geometries)
        raster = rasterize(clipped, out_shape=shape, transform=transform, dtype=np.uint8)

        return raster

    return np.zeros(shape=shape, dtype=np.uint8)


def raster_alignment(strata, **kwargs):
    out = {}

    for key, values in strata.items():
        length = len(values)
        tmp_name = '{}{:x}.tif'.format(key, abs(hash(''.join(values) + str(time()))))
        tmp_name = str(kwargs['out'] / tmp_name)

        if length == 1:
            try:
                out[key] = reproject_like(*values, tmp_name, **kwargs)

            except Exception:
                LOGGER.error('Failed strata %s includes these files %s', key, values)

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
    kwargs = make_warp_profile(template_stratum, crs)
    kwargs['out'] = out_path

    out = raster_alignment(strata, **kwargs)

    data = rasterize_vector(ifl, kwargs['transform'], kwargs['bounds'], (kwargs['height'], kwargs['width']))
    name = 'ifl{:x}.tif'.format(id(data))
    out['ifl'] = write(data, str(out_path / name), **kwargs)

    kwargs['bounds'] = round_bounds(kwargs['bounds'])

    raster_clip(out, **kwargs)


def align(dirs, sheduler, crs):
    intersection = gpd.read_file(str(dirs.masks / 'intersection.shp'))
    ifl = gpd.read_file(str(dirs.ifl / 'ifl_2000.shp'))

    for key, strata in intersection.groupby(by='key', sort=False):

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
    soc = gpd.read_file(str(dirs.masks / 'soc.shp'))
    gfc = gpd.read_file(str(dirs.masks / 'gfc.shp'))
    gl30 = gpd.read_file(str(dirs.masks / 'gl30.shp'))
    biomass = gpd.read_file(str(dirs.masks / 'biomass.shp'))

    intersection = gpd.overlay(soc, gl30)
    intersection = gpd.overlay(intersection, gfc, how='intersection')
    intersection = gpd.overlay(intersection, biomass, how='intersection')

    intersection.to_file(str(dirs.masks / 'intersection.shp'))


def main(operation, threads):
    operation = operation.lower()

    sheduler = TaskSheduler('download', int(threads))
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

    else:
        intersect(SETTINGS['data'])
        align(SETTINGS['data'], sheduler, SETTINGS['wgs84'])

    sheduler.quite()


if __name__ == '__main__':
    name, *args = argv
    main(*args)

