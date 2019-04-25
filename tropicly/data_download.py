"""
data_download

Author: Tobias Seydewitz
Date: 24.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
import logging
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

    Citation: Hansen, M. C., P. V. Potapov, R. Moore, M. Hancher,
    S. A. Turubanova, A. Tyukavina, D. Thau, S. V. Stehman, S. J. Goetz,
    T. R. Loveland, A. Kommareddy, A. Egorov, L. Chini, C. O. Justice,
    and J. R. G. Townshend. 2013.
    “High-Resolution Global Maps of 21st-Century Forest Cover Change.”
    Science 342 (15 November): 850–53.

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
        lat_lon = re.search(r'(\d{2}\w_\d{3}\w)(?=\.tif)', url).groups()[0]
        lat = orientation_to_int(lat_lon.split('_')[0])

        if -20 <= lat <= 30:
            path = str(dirs.gfc / url.split('/')[-1])
            sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def agb(sheduler, dirs, **kwargs):
    """Downloads the required Above-ground Woody Biomass density (agb) stratum.

    Citation: Woods Hole Research Center. Unpublished data. Accessed through
    Global Forest Watch Climate on [date]. climate.globalforestwatch.org

    Args:
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel download.
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    head_url = 'https://gis-gfw.wri.org/arcgis/rest/services/climate/MapServer/1/query?where=1%3D1&outFields=*&outSR=4326&f=json'
    path = str(dirs.biomass / 'biomass.geojson')

    content = download(head_url)
    write_binary(content, path)

    biomass_mask = gpd.read_file(path)
    stratum_urls = list(biomass_mask.download)

    for url in stratum_urls:
        path = str(dirs.biomass / url.split('/')[-1])
        sheduler.add_task(Thread(target=download_worker, args=(url, path), kwargs=kwargs))


def soc(dirs, **kwargs):
    """Downloads the required Soil Organic Carbon Content (GSOCmap) stratum.

    Citation:

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    url = 'http://54.229.242.119/GSOCmap/downloads/GSOCmapV1.2.0.tif'

    content = download(url, **kwargs)
    write_binary(content, str(dirs.soil / 'GSOCmap.tif'))


def ifl(dirs, **kwargs):
    """Downloads the required Intact Forest Landscape (IFL) stratum.

    Citation: Potapov P., Yaroshenko A., Turubanova S., Dubinin M., Laestadius L.,
    Thies C., Aksenov D., Egorov A., Yesipova Y., Glushkov I., Karpachevskiy M.,
    Kostikova A., Manisha A., Tsybikova E., Zhuravleva I. 2008.
    Mapping the World's Intact Forest Landscapes by Remote Sensing. Ecology and Society, 13 (2)

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    url = 'http://intactforests.org/shp/IFL_2000.zip'

    content = download(url, **kwargs)
    write_binary(content, str(dirs.ifl / url.split('/')[-1]))

    zipfile.ZipFile(str(dirs.ifl / url.split('/')[-1])).extractall(str(dirs.ifl))
    os.remove(str(dirs.ifl / url.split('/')[-1]))


def auxiliary(dirs, **kwargs):
    """Downloads the required auxiliary strata.

    Citation: Tom Patterson and Nathaniel Vaughn Kelso, Natural Earth Data

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        **kwargs: Request headers (spoof User-Agent see global HEADERS variable)
    """
    urls = [
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip',
        'http://www.naturalearthdata.com/http//www.naturalearthdata.com/download/110m/cultural/ne_110m_admin_0_countries.zip'
    ]

    for url in urls:
        content = download(url, **kwargs)
        write_binary(content, str(dirs.auxiliary / url.split('/')[-1]))

        zipfile.ZipFile(str(dirs.auxiliary / url.split('/')[-1])).extractall(str(dirs.auxiliary))
        os.remove(str(dirs.auxiliary / url.split('/')[-1]))


def main(strata, threads):
    """Entry point for data download.

    Args:
        strata (str): one of gfc, agb, soc, ifl, auxiliary or else. Downloads the corresponding dataset strata. Please,
        refer to the equivalent named methods for dataset details.
        threads (int): Number of threads to spawn for the download process.
    """
    strata = strata.lower()

    sheduler = TaskSheduler('download', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    dirs = cache_directories(get_data_dir())

    LOGGER.setLevel(logging.WARNING)
    handler = logging.FileHandler(str(dirs.log / 'download.log'), mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    if strata == 'gfc':
        gfc(sheduler, dirs, **HEADERS)

    elif strata == 'agb':
        agb(sheduler, dirs, **HEADERS)

    elif strata == 'soc':
        soc(dirs, **HEADERS)

    elif strata == 'ifl':
        ifl(dirs, **HEADERS)

    elif strata == 'auxiliary':
        auxiliary(dirs, **HEADERS)

    else:
        gfc(sheduler, dirs, **HEADERS)
        agb(sheduler, dirs, **HEADERS)
        soc(dirs, **HEADERS)
        ifl(dirs, **HEADERS)
        auxiliary(dirs, **HEADERS)

    sheduler.quite()


if __name__ == '__main__':
    *_, args = argv
    main(*args)
