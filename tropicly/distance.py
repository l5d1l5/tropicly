"""
distance.py

Author: Tobias Seydewitz
Date: 12.04.18
Mail: tobi.seyde@gmail.com
"""
from math import (sin,
                  cos,
                  asin,
                  sqrt,
                  radians,)


class Distance:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)


def haversine(coord1, coord2, scale='m'):
    """
    Computes the haversine distance between two points and returns
    it in meter.

    :param coord1: tuple or list
        X- and Y-coordinate of the first location.
    :param coord2: tuple or list
        X- and Y-coordinate of
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


def euclidean():
    pass
