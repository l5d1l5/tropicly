"""
cell.py

Author: Tobias Seydewitz
Date: 22.03.18
Mail: tobi.seyde@gmail.com
"""


class Cell:
    __slots__ = 'x', 'y', 'value'

    def __init__(self, x, y, value):
        self.x = x
        self.y = y
        self.value = value

    @property
    def row(self):
        return self.y

    @property
    def col(self):
        return self.x

    def __repr__(self):
        return '<Cell({}, {}, {}) at {}>'.format(self.x, self.y, self.value, hex(id(self)))
