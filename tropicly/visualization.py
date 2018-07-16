"""
visualization.py

Author: Tobias Seydewitz
Date: 12.07.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
from skimage import draw
from rasterio.windows import from_bounds
from shapely.affinity import affine_transform
from tropicly.grid import PolygonGrid, factory


# TODO let it work for multi band imgages
# TODO parallel
def visualization(img, grid_type='rec', width=1., height=1., fit=False):
    with rio.open(img, 'r') as src:
        invtransform = ~src.transform

        grid_polygon = factory(grid_type, width, height)
        img_polygon = affine_transform(grid_polygon, [invtransform.a, invtransform.b,
                                                      invtransform.d, invtransform.e,
                                                      invtransform.xoff, invtransform.yoff])

        grid = PolygonGrid(src.bounds, grid_polygon, fit=fit)

        for polygon in grid:
            window = from_bounds(*polygon.bounds, transform=src.transform)

            img = src.read(1, window=window)
            img = extract(img, img_polygon)

            yield img, polygon


# TODO set pixel outside of polygon by parameter
def extract(img, polygon):
    col, row = list(zip(*polygon.boundary.coords))
    fill_row_coords, fill_col_coords = draw.polygon(row, col, img.shape)

    mask = np.ones(img.shape, dtype=np.uint8)
    mask[fill_row_coords, fill_col_coords] = 0

    img[mask == 1] = 0

    return img


"""
Visualization

Receive a raster create a polygonal grid (of defined shape) over the extent.
Aggregate pixel values within each polygon with a defined method. Return the grid
as vector features (geometry is polygon, attributes defined by aggregation method)

Input:
- raster path
- grid polygon type
- grid polygon width/height
- aggregate function
- parallel execution
- number of threads

Output:
- vector layer

Features:
- must work in parallel

Process:
- open raster (in context manager)
- get raster bounds
- create grid with raster bounds, shape type, width, height
--- Potential parallel hook
- create raster read window from grid polygon
    - window = from_bounds(polygon, transform)
    - data = read(idx, window)
--- Potential parallel hook
- extract pixel within grid polygon
    - polygon must be transformed to image coords
    - need polygon and read frame
--- Potential parallel hook
- aggregate extracted pixel
    - aggregate function is user defined
    - parameters data, polygon
    - return geometry, aggregation as dictionary
"""
if __name__ == '__main__':
    import geopandas as gpd
    import pandas as pd
    path = '/home/tobi/Documents/Master/code/python/Master/tests/res/visual.tif'

    polys = []
    rec = []
    for img, poly in visualization(path, width=2, height=2, grid_type='rec', fit=True):
        polys.append(poly)
        ele, count = np.unique(img, return_counts=True)
        rec.append({str(val): count[idx] for idx, val in enumerate(ele)})

    df = gpd.GeoDataFrame(pd.DataFrame.from_records(rec), geometry=polys)
    df.to_file('/home/tobi/Documents/Master/code/python/Master/gridded.shp')
