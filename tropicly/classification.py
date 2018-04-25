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

from tropicly.distance import Distance
from tropicly.frequency import most_common_class
from tropicly.utils import write


# TODO refactor exceptions


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler)


def worker(landcover, treecover, gain, loss, filename,
           superimpose_kwargs=None, reclassify_kwargs=None, write_kwargs=None):
    """


    :param landcover:
    :param treecover:
    :param gain:
    :param loss:
    :param filename:
    :param superimpose_kwargs:
    :param reclassify_kwargs:
    :param write_kwargs:
    """
    # TODO refactor
    with rio.open(landcover, 'r') as h1, rio.open(treecover, 'r') as h2,\
            rio.open(gain, 'r') as h3, rio.open(loss, 'r') as h4:
        landcover_data = h1.read(1)
        treecover_data = h2.read(1)
        gain_data = h3.read(1)
        loss_data = h4.read(1)

        transform = h1.transform
        profile = h1.profile

    driver = superimpose(landcover_data, treecover_data, gain_data, loss_data,)

    reclassified = reclassify(driver, transform,)

    np.copyto(driver, reclassified, where=reclassified > 0)

    write(driver, filename, **profile)


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
    shape = [landcover.shape, treecover.shape, gain.shape, loss.shape]

    if len(set(shape)) > 1:
        raise ValueError

    shape = shape[0]

    tree_data = np.zeros(shape, dtype=np.uint8)
    tree_data[treecover > canopy_density] = 1

    loss_data = np.zeros(shape, dtype=np.uint8)
    loss_data[np.logical_and(tree_data == 1, np.isin(loss, years))] = 1

    gain_data = np.zeros(shape, dtype=np.uint8)
    gain_data[np.logical_and(loss_data == 1, gain == 1)] = 1

    driver = loss_data * landcover
    driver[gain_data == 1] = 25

    return driver


def reclassify(driver, affine, cluster_values=(20,), buffer_size=500):
    """


    :param driver:
    :param affine:
    :param cluster_values:
    :param buffer_size:
    :return:
    """
    # TODO distance calculation as parameter
    # TODO refactor algorithm should run only image coords provide res
    mask = np.isin(driver, cluster_values)
    haversine = Distance('hav')

    # x, y resolution
    x = haversine((affine.xoff, affine.yoff), (affine.xoff + affine.a, affine.yoff))
    y = haversine((affine.xoff, affine.yoff), (affine.xoff, affine.yoff + affine.e))

    LOGGER.debug('Pixel resolution (%s, %s)', x, y)

    to_reclassify = []
    for cluster, _ in rio.features.shapes(driver, mask=mask, transform=affine):
        polygon = Polygon(cluster['coordinates'][0])
        point = polygon.centroid

        # convert to image coordinates
        col, row = (point.x, point.y) * ~affine

        LOGGER.debug('Cluster centroid at (%s, %s)', col, row)

        buffer = extract_square(driver, center=(int(row), int(col)),
                                side_length=buffer_size, res=(x, y))

        LOGGER.debug('Buffer size (%s, %s)', buffer.shape[0], buffer.shape[1])

        new_class = most_common_class(buffer)

        if new_class not in cluster_values:
            to_reclassify.append((cluster, new_class))

    if to_reclassify:
        return rio.features.rasterize(to_reclassify, out_shape=driver.shape,
                                      transform=affine, dtype=np.uint8)

    return np.zeros(shape=driver.shape, dtype=np.uint8)


def reclass(driver, clustering=(20,), side_length=500, res=1, **kwargs):
    """
    Des

    :param driver:
    :param clustering:
    :param side_length:
    :param res:
    :param kwargs:
    :return:
    """
    mask = np.isin(driver, clustering)

    clusters = []
    for cluster, _ in rio.features.shapes(driver, mask=mask):
        polygon = Polygon(cluster['coordinates'][0])
        point = polygon.centroid
        center = int(point.y), int(point.x)

        buffer = extract_square(driver, center, side_length, res)
        cls = most_common_class(buffer, **kwargs)

        if cls not in clustering:
            clusters.append((cluster, cls))

    if clusters:
        return rio.features.rasterize(clusters, out_shape=driver.shape, dtype=driver.dtype)

    return np.zeros(shape=driver.shape, dtype=driver.dtype)


def extract_square(data, center, side_length=None, res=None):
    """
    Extracts a square around a center point from a numpy array.

    :param data: 2D np.array
        Square is extracted from this array.
    :param center: 2D tuple of int
        Center row and column coordinate of the square.
    :param side_length: int
        Side length in cell scaling or side length in real world
        distance.
    :param res: numeric or 2D tuple of int
        Real world resolution of the pixels. Must be in the same
        scaling as block length. Can be a single int or float for
        square sized pixels or a tuple of x and y length of the pixel.
    :return: np.array
        Numpy array in extent of side_length or block_length.
    """
    # TODO refactor to two functions extract square_by_block_size and by_side_length
    if side_length and res:
        if isinstance(res, (int, float)):
            x_res, y_res = res, res
        else:
            x_res, y_res = res

        # convert real world length to image length
        x_block_size = round(side_length / x_res)
        y_block_size = round(side_length / y_res)

        x_edge = round(0.5 * (x_block_size - 1))
        y_edge = round(0.5 * (y_block_size - 1))

    elif side_length:
        x_edge = int(0.5 * (side_length - 1))
        y_edge = int(0.5 * (side_length - 1))

    else:
        raise ValueError

    LOGGER.debug('Edge length (%s, %s)', x_edge, y_edge)

    row, col = center
    max_row, max_col = data.shape

    row_start = 0 if row - y_edge < 0 else row - y_edge
    row_end = max_row if row + y_edge > max_row else row + y_edge + 1

    col_start = 0 if col - x_edge < 0 else col - x_edge
    col_end = max_col if col + x_edge > max_col else col + x_edge + 1

    return data[row_start:row_end, col_start:col_end]


def circle_mask(mask_size, center, radius):
    # TODO implement properly
    cx, cy = center
    sx, sy = mask_size

    y, x = np.ogrid[:sx, :sy]

    mask = (x-cx)**2 + (y-cy)**2 <= radius**2

    return mask
