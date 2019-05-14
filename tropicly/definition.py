"""
definition
****

:Author: Tobias Seydewitz
:Date: 06.05.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
import logging
from sys import argv
from threading import Thread

import geopandas as gpd
import numpy as np
from rasterio import open as raster_open

from settings import SETTINGS
from sheduler import TaskSheduler
from sheduler import finish
from sheduler import progress

LOGGER = logging.getLogger(__name__)


def jaccard_index(arr1, arr2, return_matrix=False):
    """Computes the Jaccard Index for two binary matrices.

    The function computes the Jaccard Index (JI) of two equal sized matrices or vectors.
    If return_matrix is set to true the method provides the JI and the necessary
    calculation matrix as a 2x2 array.
    Equation:
    JI = a / (a + b + c)
    a := Similarity, both are true
    b := Difference, y is true and x is false
    c := Difference, x is true and y is false
    d := Difference, x and y are false

    Args:
        arr1 (list, ndarry): Value matrix should contain only binary values (1 and 0).
        arr2 (list, ndarry): Value matrix should contain only binary values (1 and 0).
        return_matrix (bool): If set to true function returns the JI and the coefficient matrix as a list.

    Returns:
        float or tuple(int, list): The JI or the JI and the coefficient matrix.
    """
    x, y = np.array(arr1, np.bool), np.array(arr2, np.bool)

    if x.shape != y.shape:
        raise ValueError

    a = x & y
    abc = x | y

    numerator = np.count_nonzero(a)
    denominator = np.count_nonzero(abc)

    jaccard = 0

    if denominator != 0:
        jaccard = numerator / denominator
        jaccard = np.round_(jaccard, 4)

    if return_matrix:
        b = x ^ a
        c = y ^ a
        d = np.logical_not(abc)

        matrix = [[numerator, np.count_nonzero(c)],
                  [np.count_nonzero(b), np.count_nonzero(d)]]

        return jaccard, matrix

    return jaccard


def treecover_agreement(gl30, gfc, cover_classes, canopy_densities):
    """ Computes the tree cover agreement between GL30 and GFC treecover strata.

    Computes the tree cover agreement between GL30 and GFC by applying the Jaccard Index.

    Args:
        gl30 (ndarry): GL30 strata as a numpy array.
        gfc (ndarry): GFC tree cover strata as numpy array.
        cover_classes (list, tuple): Values to consider as tree cover from GL30 strata.
        canopy_densities (list, tuple): Canopy densities to consider from GFC strata. Excludes all densities
            cd < x.

    Returns:
        list: Computed Jaccard Indexes as as list.

    Raises:
        ValueError: If the dimensionalty of GL30 and GFC strata differ.
    """
    if gl30.shape != gfc.shape:
        raise ValueError('Diverging image shapes.')

    gl30_binary = np.zeros(gl30.shape, dtype=np.uint8)
    gl30_binary[np.isin(gl30, cover_classes)] = 1

    values = []
    for density in canopy_densities:
        gfc_binary = np.zeros(gfc.shape, dtype=np.uint8)
        gfc_binary[gfc > density] = 1

        jc, _ = jaccard_index(gl30_binary, gfc_binary, return_matrix=True)
        values.append(jc)

        LOGGER.debug('JI%s matrix: %s', density, _)

    return values


def definition_worker(gl30, gfc, key, region, cover_classes, canopy_densities, out):
    """A simple worker function for parallelize tree cover agreement computation.

    Computes Jaccard Indexes for a GL30 and GFC strata set and writes results to
    out file.

    Args:
        gl30 (str): Path to GL30 strata.
        gfc (str): Path to GFC strata.
        key (str): Strata identifier.
        region (str): Strata region.
        cover_classes (list, tuple): Values to consider as tree cover from GL30 strata.
        canopy_densities (list, tuple): Canopy densities to consider from GFC strata.
        out (file): File handle to output file.
    """
    with raster_open(gl30, 'r') as handle1, raster_open(gfc, 'r') as handle2:
        gl30 = handle1.read(1)
        gfc = handle2.read(1)

    result = treecover_agreement(gl30, gfc, cover_classes, canopy_densities)

    out.write(','.join([key, region] + list(map(str, result))) + '\n')


def forest_definition(dirs, sheduler, cover_classes, canopy_densities, name):
    """Create the tree cover agreement analysis source data.

    Loads the GL30 and GFC strata from AISM and prepares a outut file
    for tree cover agreement output. The Jaccard Index results will be stored in ``/data/proc/fordef/``.

    Args:
        dirs (namedtuple): Namedtuple of path objects. Represents the data folder.
        sheduler (TaskSheduler): An instance of the TaskSheduler object for parallel computation.
        cover_classes (list, tuple): Values to consider as tree cover from GL30 strata.
        canopy_densities (list, tuple): Canopy densities to consider from GFC strata.
        name (str): Name of the out file.
    """
    aism = gpd.read_file(str(dirs.masks / 'aism.shp'))

    # prepare out file and write csv head
    out = open(str(dirs.fordef / name), 'a')
    out.write(
        ','.join(['key', 'region'] + list(map(lambda x: 'CD%s' % str(x), canopy_densities))) + '\n'
    )

    for _, row in aism.iterrows():
        sheduler.add_task(
            Thread(
                target=definition_worker,
                args=(dirs.aism / row.gl30_00, dirs.aism / row.cover, row.key,
                      row.region, cover_classes, canopy_densities, out)
            )
        )


def main(name, threads):
    """Entry point for forest definition.

    Computes tree cover agreement between GL30 and GFC. Results will be stored in
    ``/data/proc/fordef/``.

    Args:
        name (str): Name of the output file.
        threads (int): Number of threads to spawn for the download process.
    """
    sheduler = TaskSheduler('definition', int(threads))
    sheduler.on_progress.connect(progress)
    sheduler.on_finish.connect(finish)

    LOGGER.setLevel(logging.WARNING)
    handler = logging.FileHandler(str(SETTINGS['data'].log / 'definition.log'), mode='a')
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s: %(message)s')
    handler.setFormatter(formatter)
    LOGGER.addHandler(handler)

    forest_definition(SETTINGS['data'], sheduler, SETTINGS['cover_classes'], SETTINGS['canopy_densities'], name)

    sheduler.quite()


if __name__ == '__main__':
    _, *args = argv
    main(*args)
