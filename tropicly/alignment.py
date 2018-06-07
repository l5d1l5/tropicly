"""
alignment.py

Author: Tobias Seydewitz
Date: 01.06.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import geopandas as gpd
from rasterio.features import rasterize
from tropicly.raster import (clip,
                             write,
                             merge_from,
                             clip_raster,
                             round_bounds,
                             polygon_from,
                             int_to_orient,
                             reproject_like,
                             make_warp_profile,)


CRS = {'init': 'epsg:4326'}


def worker(template, alignments, vector, pathobj):
    kwargs = make_warp_profile(template, CRS)
    kwargs['out'] = pathobj

    out = raster_alignment(alignments, **kwargs)
    data = rasterize_vector(kwargs['transform'], kwargs['bounds'], (kwargs['width'], kwargs['height']), vector)
    out['ifl'] = write(data, str(pathobj/'test.tif'), **kwargs)

    kwargs['bounds'] = round_bounds(kwargs['bounds'])
    out2 = raster_clip(out, **kwargs)


def raster_alignment(alignments, **kwargs):
    out = {}

    for key, values in alignments.items():
        values = list(set(values))

        name = '{}{:x}.tif'.format(key, abs(hash(''.join(values))))
        path = str(kwargs['out']/name)

        if len(values) == 1:
            out[key] = reproject_like(values[0], path, **kwargs)

        elif len(values) > 1:
            data, affine = merge_from(values, bounds=kwargs['bounds'], res=kwargs['res'])
            out[key] = write(data, path, **kwargs)

        else:
            continue

    return out


def raster_clip(to_clip, bounds, **kwargs):
    orientation = int_to_orient(bounds.left, bounds.top)
    out = {}

    for key, value in to_clip.items():
        name = '{}_{}.tif'.format(key, orientation)
        path = str(kwargs['out']/name)

        data, transform = clip_raster(value, bounds)
        kwargs.update({'transform': transform})
        out[key] = write(data, path, **kwargs)

    return out


def rasterize_vector(transform, bounds, shape, vector):
    """

    :param transform:
    :param bounds:
    :param shape:
    :param vector:
    :return:
    """
    clipper = polygon_from(bounds)
    geometries = list(vector.cx[bounds[0]:bounds[2], bounds[1]:bounds[3]].geometry)

    if geometries:
        clipped = clip(clipper, geometries)
        raster = rasterize(clipped, out_shape=shape, transform=transform, dtype=np.uint8)

        return raster

    return np.zeros(shape=shape, dtype=np.uint8)


if __name__ == '__main__':
    from pathlib import Path
    out = {'gl30_10': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2010lc030.tif'], 'soc': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/soil/GSOCmapV1.1.tif'], 'gain': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_gain_10N_080W.tif'], 'biomass': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/10N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/10N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/10N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/20N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/20N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/20N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/10N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/20N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/10N_080W_merge.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/biomass/20N_080W_merge.tif'], 'gl30_00': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gl30/n18_05_2000lc030.tif'], 'loss': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_lossyear_10N_080W.tif'], 'cover': ['/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif', '/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10N_080W.tif']}
    vector = gpd.read_file('/media/ilex/StorageOne/docs/code/python/projects/Master/data/core/ifl/ifl_2000.shp')
    worker(out['gl30_10'][0], out, vector, Path('/home/ilex/Documents/'))

