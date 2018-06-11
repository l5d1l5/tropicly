"""
alignment.py

Author: Tobias Seydewitz
Date: 01.06.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
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
    data = rasterize_vector(vector, **kwargs)
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


def rasterize_vector(vector, transform, bounds, shape):
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
