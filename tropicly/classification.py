"""
classification
**************

:Author: Tobias Seydewitz
:Date: 14.05.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import logging
import sys
from multiprocessing import Process

import geopandas as gpd
import numpy as np
from rasterio import open
from rasterio.features import rasterize
from rasterio.features import shapes
from shapely.geometry import Polygon

from distance import Distance
from frequency import most_common_class
from raster import write
from settings import SETTINGS
from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress

LOGGER = logging.getLogger(__name__)


def extract_square(data, center, side_length=None, res=None):
    """Extracts a square from a numpy array around a center point.

    Args:
        data (ndarray): A 2D numpy array. Square is extracted from this array.
        center (tuple(int, int)): Center coordinate of the square.
        side_length (int): Side length in cell scaling or side length in real world distance.
        res (float or tuple(float, float)): Real world resolution of the cells.

    Returns:
        ndarray: The extracted square.
    """
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


def reclassify(driver, clustering=SETTINGS['clustering'],
               reject=SETTINGS['reject'], side_length=SETTINGS['buffer'], res=(1, 1)):
    """Reclassify pixels in proximate deforestation stratum.

    Approach: Cluster pixels with values ``clustering``; create square sized buffer around the cluster center;
    count most frequent class within the buffer by exclusion of ``reject``; reassign cluster to most frequent class

    Args:
        driver (ndarray): Proximate deforestation driver stratum.
        clustering (list(int): Values to cluster.
        reject (list(int): Values to reject for reclassification.
        side_length (int): Edge length of the buffer.
        res(int or tuple(int, int)): Cell size.

    Returns:
        ndarray: The reclassified stratum.
    """

    mask = np.isin(driver, clustering)

    clusters = []
    for cluster, _ in shapes(driver, mask=mask):
        polygon = Polygon(cluster['coordinates'][0])
        point = polygon.centroid
        center = int(point.y), int(point.x)

        LOGGER.debug('Cluster centroid at (%s, %s)', int(point.x), int(point.y))

        buffer = extract_square(driver, center, side_length, res)

        LOGGER.debug('Buffer size (%s, %s)', buffer.shape[0], buffer.shape[1])

        mc = most_common_class(buffer, reject)

        if mc:
            cls, count = mc
            clusters.append((cluster, cls))

    if clusters:
        return rasterize(clusters, out_shape=driver.shape, dtype=driver.dtype)

    return np.zeros(shape=driver.shape, dtype=driver.dtype)


def superimpose(gl30, gfc_treecover, gfc_gain, gfc_loss,
                years=SETTINGS['classify_years'], canopy_density=SETTINGS['canopy_density']):
    """Classify proximate deforestation driver.

    Determines the proximate drivers of deforestation. Superimposes GL30 with
    filtered GFC annual losses.

    Args:
        gl30 (ndarray): GlobeLAnd30 stratum
        gfc_treecover (ndarray): Global Forest Change treecover 2000 stratum
        gfc_gain (ndarray): Global Forest Change treecover 2000 gain stratum
        gfc_loss (ndarray): Global Forest Change treecover 2000 loss stratum
        years (list(int)): Forest loss years to consider
        canopy_density (list(int)): Canopy densities to consider

    Returns:
        ndarray: Forest loss classified by proximate deforestation driver.
    """
    shape = [gl30.shape, gfc_treecover.shape, gfc_gain.shape, gfc_loss.shape]

    if len(set(shape)) > 1:
        raise ValueError('Diverging shape of the strata')

    losses = (gfc_treecover > canopy_density) & np.isin(gfc_loss, years)

    driver = losses * gl30
    driver[(losses & gfc_gain) == 1] = 25

    return driver


def classification_worker(gl30, gfc_treecover, gfc_gain, gfc_loss, out_name, distance='hav'):
    """Worker for parallel execution of the proximate deforestation driver classification.

    Args:
        gl30 (str or Path): Path to GlobeLAnd30 stratum
        gfc_treecover (str or Path): Path to Global Forest Change treecover 2000 stratum
        gfc_gain (str or Path): Path to Global Forest Change treecover 2000 gain stratum
        gfc_loss (str or Path): Path to Global Forest Change treecover 2000 loss stratum
        out_name (str of Path): Store stratum under this path with this name
        distance (str): Algorithm to use for pixel resolution computation
    """
    with open(gl30, 'r') as h1, open(gfc_treecover, 'r') as h2,\
            open(gfc_gain, 'r') as h3, open(gfc_loss, 'r') as h4:

        landcover_data = h1.read(1)
        treecover_data = h2.read(1)
        gain_data = h3.read(1)
        loss_data = h4.read(1)

        transform = h1.transform
        profile = h1.profile

    # compute cell size for this tile
    haversine = Distance(distance)
    x = haversine((transform.xoff, transform.yoff), (transform.xoff + transform.a, transform.yoff))
    y = haversine((transform.xoff, transform.yoff), (transform.xoff, transform.yoff + transform.e))

    try:
        driver = superimpose(landcover_data, treecover_data, gain_data, loss_data)

        reclassified = reclassify(driver, res=(x, y))

        np.copyto(driver, reclassified, where=reclassified > 0)

        write(driver, out_name, **profile)

    except ValueError as err:
        LOGGER.error('Strata %s error %s', out_name, str(err))


def classify(dirs, sheduler):
    """Perform proximate driver classification

    Prerequisites are the aism mask and the aism strata.
    Proximate deforestation driver strata will be stored in ``/data/proc/driver``.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel alignment.
    """
    aism = gpd.read_file(str(dirs.masks / 'aism.shp'))

    for idx, row in aism.iterrows():
        gl30 = dirs.aism / row.gl30_10
        gfc_treecover = dirs.aism / row.cover
        gfc_gain = dirs.aism / row.gain
        gfc_loss = dirs.aism / row.loss

        out_name = dirs.driver / 'driver_{}.tif'.format(row.key)

        # use of multiprocessing because we do a lot of computation within a python instance
        sheduler.add_task(
            Process(target=classification_worker, args=(gl30, gfc_treecover, gfc_gain, gfc_loss, out_name))
        )


def main(threads):
    """Entry point for proximate deforestation driver classification to create the Aligned Image Stack Mosaic (AISM).
    Args:
        threads (int): number of threads to spawn for the alignment or clean process.
    """
    sheduler = TaskSheduler('classification', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    LOGGER.setLevel(logging.WARNING)
    handler = logging.FileHandler(str(SETTINGS['data'].log / 'classification.log'), mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    classify(SETTINGS['data'], sheduler)

    sheduler.quite()


if __name__ == '__main__':
    _, *args = sys.argv
    main(*args)
