"""
**definition.py**

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
    """
    Calculates the Jaccard Index (JI) of two equal sized arrays or vectors.
    If return_matrix is set to true the method provides the JI and the necessary
    calculation matrix as a 2x2 array.
    Equation:
    JI = a / (a + b + c)
    a := Similarity, both are true
    b := Difference, y is true and x is false
    c := Difference, x is true and y is false
    d := Difference, x and y are false

    :param arr1: numpy.ndarray, list or tuple
    :param arr2: numpy.ndarray, list or tuple
        Both array alike objects sized in equal n x m (dimensions).
    :param return_matrix: boolean, optional
        A boolean value determining the return of the calculation matrix.
    :return: float OR (float, list)
        Default, the method returns only the JI if, return_matrix is set to true the
        method returns the JI and the coefficient matrix.
        [[a, b],
         [c, d]]
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


def treecover_similarity(gl30, gfc, cover_classes, canopy_densities):
    """
    Determines the tree cover agreement between a GlobaLand30 land cover and a Global Forest
    Change tree cover raster image.

    :param gl30: np.ndarray
    :param gfc: np.ndarray
        GL30 and GFC treecover image data.
    :param cover_classes: list or tuple of integer values
        GL30 land cover classes to interpret as forest.
    :param canopy_densities: list or tuple of integer values
        GFC treecover canopy densities to consider for
        analysis.
    :param compute_smc: boolean
        Compute simple matching coefficient as well. Default is false.
    :return: dictionary
        Computed values stored in a dictionary.
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
    with raster_open(gl30, 'r') as handle1, raster_open(gfc, 'r') as handle2:
        gl30 = handle1.read(1)
        gfc = handle2.read(1)

    result = treecover_similarity(gl30, gfc, cover_classes, canopy_densities)

    out.write(','.join([key, region] + list(map(str, result))) + '\n')


def forest_definition(dirs, sheduler, cover_classes, canopy_densities, name):
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
    """

    Args:
        name (str):
        threads (int):
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
    name, *args = argv
    main(*args)



