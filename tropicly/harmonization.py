"""
Author: Tobias Seydewitz
Mail: tobi.seyde@gmail.com
"""
import logging
from collections import namedtuple

import numpy as np
from rasterio import open

LOGGER = logging.getLogger(__name__)


def worker(landcover, treecover, return_stack, *args, **kwargs):
    """
    Worker function for parallel execution.

    :param landcover: string
    :param treecover: string
        Path to landcover and treecover raster files.
    :param return_stack: queue or list
        Result will be added. Should provide
        a put or append method.
    :param args: any
        Additional parameters, will be added to result record.
    :param kwargs:
        Parameter for treecover_similarity function. Please consider function
        doc for detailed info.
    """
    with open(landcover, 'r') as handle1, open(treecover, 'r') as handle2:
        gl30 = handle1.read(1)
        gfc = handle2.read(1)

    result = treecover_similarity(gl30, gfc, **kwargs)

    for idx, val in enumerate(args):
        result['arg%s' % idx] = val

    if isinstance(return_stack, list):
        return_stack.append(result)

    else:
        return_stack.put(result)


def treecover_similarity(gl30, gfc, cover_class=(20,), canopy_density=(0, 10, 20, 30,), compute_smc=False):
    """
    Determines the tree cover agreement between a GlobaLand30 land cover and a Global Forest
    Change tree cover raster image.

    :param gl30: np.ndarray
    :param gfc: np.ndarray
        GL30 and GFC treecover image data.
    :param cover_class: list or tuple of integer values
        GL30 land cover classes to interpret as forest.
    :param canopy_density: list or tuple of integer values
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
    gl30_binary[np.isin(gl30, cover_class)] = 1

    values = {}
    for density in canopy_density:
        gfc_binary = np.zeros(gfc.shape, dtype=np.uint8)
        gfc_binary[gfc > density] = 1

        jc, _ = binary_jaccard(gl30_binary, gfc_binary, return_matrix=True)
        values['JI%s' % density] = jc

        LOGGER.debug('JI%s matrix: %s', density, _)

        if compute_smc:
            smc, _ = simple_matching_coefficient(gl30_binary, gfc_binary, return_matrix=True)
            values['SMC%s' % density] = smc

            LOGGER.debug('SMC%s matrix: %s', density, _)

    return values


def binary_jaccard(arr1, arr2, return_matrix=False):
    """
    Calculates the Jaccard Index (JI) of two equal sized arrays or vectors.
    If return_matrix is set to true the method provides the JI and the necessary
    calculation matrix as a 2x2 array.

    :param arr1: numpy.ndarray, list or tuple
    :param arr2: numpy.ndarray, list or tuple
        Both array alike objects sized in equal n x m (dimensions).
    :param return_matrix: boolean, optional
        A boolean value determining the return of the calculation matrix.
    :return: float OR (float, list)
        Default, the method returns only the JI if, return_matrix is set to true the
        method returns the JI and the computation matrix.
        [[a, b],
         [c, d]]
         a: total both images are true

    """
    x, y = np.array(arr1, np.bool), np.array(arr2, np.bool)

    if x.shape != y.shape:
        raise ValueError

    a = x & y
    abc = x | y
    b = x ^ a
    c = y ^ a
    d = np.logical_not(x) & np.logical_not(y)

    numerator = np.count_nonzero(a)
    denominator = np.count_nonzero(abc)

    if denominator == 0:
        jaccard = 0

    else:
        jaccard = numerator / denominator
        jaccard = np.round_(jaccard, 4)

    if return_matrix:
        matrix = [[numerator, np.count_nonzero(b)],
                  [np.count_nonzero(c), np.count_nonzero(d)]]

        return jaccard, matrix

    return jaccard


def simple_matching_coefficient(arr1, arr2, return_matrix=False):
    """
    Calculates the Simple Matching Coefficient (SMC) of two equal sized arrays or vectors.
    If return_matrix is set to true the method provides the SMC and the necessary calculation
    matrix as a named tuple.

    :param arr1: numpy.ndarray, list, tuple
    :param arr2: numpy.ndarray, list, tuple
        Both array alike objects sized in equal dimensions should contain exclusively
        binary data (1,0).
    :param return_matrix: boolean
        Optional, a boolean value determining the return of the calculation matrix.
    :return: float OR (float, namedtuple(m11, m01, m10, m00))
        Default, the method returns only the SMC, if return_matrix is
        set to true the method returns the SMC and the computation matrix.
        The Matrix contains the following attributes:
        m11 = total number of attributes where arr1 == 1 and arr2 == 1
        m10 = total number of attributes where arr1 == 1 and arr2 == 0
        m01 = total number of attributes where arr1 == 0 and arr2 == 1
        m00 = total number of attributes where arr1 == 0 and arr2 == 0
    """
    _, matrix = binary_jaccard(arr1, arr2, True)
    size = sum(matrix[0]) + sum(matrix[1])

    smc = (matrix[0][0] + matrix[1][1]) / size
    smc = np.round_(smc, 4)

    if return_matrix:
        return smc, matrix

    return smc
