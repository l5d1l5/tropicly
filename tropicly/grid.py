"""
grid.py

Author: Tobias Seydewitz
Date: 10.07.18
Mail: tobi.seyde@gmail.com
"""
from shapely.geometry import Polygon
from math import tan, atan, pi, sin, sqrt
from shapely.affinity import translate


# TODO tests
class PolygonGrid:
    """
    Creates a grid covering a raster image with a selected Polygon.
    """
    def __init__(self, grid_extent, grid_polygon, fit=False):
        """
        Class constructor.

        :param grid_extent: shapely.Polygon or tuple(left, bottom, right, top)
            Bounding box of the grid should be in crs coordinates.
            Grid extent provided as a polygon will use the polygon bounds
            as boundaries.
        :param grid_polygon: GridPolygon
            A GridPolygon instance.
        :param fit: boolean, optional
            Default is false. If set to true grid polygons are clipped to
            grid extent.
        """
        if isinstance(grid_extent, Polygon):
            self.left, self.bottom, self.right, self.top = grid_extent.bounds
            self.extent = grid_extent

        else:
            self.left, self.bottom, self.right, self.top = grid_extent
            self.extent = Polygon.from_bounds(*grid_extent)

        self.fit = fit

        self._poly = grid_polygon
        self._grid = []

    def _griddify(self):
        """
        Grid generator, yields a grid polygon per call.
        """
        y_start = self.bottom - self._poly.y_shift

        for row, y in enumerate(__class__.ticker(y_start, self.top, self._poly.y_spacing)):
            x_start = self.left - self._poly.x_shift if row % 2 == 0 else self.left

            for col, x in enumerate(__class__.ticker(x_start, self.right, self._poly.x_spacing)):
                translated = translate(self._poly, xoff=x, yoff=y)

                if self.fit:
                    # TODO if disjoint continue elif not within
                    if not translated.within(self.extent):
                        translated = translated.intersection(self.extent)
                        if translated.is_empty:
                            continue

                self._grid.append(translated)
                yield translated

    def __iter__(self):
        if self._grid:
            return self._grid.__iter__()
        else:
            return self._griddify()

    def __getitem__(self, item):
        return self._grid[item]

    def __len__(self):
        return len(self._grid)

    @staticmethod
    def ticker(start, stop, step):
        coord = start

        while coord < stop:
            yield coord
            coord += step


# TODO tests
class GridPolygon(Polygon):
    """
    Class instances are used for griding
    """
    def __init__(self, shell=None, holes=None, x_spacing=0.0, x_shift=0.0, y_spacing=0.0, y_shift=0.0):
        """
        No direct instantiation! Please use the class methods rectangular or hexagonal.
        """
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
        """
        Creates a rectangular shaped instance. Can be used for griding.

        :param width: int or float
            Width of the polygon as crs units.
        :param height: in or float
            Height of the polygon as crs units.
        :return: GridPolygon
            A  instance of GridPolygon
        """
        # create rectangular shaped polygon at
        # crs point of origin (0, 0, width, height)
        coords = [(0, 0), (width, 0),
                  (width, height), (0, height)]

        return cls(shell=coords, x_spacing=width, y_spacing=height)

    @classmethod
    def irregular_hexagon(cls, width, height):
        """
        Creates a hexagonal shaped instance. Can be used for griding.

        :param width: int or float
            Width of the hexagon as crs units.
        :param height: in or float
            Height of the hexagon as crs units.
        :return: GridPolygon
            A  instance of GridPolygon
        """
        a = atan(height / width) - pi / 12

        if a < 0:
            raise ValueError

        rx = width / 2
        ry = height / 2

        # create a fluent hexagonal shaped polygon at
        # crs bounds (0, 0, width, height)
        coords = [
            (0, -rx*tan(pi+a)+ry),
            (rx, 0),
            (2*rx, rx*tan(2*pi-a)+ry),
            (2*rx, rx*tan(a)+ry),
            (rx, 2*ry),
            (0, -rx*tan(pi-a)+ry)
        ]

        return cls(shell=coords, x_spacing=width, x_shift=rx,
                   y_spacing=coords[3][-1], y_shift=coords[0][-1])

    @classmethod
    def regular_hexagon(cls, **kwargs):
        """
        area,
        edge,
        ldiagonal
        sdiagonal
        :param kwargs:
        :return:
        """
        if len(kwargs) > 1:
            raise ValueError

        else:
            key = list(kwargs.keys())[0]
            arg = kwargs[key]

        R = {
            'area': lambda: sqrt(2*arg) / 27**(1/4),
            'edge': lambda: arg,
            'ldiagonal': lambda: arg/2,
            'sdiagonal': lambda: arg/sqrt(3),
        }.get(key, lambda: None)()

        assert R is not None

        cx = (R*sqrt(3))/2
        cy = R

        d = (2*R*sqrt(3))/2
        r = d/2

        # create a regular hexagonal shaped polygon at
        # crs bounds (0, 0, width, height)
        coords = [
            (0, R*sin(pi+pi/6)+cy),
            (cx, 0),
            (2*cx, R*sin(2*pi-pi/6)+cy),
            (2*cx, R*sin(pi/6)+cy),
            (cx, 2*R),
            (0, R*sin(pi-pi/6)+cy),
        ]

        return cls(shell=coords, x_spacing=d, x_shift=r,
                   y_spacing=coords[3][-1], y_shift=coords[0][-1])


class SegmentedHexagon:
    def __init__(self, hexagon):
        # geometric properties
        self.hexagon = hexagon
        self.x1, self.y1, self.x2, self.y2 = hexagon.bounds
        self.R = sqrt(2*hexagon.area) / 27**(1/4)

        self.ratio = 0
        self.current_split = None
        self.segments = []

    def segment(self, ration):
        pass
