"""
classification.py

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
import rasterio as rio
from rasterio.features import shapes
from shapely.geometry import Polygon

from .distance import Distance
from .frequency import most_common_class


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler)


def worker():
    pass


def superimpose(landcover, treecover, gain, loss, years=(1, 2, 3, 4, 5, 6, 7, 8, 9, 10), canopy_density=10):
    """
    Des

    :param landcover:
    :param treecover:
    :param gain:
    :param loss:
    :param years:
    :param canopy_density:
    :return:
    """
    shapes = [landcover.shape, treecover.shape, gain.shape, loss.shape]

    if len(set(shapes)) > 1:
        raise ValueError

    shape = shapes[0]

    tree_data = np.zeros(shape, dtype=np.uint8)
    tree_data[treecover > canopy_density] = 1

    gain_data = np.zeros(shape, dtype=np.uint8)
    gain_data[np.logical_and(tree_data == 1, gain == 1)] = 1

    loss_data = np.zeros(shape, dtype=np.uint8)
    loss_data[np.isin(loss, years)] = 1

    driver = loss_data * landcover
    driver[np.logical_and(gain == 1, driver > 0)] = 25

    return driver


def reclassify(driver, cluster_values=(20,), affine=None, buffer_size=500):
    """

    :param driver:
    :param cluster_values:
    :param affine:
    :param buffer_size:
    :return:
    """
    mask = np.isin(driver, cluster_values)
    haversine = Distance('hav')

    if affine:
        # x, y resolution
        x = haversine((affine.xoff, affine.yoff), (affine.xoff + affine.a, affine.yoff))
        y = haversine((affine.xoff, affine.yoff), (affine.xoff, affine.yoff + affine.e))

        clusters = rio.features.shapes(driver, mask=mask, transform=affine)

        kwargs = {'side_length': buffer_size, 'res': (x, y)}

    else:
        clusters = rio.features.shapes(driver, mask=mask)

        kwargs = {'block_size': buffer_size}

    to_reclassify = []
    for cluster, _ in clusters:
        polygon = Polygon(cluster['coordinates'][0])
        point = polygon.centroid
        x, y = point.x, point.y

        if affine:
            # convert to image coordinates
            x, y = (x, y) * ~affine

        buffer = extract_square(driver, (int(y), int(x)), **kwargs)

        new_class = most_common_class(buffer)

        if new_class not in cluster_values:
            to_reclassify.append((cluster, new_class))

    reclassified = None

    if len(to_reclassify) > 0:
        reclassified = rio.features.rasterize(to_reclassify, out_shape=driver.shape,
                                              transform=affine)

    return reclassified


def extract_square(data, center, block_size=None, side_length=None, res=None):
    """
    Des

    :param data:
    :param center:
    :param block_size:
    :param side_length:
    :param res:
    :return:
    """
    # TODO round might be a better idea
    if block_size:
        x_edge = int(0.5 * (block_size - 1))
        y_edge = int(0.5 * (block_size - 1))

    elif side_length and res:
        if isinstance(res, (int, float)):
            x_res, y_res = res, res
        else:
            x_res, y_res = res

        # convert real world length to image length
        x_block_size = int(side_length / x_res)
        y_block_size = int(side_length / y_res)

        x_edge = int(0.5 * (x_block_size - 1))
        y_edge = int(0.5 * (y_block_size - 1))

    else:
        raise ValueError

    row, col = center
    max_row, max_col = data.shape

    row_start = 0 if row - y_edge < 0 else row - y_edge
    row_end = max_row if row + y_edge > max_row else row + y_edge + 1

    col_start = 0 if col - x_edge < 0 else col - x_edge
    col_end = max_col if col + x_edge > max_col else col + x_edge + 1

    return data[row_start:row_end, col_start:col_end]


def circle_mask(mask_size, center, radius):
    # TODO implement properly
    """
    Des

    :param mask_size:
    :param center:
    :param radius:
    :return:
    """
    cx, cy = center
    sx, sy = mask_size

    y, x = np.ogrid[:sx, :sy]

    mask = (x-cx)**2 + (y-cy)**2 <= radius**2

    return mask