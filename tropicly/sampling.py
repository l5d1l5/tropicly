"""
sampling.py

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
import rasterio as rio


# TODO refactor exceptions


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


def worker(image, return_stack, **kwargs):
    """
    Worker function for parallel sampling.

    :param image: string
        Path to raster image.
    :param return_stack: container object
        Result will be added to container object. Should provide
        a put method.
    :param kwargs: optional
        Parameter for sample_occupied. Please, consider the doc of this function
        for detailed instructions.
    """
    with rio.open(image, 'r') as src:
        data = src.read(1)
        affine = src.transform

    samples = sample_occupied(data, affine=affine, **kwargs)

    return_stack.put(samples)


def sample_occupied(data, samples=100, occupied=None, affine=None, seed=None):
    """
    A function to draw random samples from a 2D numpy array. A default call
    of this function draws 100 samples where the cell value is greater or lower
    than zero. If occupied is provided as a parameter only the values selected
    by occupied will be drawn as samples.

    :param data: np.ndarray
        A two dimensional numpy array.
    :param samples: int
        Total number of samples to draw from array.
        Default is 100 samples.
    :param occupied: list of int, optional
        Values to consider for sampling.
    :param affine: Affine, optional
        Affine matrix to convert image coordinates to real world
        coordinates. Must be an affine object.
    :param seed: int, str, optional
        Seed for random number generator.
    :return: list of dictionaries
        Each sample is a dictionary with the following keys:
        label: cell value
        row: image coordinate
        col: image coordinate
        x: real world coordinate or none
        y: real world coordinate or none
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


def draw_sample(data, samples=None, seed=None):
    """
    Generator function to draw a random sample from a list
    of values. If samples is omitted as a parameter the function
    draw from list until it is empty.

    :param data: list
        Sampling list, function draw samples from this list.
    :param samples: int, optional
        Total number of samples to draw from list until the
        function returns.
    :param seed: int, str, optional
        Seed for random number generator.
    :return:
        A randomly selected list value.
    """
    random = np.random.RandomState(seed)

    c = 0
    while data:
        idx = random.randint(len(data))
        yield data.pop(idx)

        c += 1

        if samples and samples == c:
            return
