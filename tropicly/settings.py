"""
settings.py

Author: Tobias Seydewitz
Date: 25.04.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
from rasterio.crs import CRS

SETTINGS = {
    'headers': {'headers': {'User-Agent': "Mozilla/5.0 (X11; U; Linux i686) Gecko/20071127 Firefox/2.0.0.11"}},
    'wgs84': CRS.from_epsg(4326),
}
