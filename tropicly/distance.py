from math import asin
from math import cos
from math import radians
from math import sin
from math import sqrt


# TODO exceptions
#  doc

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
        'cm': lambda: haversine_dist * 100,
        'm': lambda: haversine_dist,
        'km': lambda: haversine_dist * 0.001,
    }
    earth_radius = 6378137  # in meter

    px, py = map(radians, coord1)
    qx, qy = map(radians, coord2)

    term1 = (py - qy) * 0.5
    term2 = (px - qx) * 0.5
    term3 = sin(term1)**2 + cos(py) * cos(qy) * sin(term2)**2

    haversine_dist = 2 * earth_radius * asin(sqrt(term3))

    return scales.get(scale, haversine_dist)()


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
            haversine or hav
            euclidean or euc
        """
        self.func = __class__.ALGORITHMS.get(algorithm, None)

        if not self.func:
            raise ValueError

        self.__class__.__doc__ = self.func.__doc__

    def _validate_args(self, *args, **kwargs):
        if len(args) != 2:
            return False

        elif len(args[0]) != len(args[1]):
            return False

        elif self.func.__name__ != 'haversine' and len(args[0]) > 2 and len(args[1]) > 2:
            return False

        # TODO check kwargs with from inspect import Signature

        return True

    def __call__(self, *args, **kwargs):
        if self._validate_args(*args):
            return self.func(*args, **kwargs)

        raise ValueError

    def __repr__(self):
        return '<Distance({}) at {}>'.format(self.func.__name__, hex(id(self)))
