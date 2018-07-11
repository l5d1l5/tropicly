"""
grid.py

Author: Tobias Seydewitz
Date: 10.07.18
Mail: tobi.seyde@gmail.com
"""
from math import tan, atan, pi
from shapely.geometry import Polygon
from shapely.affinity import translate

# TODO tests
# TODO implement iterator protocol
class PolygonGrid:
    def __init__(self, extent, polygon, fit=False):
        if isinstance(extent, Polygon):
            self.left, self.bottom, self.right, self.top = extent.bounds
            self.extent = extent

        else:
            self.left, self.bottom, self.right, self.top = extent
            self.extent = Polygon.from_bounds(*extent)

        self.poly = polygon

        self.fit = fit
        self.grid = []

    def get(self):
        y_start = self.bottom - self.poly.y_shift

        for row, y in enumerate(__class__.ticker(y_start, self.top, self.poly.y_spacing)):
            x_start = self.left - self.poly.x_shift if row % 2 == 0 else self.left

            for col, x in enumerate(__class__.ticker(x_start, self.right, self.poly.x_spacing)):
                translated = translate(self.poly, xoff=x, yoff=y)

                if self.fit:
                    if not translated.within(self.extent):
                        translated = translated.intersection(self.extent)

                self.grid.append(translated)
                yield translated

    def __getitem__(self, item):
        return self.grid[item]

    def __len__(self):
        return len(self.grid)

    @staticmethod
    def ticker(start, stop, step):
        coord = start

        while coord < stop:
            yield coord
            coord += step


class GridPolygon(Polygon):
    def __init__(self, shell=None, holes=None, x_spacing=0.0, x_shift=0.0, y_spacing=0.0, y_shift=0.0):
        super().__init__(shell, holes)

        self.x_spacing = x_spacing
        self.x_shift = x_shift
        self.y_spacing = y_spacing
        self.y_shift = y_shift

    @property
    def coords(self):
        return super().coords

    @property
    def xy(self):
        return super().xy

    @property
    def __array_interface__(self):
        return super().__array_interface__

    def _get_coords(self):
        return super()._get_coords()

    def _set_coords(self, ob):
        super()._set_coords(ob)

    @classmethod
    def rectangular(cls, width, height):
        coords = [(0, 0), (width, 0),
                  (width, height), (0, height)]

        return cls(shell=coords, x_spacing=width, y_spacing=height)

    @classmethod
    def hexagonal(cls, width, height):
        a = atan(height / width) - pi / 12

        if a < 0:
            raise ValueError

        rx = width / 2
        ry = height / 2

        coords = [(0, -rx*tan(pi+a)+ry), (rx, 0),
                  (2*rx, rx*tan(2*pi-a)+ry), (2*rx, rx*tan(a)+ry),
                  (rx, 2*ry), (0, -rx*tan(pi-a)+ry)]

        return cls(shell=coords, x_spacing=width, x_shift=rx,
                   y_spacing=rx*tan(a)+ry, y_shift=-rx*tan(pi+a)+ry)


if __name__ == '__main__':
    import geopandas as gpd
    poly = GridPolygon.hexagonal(1.7, 2)
    grid = PolygonGrid((-29.9999992, -25.000061138681087, 60.00010940962595, 24.9999992), poly, True)
    list(grid.get())

    df = gpd.GeoDataFrame(geometry=grid.grid)
    df.crs = {'init': 'epsg:4326'}
    df.to_file('/home/tobi/Documents/grid.shp')
    #poly = HexagonalGridPolygon(20, 20)

