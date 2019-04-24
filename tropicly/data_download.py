"""
data_download

Author: Tobias Seydewitz
Date: 24.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
import os
import re
import zipfile
from sys import argv
from threading import Thread
from urllib import request

import geopandas as gpd

from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress
from utils import cache_directories
from utils import get_data_dir
from utils import orientation_to_int

HEADERS = {'headers': {'User-Agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}}


def download(url, **kwargs):
    req = request.Request(url, **kwargs)
    response = None

    try:
        response = request.urlopen(req)

    except:
        pass  # log error -> unable to download URL

    if response is not None:
        return response.read()

    return response


def write_binary(content, to_path):
    with open(to_path, 'wb') as dst:
        dst.write(content)


def download_worker(url, to_path, **kwargs):
    content = download(url, **kwargs)

    if content is not None:
        write_binary(content, to_path)


def gfc(sheduler, dirs, **kwargs):
    """Downloads the required Global Forest Change stratum."""
    head_url = 'http://commondatastorage.googleapis.com/earthenginepartners-hansen/GFC2013/'
    tails = 'treecover2000.txt gain.txt lossyear.txt'.split()

    stratum_urls = []
    for tail in tails:
        content = download(head_url + tail, **kwargs)
        stratum_urls += content.decode('utf-8').splitlines()

    for url in stratum_urls:
        lat_lon = re.search(r'(\d{2}\w_\d{3}\w)(?=\.tif)', url).groups()[0]
        lat = orientation_to_int(lat_lon.split('_')[0])

        if -20 <= lat <= 30:
            path = str(dirs.gfc / url.split('/')[-1])
            sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def agb(sheduler, dirs, **kwargs):
    """Downloads the required Above-ground Woody Biomass density (agb) stratum."""
    head_url = 'http://data.globalforestwatch.org/datasets/8f93a6f94a414f9588ce4657a39c59ff_1.geojson'
    path = str(dirs.auxiliary / 'biomass.geojson')

    content = download(head_url)
    write_binary(content, path)

    biomass_mask = gpd.read_file(path)
    stratum_urls = list(biomass_mask.download) + list(biomass_mask.confidence)

    for url in stratum_urls:
        path = str(dirs.biomass / url.split('/')[-1])
        sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def soc(dirs, **kwargs):
    """Downloads the required Soil Organic Carbon Content (GSOCmap) stratum."""
    url = 'http://54.229.242.119/GSOCmap/downloads/GSOCmapV1.2.0.tif'

    content = download(url, **kwargs)
    write_binary(content, str(dirs.soil / 'GSOCmap.tif'))


def ifl(dirs, **kwargs):
    """Downloads the required Intact Forest Landscape (IFL) stratum."""
    url = 'http://intactforests.org/shp/IFL_2000.zip'

    content = download(url, **kwargs)
    write_binary(content, str(dirs.ifl / url.split('/')[-1]))

    zipfile.ZipFile(str(dirs.ifl / url.split('/')[-1])).extractall(str(dirs.ifl))
    os.remove(str(dirs.ifl / url.split('/')[-1]))


def auxiliary(dirs, **kwargs):
    url = 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_populated_places.zip'

    content = download(url, **kwargs)
    write_binary(content, str(dirs.auxiliary / url.split('/')[-1]))

    zipfile.ZipFile(str(dirs.auxiliary / url.split('/')[-1])).extractall(str(dirs.auxiliary))
    os.remove(str(dirs.auxiliary / url.split('/')[-1]))

    url = 'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip'

    content = download(url, **HEADERS)
    write_binary(content, str(dirs.auxiliary / url.split('/')[-1]))

    zipfile.ZipFile(str(dirs.auxiliary / url.split('/')[-1])).extractall(str(dirs.auxiliary))
    os.remove(str(dirs.auxiliary / url.split('/')[-1]))


def main(key, threads):
    key = key.lower()

    sheduler = TaskSheduler('download', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    dirs = cache_directories(get_data_dir())

    if key == 'gfc':
        gfc(sheduler, dirs, **HEADERS)

    elif key == 'agb':
        agb(sheduler, dirs, **HEADERS)

    elif key == 'soc':
        soc(dirs, **HEADERS)

    elif key == 'ifl':
        ifl(dirs, **HEADERS)

    else:
        gfc(sheduler, dirs, **HEADERS)
        agb(sheduler, dirs, **HEADERS)
        soc(dirs, **HEADERS)
        ifl(dirs, **HEADERS)

    sheduler.quite()


if __name__ == '__main__':
    *_, key, threads = argv
    main(key, threads)
