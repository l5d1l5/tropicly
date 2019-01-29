from time import time

import numpy as np
from rasterio.features import rasterize

from tropicly.raster import clip
from tropicly.raster import clip_raster
from tropicly.raster import int_to_orient
from tropicly.raster import make_warp_profile
from tropicly.raster import merge_from
from tropicly.raster import polygon_from
from tropicly.raster import reproject_like
from tropicly.raster import round_bounds
from tropicly.raster import write


# TODO thesis
# TODO exceptions


def worker(template, alignments, vector, crs, pathobj):
    # TODO refactor
    kwargs = make_warp_profile(template, crs)
    kwargs['out'] = pathobj

    out = raster_alignment(alignments, **kwargs)

    data = rasterize_vector(vector, kwargs['transform'], kwargs['bounds'], (kwargs['height'], kwargs['width']))
    name = 'ifl{:x}.tif'.format(id(data))
    out['ifl'] = write(data, str(pathobj / name), **kwargs)

    kwargs['bounds'] = round_bounds(kwargs['bounds'])

    return raster_clip(out, **kwargs)


def raster_alignment(alignments, **kwargs):
    # TODO refactor
    out = {}

    for key, values in alignments.items():
        values = list(set(values))

        name = '{}{:x}.tif'.format(key, abs(hash(''.join(values) + str(time()))))
        path = str(kwargs['out'] / name)

        err_msg = 'Failed at {} files {}'.format(key, values)

        if len(values) == 1:
            try:
                out[key] = reproject_like(*values, path, **kwargs)
            except Exception:
                print(err_msg)

        elif len(values) > 1:
            try:
                data, affine = merge_from(values, bounds=kwargs['bounds'], res=kwargs['res'])
                out[key] = write(data, path, **kwargs)
            except Exception:
                print(err_msg)

        else:
            continue

    return out


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
