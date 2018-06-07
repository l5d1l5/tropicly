"""
alignment.py

Author: Tobias Seydewitz
Date: 01.06.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from rasterio import open
from rasterio.features import rasterize
from rasterio.warp import calculate_default_transform
from tropicly.raster import (write, reproject_like, merge_from, polygon_from, clip, reproject_from)


CRS = {'init': 'epsg:4326'}


def worker(template, alignments, pathobj):
    kwargs = trans(template)
    kwargs['out'] = pathobj
    print(alignment(alignments, **kwargs))


def alignment(alignments, **kwargs):
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


def trans(template):
    with open(template, 'r') as src:
        affine, width, height = calculate_default_transform(
            src_crs=src.crs,
            dst_crs=CRS,
            width=src.width,
            height=src.height,
            **src.bounds._asdict(),
        )

        kwargs = src.profile.copy()

    bounds = bounds_from_transform(affine, width, height)

    kwargs.update(
        transform=affine,
        width=width,
        height=height,
        compress='lzw',
        crs=CRS,
        res=(abs(affine[0]), abs(affine[4])),
        bounds=bounds
    )

    return kwargs


def bounds_from_transform(transform, width, height):
    return (transform.xoff, transform.yoff+(height*transform[4]),
            transform.xoff+(width*transform[0]), transform.yoff)


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
    out = {'gain': ['/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_gain_20S_030E.tif'], 'soc': ['/home/tobi/Documents/Master/code/python/Master/data/core/soil/GSOCmapV1.1.tif'], 'gl30_00': ['/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2000lc030.tif'], 'loss': ['/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_lossyear_20S_030E.tif'], 'cover': ['/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_10S_020E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gfc/Hansen_GFC2013_treecover2000_20S_030E.tif'], 'biomass': ['/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/biomass/s36_20_2000lc030.tif'], 'gl30_10': ['/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif', '/home/tobi/Documents/Master/code/python/Master/data/core/gl30/s36_20_2010lc030.tif']}
    out['biomass'] = []

    worker(out['gl30_10'][0], out, Path('/home/tobi/Documents/'))

