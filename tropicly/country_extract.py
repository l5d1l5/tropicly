from tropicly.raster import merge_from, write
from tropicly.utils import get_data_dir, cache_directories
import geopandas as gpd
import rasterio as rio
from rasterio.mask import mask
from rasterio.crs import CRS
import os
import re
import gc


DIRS = cache_directories(get_data_dir())
WGS84 = CRS.from_epsg(4326)

countries = gpd.read_file(DIRS.masks / 'earth.shp')
aism = gpd.read_file(DIRS.auxiliary / 'mask.shp')

intersection = gpd.overlay(countries, aism, how='intersection')
groups = intersection.groupby(by='NAME')

for country, gdf in groups:
    normalized_country = country.lower()
    normalized_country = re.sub(r' ', '_', normalized_country)
    normalized_country = re.sub(r'\.', '', normalized_country)

    if normalized_country in ['algeria', 'angola', 'argentina', 'australia',
                              'bahamas', 'bangladesh', 'belize', 'benin',
                              'bolivia', 'brazil', 'botswana']:
        continue

    merge_msg = 'Merging: {}'.format(normalized_country)
    clip_msg = 'Clip: {}'.format(normalized_country)

    driver_tiles = [DIRS.driver / tile for tile in set(gdf.driver)]

    country_geometry = countries[countries['NAME'] == country].__geo_interface__
    country_geometry = country_geometry['features'][0]['geometry']

    print(merge_msg)
    data, transform = merge_from(driver_tiles)
    f = write(data, DIRS.tif / '{}.tif'.format(normalized_country),
              crs=WGS84, transform=transform, driver='GTiff', compress='lzw')

    del data, transform
    gc.collect()

    print(clip_msg)
    with rio.open(f, 'r') as src:
        data, transform = mask(src, [country_geometry], crop=True)

    write(data, DIRS.tif / 'driver_{}.tif'.format(normalized_country),
          crs=WGS84, transform=transform, driver='GTiff', compress='lzw')

    os.remove(str(f))

