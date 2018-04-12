"""
classification.py

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
from rasterio.features import shapes
from shapely.geometry import Polygon
from .frequency import most_common_class


def assignment_worker(treecover, loss, gain, landcover, key, out_path, year=10, target_cover=10):
    # TODO doc, refactor
    handler = [
        read_raster(item)
        for item in [treecover, loss, gain, landcover]
    ]

    tree_arr, loss_arr, gain_arr, cover_arr = [
        item.read(1)
        for item in handler
    ]

    profile = fetch_metadata(handler[0], 'transform', 'crs', 'driver')

    [item.close() for item in handler]

    # prepare annual tree cover loss within a selected
    # tree cover class in a selected temporal resolution
    annual_loss = np.copy(loss_arr)
    np.place(annual_loss, annual_loss > year, 0)
    annual_loss[tree_arr <= target_cover] = 0

    # binary loss layer from annual tree cover loss
    binary_loss = np.zeros(annual_loss.shape, dtype=np.uint8)
    binary_loss[annual_loss != 0] = 1

    # tree cover gain within annual loss
    loss_gain = np.copy(gain_arr)
    loss_gain[annual_loss == 0] = 0

    # deforestation driver from 1 till year
    driver = binary_loss * cover_arr
    driver_gain = np.copy(driver)
    driver_gain[loss_gain == 1] = 25

    name = 'driver_{}.tif'.format(key)
    write(driver, str(out_path/name), driver=profile.driver,
          crs=profile.crs, compress='lzw', transform=profile.transform)

    name = 'driver_gain_{}.tif'.format(key)
    write(driver_gain, str(out_path/name), driver=profile.driver,
          crs=profile.crs, compress='lzw', transform=profile.transform)


def reclassification_worker(driver, out_path):
    # TODO doc, refactor
    handle = read_raster(driver)

    src_data = handle.read(1)
    transform = handle.transform

    reclassified = src_data.copy()

    mask = src_data == 20
    gen = rio.features.shapes(src_data, mask, transform=transform)

    reclass = []
    for geometry, _ in gen:
        polygon = Polygon(geometry['coordinates'][0])
        centroid = polygon.centroid
        row, col = handle.index(centroid.x, centroid.y)

        buffer = square_buffer(src_data, (row, col), 8)

        most_common = class_frequency(buffer, [0], default=20)

        if most_common != 20:
            reclass.append((geometry, most_common))

    if len(reclass) > 0:
        _ = rio.features.rasterize(reclass, out_shape=reclassified.shape,
                                   out=reclassified, transform=transform)

    handle.close()

    write(reclassified, str(out_path), transform=transform, driver='GTiff', compress='lzw',
          crs={'init': 'epsg:4326'})


def extract_square(data, center, block_size=None, side_lenght=None, res=None):
    if block_size:
        pass

    elif side_lenght and res:
        pass


# Statistic/Compute
def square_buffer(data, center, size):
    # TODO doc
    row, col = center
    max_row, max_col = data.shape

    half = int(size / 2)

    row_start = 0 if row - half < 0 else row - half
    row_end = max_row if row + half > max_row else row + half + 1
    col_start = 0 if col - half < 0 else col - half
    col_end = max_col if col + half > max_col else col + half + 1

    buffer = data[row_start:row_end, col_start:col_end]

    return buffer


def circle_mask(mask_size, center, radius):
    # TODO doc
    cx, cy = center
    sx, sy = mask_size

    y, x = np.ogrid[:sx, :sy]

    mask = (x-cx)**2 + (y-cy)**2 <= radius**2

    return mask