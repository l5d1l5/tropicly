"""
harmonization.py

Author: Tobias Seydewitz
Date: 06.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
from collections import namedtuple


# TODO documentation, refactor exceptions


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def worker(landcover, treecover, return_stack, **kwargs):
    """
    Description

    :param landcover:
    :param treecover:
    :param return_stack:
    :param kwargs:
    :return:
    """
    pass


def treecover_similarity(gl30, gfc, cover_class=(20,), canopy_density=(0, 10, 20, 30,), compute_smc=False):
    """
    Description

    :param gl30: np.ndarray
    :param gfc: np.ndarray
        Description
    :param cover_class: list or tuple of numeric values
        Description
    :param canopy_density: list or tuple of numeric values
        Description
    :param compute_smc: boolean
        Description
    :return: dictionary
        Description
    """
    if gl30.shape != gfc.shape:
        raise ValueError('Diverging image shapes.')

    gl30_binary = np.zeros(gl30.shape, dtype=np.uint8)
    gl30_binary[np.isin(gl30, cover_class)] = 1

    values = {}
    for density in canopy_density:
        gfc_binary = np.zeros(gfc.shape, dtype=np.uint8)
        gfc_binary[gfc > density] = 1

        jc = binary_jaccard(gl30_binary, gfc_binary)
        values['JC%s' % density] = jc

        if compute_smc:
            smc = simple_matching_coefficient(gl30_binary, gfc_binary)
            values['SMC%s' % density] = smc

    return values


def binary_jaccard(arr1, arr2, return_matrix=False):
    """
    Calculates the Jaccard Index (JI) of two equal sized binary arrays or vectors.
    If return_matrix is set to true the method provides the JI and the necessary
    calculation matrix as a named tuple. Attention, this method does not work in-place!

    :param arr1: numpy.ndarray, list or tuple
    :param arr2: numpy.ndarray, list or tuple
        Both array alike objects sized in equal dimensions should contain exclusively
        binary data (1,0).
    :param return_matrix: boolean
        Optional, a boolean value determining the return of the calculation matrix.
    :return: float OR (float, namedtuple(m11, m01, m10, m00))
        Default, the method returns only the JI if, return_matrix is set to true the
        method returns the JI and the computation matrix.
        The Matrix contains the following attributes:
        m11 = total number of attributes where arr1 == 1 and arr2 == 1
        m10 = total number of attributes where arr1 == 1 and arr2 == 0
        m01 = total number of attributes where arr1 == 0 and arr2 == 1
        m00 = not required, set to 0
    """
    a, b = np.array(arr1, dtype=np.int8), np.array(arr2, dtype=np.int8)

    if np.sum(np.logical_or(a < 0, a > 1)) != 0 or np.sum(np.logical_or(b < 0, b > 1)) != 0:
        raise ValueError('Attributes should contain only binary values')

    c = a + b
    a = (b - c) + b  # a = (a - C) + a, m10 = a == 1
    b = (a - c) + a  # b = (b - C) + b, m01 = b == 1

    # Total number of attributes where a == 1 and b == 1
    m11 = np.sum(c == 2)
    # Total number of attributes where a == 1 and b == 0
    m10 = np.sum(a == -1)
    # Total number of attributes where a == 0 and b == 1
    m01 = np.sum(b == -1)

    denominator = (m10 + m01 + m11)

    if denominator == 0:
        jaccard = 0

    else:
        jaccard = m11 / denominator

    if return_matrix:
        Matrix = namedtuple('Matrix', 'm11 m10 m01 m00')
        return jaccard, Matrix(m11, m10, m01, 0)

    return jaccard


def simple_matching_coefficient(arr1, arr2, return_matrix=False):
    """
    Calculates the Simple Matching Coefficient (SMC) of two equal sized arrays or vectors.
    If return_matrix is set to true the method provides the SMC and the necessary calculation
    matrix as a named tuple. Attention, this method does not work in-place!

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
    a = np.array(arr1, dtype=np.int8)

    # Total number of attributes where a == 0 and b == 0
    m00 = a.size - sum(matrix)

    smc = (matrix.m11 + m00) / a.size

    if return_matrix:
        matrix = matrix._replace(m00=m00)
        return smc, matrix

    return smc
