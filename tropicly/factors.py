"""
factors.py

Author: Tobias Seydewitz
Date: 16.05.18
Mail: tobi.seyde@gmail.com
"""
from enum import Enum
from collections import namedtuple


class Factors:
    def __init__(self, name, *args):
        self.name = name
        self._factors = {}

        if args:
            self.add_factors(*args)

    def add_factors(self, *args):
        for arg in args:
            if not isinstance(arg, Factor):
                arg = self.__class__.factor_factory(*arg)

            self._factors[arg.alias] = arg

    def __getitem__(self, item):
        if item in self._factors:
            return self._factors[item]

        raise KeyError('No item {}'.format(item))

    @staticmethod
    def factor_factory(*args):
        if len(args) == 1:
            return Factor(*args)

        elif len(args) == 3:
            return SOCCFactor(*args)

        raise ValueError


class Factor:
    def __init__(self, alias):
        self.alias = alias


class SOCCFactor(Factor):
    def __init__(self, alias, mean, std):
        super().__init__(alias)

        self.mean = mean
        self.std = std  # standard deviation

    @property
    def min(self):
        return self.mean - self.std

    @property
    def max(self):
        return self.mean + self.std

    def __repr__(self):
        return '<{}({}, {}, {}) at {}>'.format(self.__class__.__name__, self.alias,
                                               self.mean, self.std, hex(id(self)))


class SOCClasses(Enum):
    primary_forest = 0
    secondary_forest = 1
    grassland = 2
    perennial_crops = 3


ChangeType = namedtuple('ChangeType', 'from_ to')


SOCC = [
    (ChangeType(SOCClasses.primary_forest, SOCClasses.grassland), 0.121, 0.023),
]


if __name__ == '__main__':
    f = Factors('name', *SOCC)
    c = ChangeType(SOCClasses.primary_forest, SOCClasses.grassland)
    print(f[c])