"""
grid.py

Author: Tobias Seydewitz
Date: 10.07.18
Mail: tobi.seyde@gmail.com
"""
from math import tan, atan, pi, sin, sqrt
from shapely.affinity import translate
from shapely.geometry import Polygon, LineString
from shapely.ops import linemerge, polygonize, unary_union


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


# TODO tests
class SegmentedHexagon:
    def __init__(self, hexagon):
        self._ratio = 0
        self.hexagon = hexagon
        self.top_segment = None  # remaining hexagon
        self.bottom_segments = []  # stores all hexagon segments

        # geometric properties
        self.x1, self.y1, self.x2, self.y2 = hexagon.bounds
        self.R = sqrt(2*hexagon.area) / 27**(1/4)  # hexagon circumscribed circle radius

        # analytic properties
        # function intervals
        self.interval1 = self.y1
        self.interval2 = self.y1 + self.R * sin(pi - pi / 6)
        self.interval3 = self.y1 + self.R * (sin(pi - pi / 6) + 1)
        self.interval4 = self.y2

        self.slope = 1/tan(pi/6)
        self.intercept = self.x1 + (self.x2-self.x1)/2

    def get_segment(self, ratio):
        assert (self._ratio + ratio) <= 100  # more than 100%
        assert ratio > 0  # no negative ratio allowed

        self._ratio += ratio

        if self._ratio == 100:
            top = None
            bottom = self.hexagon if self.top_segment is None else self.top_segment

        elif self.top_segment:
            top, bottom = self._split_polygon(self.top_segment, self._split_line())

        else:
            top, bottom = self._split_polygon(self.hexagon, self._split_line())

        self.top_segment = top
        self.bottom_segments.append({'segment': bottom, 'ratio': ratio})

        return bottom

    def _split_line(self):
        x = ((self._ratio * (self.y2 - self.y1)) / 100) + self.y1

        assert self.interval1 <= x <= self.interval4

        if self.interval1 <= x < self.interval2:
            slope = x - self.y1
            yl = -(slope * self.slope) + self.intercept
            yr = slope * self.slope + self.intercept

        elif self.interval2 <= x < self.interval3:
            yl = self.x1
            yr = self.x2

        else:
            slope = x - self.y2
            yl = slope * self.slope + self.intercept
            yr = -(slope * self.slope) + self.intercept

        return [(yl, x), (yr, x)]

    def _split_polygon(self, polygon, split_line):
        # TODO refactor to one loop
        previous = list(polygon.boundary.coords)[0]
        coords = [previous]
        previous_loc = __class__.point_orientation(split_line, previous)

        # add intersection coords to hexagon coords
        for point in list(polygon.boundary.coords)[1:]:
            current_loc = __class__.point_orientation(split_line, point)

            if current_loc != previous_loc:
                mid = (previous[0]+point[0])/2
                intersection = split_line[0] if mid < self.intercept else split_line[1]  # left or right intersection
                coords.append(intersection)

            previous = point
            previous_loc = current_loc
            coords.append(point)

        top_polygon = []
        bottom_polygon = []
        for point in coords:
            loc = __class__.point_orientation(split_line, point)

            if loc == 1:
                top_polygon.append(point)
            elif loc == -1:
                bottom_polygon.append(point)
            else:
                top_polygon.append(point)
                bottom_polygon.append(point)

        return Polygon(top_polygon), Polygon(bottom_polygon)

    @staticmethod
    def point_orientation(line, point):
        if line[0][0] == line[1][0]:  # vertical line
            y_line = line[0][0]
            y_point = point[0]

        elif line[0][1] == line[1][1]:  # horizontal line
            y_line = line[0][1]
            y_point = point[1]

        else:
            y_line = ((line[1][1]-line[0][1])/(line[1][0]-line[0][0])) * (point[0]-line[0][0]) + line[0][1]
            y_point = point[1]

        if y_point == y_line:
            return 0  # point on line
        elif y_point < y_line:
            return -1  # point under line or on the left
        else:
            return 1  # point above line or on the right
