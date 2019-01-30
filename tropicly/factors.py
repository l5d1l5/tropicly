# TODO doc


class Coefficient:
    """
    A data object class stores some statistical properties.
    Used as coefficients to compute Ecosystem Service Values and
    Soil Organic Carbon changes.
    """
    def __init__(self, name, mean, std=None, med=None, mini=None, maxi=None):
        """
        Constructor

        :param name: str
            Identifier
        :param mean: numeric
        :param std: numeric, optional
            Standard deviation
        :param med: numeric, optional
            Median
        :param mini: numeric, optional
            Minimum, if std true and mini false equals
            mean - std
        :param maxi: numeric, optional
        """
        self.name = name
        self.mean = mean
        self.std = std
        self.median = med
        self._min = mini
        self._max = maxi

    @property
    def min(self):
        if self.std and not self._min:
            return self.mean - self.std

        else:
            return self._min

    @property
    def max(self):
        if self.std and not self._max:
            return self.mean + self.std

        else:
            return self._max

    def __repr__(self):
        return '<{}(name={}, mean={}) at {}>'.format(self.__class__.__name__, self.name,
                                                     self.mean, hex(id(self)))
