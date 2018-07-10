"""
grid.py

Author: Tobias Seydewitz
Date: 10.07.18
Mail: tobi.seyde@gmail.com
"""

# bounds (left bottom right top)
class Polygon:
    v_spacing = 2
    h_spacing = 2


class Grid:
    def __init__(self, bounds, polygon, fit=False):
        self.left, self.bottom, self.right, self.top = bounds

        self.polygon = polygon
        self.fit = fit
        self.grid = []

    def x_gen(self):
        x_coord = self.left

        while x_coord < self.right:
            yield x_coord

            x_coord += self.polygon.v_spacing

    def y_gen(self):
        y_coord = self.top

        while y_coord > self.bottom:
            yield y_coord

            y_coord -= self.polygon.h_spacing

    def get(self):
        for y in self.y_gen():
            for x in self.x_gen():
                print(x, y)


if __name__ == '__main__':
    poly = Polygon()
    g = Grid((0,-10,10,0), poly)
    g.get()