"""
sampling.py

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np


# TODO refactor exceptions, maybe src_nodata=0


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def worker():
    pass


def sample_occupied(data, samples=100, occupied=None, affine=None, seed=42):
    """
    Description

    :param data:
    :param samples:
    :param occupied:
    :param affine:
    :param seed:
    :return:
    """
    if len(data.shape) != 2:
        raise ValueError

    mask = np.zeros(data.shape, dtype=np.uint8)

    if occupied:
        mask[np.isin(data, occupied)] = 1

    else:
        mask[np.logical_or(data > 0, data < 0)] = 1

    cells = list(zip(*np.nonzero(mask)))

    records = []
    for sample in draw_sample(cells, samples, seed):
        row, col = sample
        x, y = None, None

        if affine:
            x, y = (col, row) * affine

        record = {'label': data[row][col],
                  'row': row,
                  'col': col,
                  'x': x,
                  'y': y, }

        records.append(record)

    return records


def draw_sample(data, samples=100, seed=None):
    random = np.random.RandomState(seed)

    for i in range(samples):
        idx = random.randint(len(data))

        yield data.pop(idx)

        if not data:
            return
