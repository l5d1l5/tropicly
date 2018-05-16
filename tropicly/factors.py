"""
factors.py

Author: Tobias Seydewitz
Date: 16.05.18
Mail: tobi.seyde@gmail.com
"""


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

    def __getitem__(self, key):
        if key in self._factors:
            return self._factors[key]

        raise KeyError('No item {}'.format(key))

    def get(self, key, default=None):
        return self._factors.get(key, default)

    @staticmethod
    def factor_factory(*args):
        if len(args) == 2:
            return Factor(*args)

        elif len(args) == 3:
            return SOCCFactor(*args)

        raise ValueError


class Factor:
    def __init__(self, alias, value):
        self.alias = alias
        self.value = value

    def __repr__(self):
        return '<{}(alias={}, value={}) at {}>'.format(self.__class__.__name__, self.alias,
                                                       self.value, hex(id(self)))


class SOCCFactor(Factor):
    def __init__(self, alias, mean, std):
        super().__init__(alias, mean)

        self.std = std  # standard deviation

    @property
    def min(self):
        return self.value - self.std

    @property
    def max(self):
        return self.value + self.std

    def __repr__(self):
        return '<{}(alias={}, mean={}, std={}) at {}>'.format(self.__class__.__name__, self.alias,
                                                              self.value, self.std, hex(id(self)))
