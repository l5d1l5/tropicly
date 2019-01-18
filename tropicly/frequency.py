from collections import OrderedDict

import numpy as np
from rasterio import open


# TODO refactor exceptions


def worker(image, return_stack, *args):
    """
    Worker function for parallel execution.

    :param image: string
        Path to raster image.
    :param return_stack: queue or list
        Result will be added. Should provide
        a put or append method.
    :param args:
        Additional parameters, will be added to result record.
    """
    with open(image, 'r') as src:
        data = src.read()

    freq = frequency(data)

    for idx, val in enumerate(args):
        freq['arg%s' % idx] = val

    if isinstance(return_stack, list):
        return_stack.append(freq)

    else:
        return_stack.put(freq)


def frequency(data):
    """
    Counts value/class frequency in a  integer numpy array.
    Counts are returned as a dictionary where value/class
    represents the key and value is the frequency. Sorted
    in ascending order.

    :param data: np.ndarray, integer
        A numpy integer array.
    :return: dictionary
        Key is value and value is frequency.
    """
    if not np.issubdtype(data.dtype, np.integer):
        raise ValueError

    values, counts = np.unique(data, return_counts=True)

    pairs = [(key, val) for key, val in zip(values, counts)]

    return OrderedDict(pairs)


def most_common_class(data, exclude=(0, 20, 255)):
    """
    Return the most common element in a numpy array. Omits
    elements from counting if they are in exclude. Returns
    none if no element is found.

    :param data: np.ndarray, integer
        A numpy integer array.
    :param exclude: list of integer
        Elements to exclude from counting.
    :return: int, int
         Most common value and its count.
    """
    freq = frequency(data)

    freq = [
        item
        for item in freq.items()
        if item[0] not in exclude
    ]

    LOGGER.debug('Classes: %s', freq)

    freq = sorted(
        freq,
        key=lambda item: item[1],
        reverse=True
    )

    if freq:
        return freq[0]

    return None
