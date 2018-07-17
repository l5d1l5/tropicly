"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import geopandas as gpd
from tropicly.grid import PolygonGrid, GridPolygon
from shapely.affinity import scale


poly = GridPolygon.hexagonal(2, 1.7)
grid = PolygonGrid((0, -10, 10, 0), poly)
geometry = list(grid)

df = gpd.GeoDataFrame(geometry=geometry)
df.crs = {'init': 'epsg:4326'}
df.to_file('/home/ilex/Documents/grid.shp')

geometry2 = [scale(i, xfact=0.8, yfact=0.8) for i in geometry]
df = gpd.GeoDataFrame(geometry=geometry2)
df.crs = {'init': 'epsg:4326'}
df.to_file('/home/ilex/Documents/grid2.shp')