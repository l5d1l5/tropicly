"""
frequency.py

Author: Tobias Seydewitz
Date: 10.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import rasterio as rio
from collections import OrderedDict


def worker():
    pass


def frequency(data):
    """

    :param data:
    :return:
    """
    if not np.issubdtype(data.dtype, np.integer):
        raise ValueError

    values, counts = np.unique(data, return_counts=True)

    pairs = [(key, val) for key, val in zip(values, counts)]

    return OrderedDict(pairs)


def most_common_class(data, exclude=(0, 255), default=20):
    """

    :param data:
    :param exclude:
    :param default:
    :return:
    """
    freq = frequency(data)

    freq = [
        item
        for item in freq.items()
        if item[0] not in exclude
    ]

    freq = sorted(
        freq,
        key=lambda item: item[1],
        reverse=True
    )

    if freq:
        try:
            return freq[0][0] if freq[0][0] != default else freq[1][0]

        except KeyError:
            return default

    return default
