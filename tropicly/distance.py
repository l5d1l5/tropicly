"""
distance.py

Author: Tobias Seydewitz
Date: 12.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
from math import (sin,
                  cos,
                  asin,
                  sqrt,
                  radians,)


# TODO refactor exceptions


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler)


def haversine(coord1, coord2, scale='m'):
    """
    Computes the haversine distance between two points and returns
    it in meter.

    :param coord1: tuple or list
        X- and Y-coordinate of the first location.
    :param coord2: tuple or list
        X- and Y-coordinate of the second location.
    :param scale: string, optional
        Distance scale default is meter.
        Possible values: cm, km
    :return: numeric
        Distance between the two points in requested
        scaling.
    """
    scales = {
        'cm': lambda d: d * 100,
        'km': lambda d: d * 0.001,
    }
    earth_radius = 6378137  # in meter

    px, py = map(radians, coord1)
    qx, qy = map(radians, coord2)

    term1 = (py - qy) * 0.5
    term2 = (px - qx) * 0.5
    term3 = sin(term1)**2 + cos(py) * cos(qy) * sin(term2)**2

    haversine_dist = 2 * earth_radius * asin(sqrt(term3))

    return scales.get(scale, haversine_dist)(haversine_dist)


def euclidean(coord1, coord2):
    """
    Computes the euclidean distance between two points.

    :param coord1: tuple or list
        X- and Y-coordinate of the first location.
    :param coord2: tuple or list
        X- and Y-coordinate of the first location.
    :return:
    """
    px, py = coord1
    qx, qy = coord2

    term1 = (px - qx)**2
    term2 = (py - qy)**2

    euclidean_dist = sqrt(term1 + term2)

    return euclidean_dist


class Distance:
    """
    Wrapper classes for different distance algorithms.
    Select at instantiation the required distance algorithm.

    Example:
    haversine = Distance('haversine')
    haversine((0, 0), (1, 1))
    """
    ALGORITHMS = {
        'haversine': haversine,
        'euclidean': euclidean,
        'hav': haversine,
        'euc': euclidean,
    }

    def __init__(self, algorithm):
        """
        :param algorithm: string
            Possible arguments:
            haversine, hav
            euclidean, euc
        """
        self.func = __class__.ALGORITHMS.get(algorithm, None)

        if not self.func:
            raise ValueError

        self.__class__.__doc__ = self.func.__doc__

    def validate_args(self, *args):
        # TODO implement, two coords, length of coords is two, special case euclidean
        pass

    def __call__(self, *args, **kwargs):
        if self.validate_args(*args):
            return self.func(*args, **kwargs)

        raise ValueError

    def __repr__(self):
        return '<Distance({}) at {}>'.format(self.func.__name__, hex(id(self)))