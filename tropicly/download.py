"""**download**

:Author: Tobias Seydewitz
:Date: 24.04.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import logging
import os
import re
import zipfile
from sys import argv
from threading import Thread
from urllib import request

import geopandas as gpd

from settings import SETTINGS
from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress
from raster import orient_to_int

LOGGER = logging.getLogger('Download')


def download(url, **kwargs):
    """A simple function to download content from an URL.

    Args:
        url (str): URL ro request
        **kwargs: Request headers.

    Returns:
        b str: Response content
    """
    req = request.Request(url, **kwargs)

    try:
        response = request.urlopen(req)
        LOGGER.debug('Got response from %s', url)
        return response.read()

    except Exception:
        print('Request to URL %s failed' % url)
        LOGGER.error('Request to URL %s failed', url)


def write_binary(content, to_path):
    """Simple function to write binary content on disk.

    Args:
        content (b str): Content to write as binary str.
        to_path (str): Target path/name.
    """
    with open(to_path, 'wb') as dst:
        dst.write(content)


def download_worker(url, to_path, **kwargs):
    """A simple worker function for parallelize download and write operations.

    Args:
        url (str): URL to request.
        to_path (str): Content to write as binary str.
        **kwargs: Request headers
    """
    content = download(url, **kwargs)

    if content is not None:
        write_binary(content, to_path)


def gfc(sheduler, dirs, **kwargs):
    """Downloads the required Global Forest Change stratum.

    Files are stored in the ``/data/raw/gfc`` directory.

    **Citation:** *Hansen, M. C., P. V. Potapov, R. Moore, M. Hancher,
    S. A. Turubanova, A. Tyukavina, D. Thau, S. V. Stehman, S. J. Goetz,
    T. R. Loveland, A. Kommareddy, A. Egorov, L. Chini, C. O. Justice,
    and J. R. G. Townshend. 2013.
    “High-Resolution Global Maps of 21st-Century Forest Cover Change.”
    Science 342 (15 November): 850–53.*

    Args:
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel download.
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    head_url = 'http://commondatastorage.googleapis.com/earthenginepartners-hansen/GFC2013/'
    tails = 'treecover2000.txt gain.txt lossyear.txt'.split()

    stratum_urls = []
    for tail in tails:
        content = download(head_url + tail, **kwargs)
        stratum_urls += content.decode('utf-8').splitlines()

    for url in stratum_urls:
        lat, lng = re.search(r'(\d{2}[NS])_(\d{3}[WE])\.tif', url).groups()
        lng, lat = orient_to_int(lng, lat)

        if -20 <= lat <= 30:
            path = str(dirs.gfc / url.split('/')[-1])
            sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def agb(sheduler, dirs, **kwargs):
    """Downloads the required Above-ground Woody Biomass density (AGB) stratum.

    Files are stored in the ``/data/raw/biomass`` directory.

    **Citation:** *Woods Hole Research Center. Unpublished data. Accessed through
    Global Forest Watch Climate on [date]. climate.globalforestwatch.org*

    Args:
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel download.
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    head = 'https://gis-gfw.wri.org/arcgis/rest/services/climate/MapServer/1/'
    tail = 'query?where=1%3D1&outFields=*&geometry=-180%2C-24%2C180%2C24&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json'
    url = head + tail
    path = str(dirs.biomass / 'biomass.geojson')

    download_worker(url, path, **kwargs)

    biomass_mask = gpd.read_file(path)
    stratum_urls = list(biomass_mask.download)

    for url in stratum_urls:
        path = str(dirs.biomass / url.split('/')[-1])
        sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def soc(sheduler, dirs, **kwargs):
    """Downloads the required Soil Organic Carbon Content (GSOCmap) stratum.

    Files are stored in the ``/data/raw/gsocmap`` directory.

    **Citation:** *Food and Agriculture Organization of the United Nations,
    GSOCMap Version 1.2.0*

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    url = 'http://54.229.242.119/GSOCmap/downloads/GSOCmapV1.2.0.tif'

    sheduler.add_task(Thread(target=download_worker, args=(url, str(dirs.gsocmap/'GSOCmap.tif')), kwargs=kwargs))


def ifl(dirs, **kwargs):
    """Downloads the required Intact Forest Landscape (IFL) stratum.

    Files are stored in the ``/data/raw/ifl`` directory.

    **Citation:** *Potapov P., Yaroshenko A., Turubanova S., Dubinin M., Laestadius L.,
    Thies C., Aksenov D., Egorov A., Yesipova Y., Glushkov I., Karpachevskiy M.,
    Kostikova A., Manisha A., Tsybikova E., Zhuravleva I. 2008.
    Mapping the World's Intact Forest Landscapes by Remote Sensing. Ecology and Society, 13 (2)*

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    url = 'http://intactforests.org/shp/IFL_2000.zip'
    path = str(dirs.ifl / url.split('/')[-1])

    download_worker(url, path, **kwargs)

    zipfile.ZipFile(path).extractall(str(dirs.ifl))
    os.remove(path)


def auxiliary(dirs, **kwargs):
    """Downloads the required auxiliary strata.

    Files are stored in the ``/data/raw/auxiliary`` directory.

    **Citation:** *Tom Patterson and Nathaniel Vaughn Kelso, Natural Earth Data*

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    urls = [
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip',
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip'
    ]

    for url in urls:
        path = str(dirs.auxiliary / url.split('/')[-1])

        download_worker(url, path, **kwargs)

        zipfile.ZipFile(path).extractall(str(dirs.auxiliary))
        os.remove(path)


def main(strata, threads):
    """Entry point for data download.

    Downloads the required strata. Downloaded files will be stored in the ``/data/raw`` folder.
    Defaults to download all datasets if strata parameter is unknown.

    Args:
        strata (str): one of gfc, agb, soc, ifl, auxiliary or else. Downloads the corresponding dataset strata. Please,
            refer to the equivalent named methods for dataset details.
        threads (int): Number of threads to spawn for the download process.
    """
    strata = strata.lower()

    sheduler = TaskSheduler('download', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    LOGGER.setLevel(logging.WARNING)
    handler = logging.FileHandler(str(SETTINGS['data'].log / 'download.log'), mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    if strata == 'gfc':
        gfc(sheduler, SETTINGS['data'], **SETTINGS['headers'])

    elif strata == 'agb':
        agb(sheduler, SETTINGS['data'], **SETTINGS['headers'])

    elif strata == 'soc':
        soc(sheduler, SETTINGS['data'], **SETTINGS['headers'])

    elif strata == 'ifl':
        ifl(SETTINGS['data'], **SETTINGS['headers'])

    elif strata == 'auxiliary':
        auxiliary(SETTINGS['data'], **SETTINGS['headers'])

    else:
        gfc(sheduler, SETTINGS['data'], **SETTINGS['headers'])
        agb(sheduler, SETTINGS['data'], **SETTINGS['headers'])
        soc(sheduler, SETTINGS['data'], **SETTINGS['headers'])
        ifl(SETTINGS['dirs'], **SETTINGS['headers'])
        auxiliary(SETTINGS['data'], **SETTINGS['headers'])

    sheduler.quite()


if __name__ == '__main__':
    name, *args = argv
    main(*args)
