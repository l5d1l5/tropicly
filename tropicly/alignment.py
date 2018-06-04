"""
alignment.py

Author: Tobias Seydewitz
Date: 01.06.18
Mail: tobi.seyde@gmail.com
"""



def alignment_worker(to_reproject, to_crs, to_merge_alike, out_path, generic_name):
    # TODO refactor get list of raster a tuple in list is a mergeable dataset
    template = None
    path = Path(out_path)

    for idx, raster in enumerate(to_reproject):
        out_path = str(path / 'reproject_{}_{}'.format(idx, generic_name))

        if idx == 0:
            try:
                template = reproject_from(raster, to_crs, out_path)
            except Exception as err:
                LOGGER.error('Fatal no template %s', raster, exc_info=err)
                raise err

        else:
            try:
                reproject_like(template, raster, out_path)
            except Exception as err:
                LOGGER.warning('Unable to reproject %s', raster, exc_info=err)

    kwargs = fetch_metadata(template, 'profile')

    for idx, rasters in enumerate(to_merge_alike):
        out_path = str(path / 'merge_{}_{}'.format(idx, generic_name))

        try:
            data, transform = merge_alike(template, rasters)
            kwargs.update({'transform': transform})
            write(data, out_path, **kwargs)

        except Exception as err:
            LOGGER.warning('Unable to merge %s, cant create %s', rasters, out_path)


def clip_worker(to_clip, bounds, profile, out_path):
    # TODO doc
    key = int_to_orient(bounds.left, bounds.top)
    path = Path(out_path)

    for idx, raster in enumerate(to_clip):
        data, transform = clip_raster(raster, bounds)
        opath = path / '{}_{}.tif'.format(idx, key)
        profile.update({'transform': transform})
        write(data, str(opath), **profile)