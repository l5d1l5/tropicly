"""
hexagon.py

Author: Tobias Seydewitz
Date: 25.10.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from math import sin, cos, pi
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Polygon, Rectangle
from matplotlib.collections import PolyCollection
from matplotlib import rcParams

from tropicly.grid import GridPolygon, PolygonGrid


rcParams['patch.facecolor'] = 'none'

area = 1.8
img = [2.2, 2, 6.7, 4.7]

hexagon = GridPolygon.regular_hexagon(area=area)
grid = PolygonGrid(img, hexagon)

# hexagon polygon coordinates
x, y = list(zip(*hexagon.boundary.coords))
x, y = list(x), list(y)
hex_coords = np.array([x, y]).T

# grid coords
cells = []
for cell in grid:
    cellx, celly = list(zip(*cell.boundary.coords))
    cellx, celly = list(cellx), list(celly)
    cells.append(np.array([cellx, celly]).T)

# line and point coords
mid = [hexagon.centroid.x, hexagon.centroid.y]
R_line = [[mid[0], x[3]], [mid[1], y[3]]]
R_point = [(mid[0]+x[3])/2, (mid[1]+y[3])/2]
e_point = [(x[3]+x[4])/2, (y[3]+y[4])/2]
d_line = [[x[0], x[2]], [mid[1], mid[1]]]
d_point = [(x[0]+mid[0])/2, mid[1]]
r_point = [(mid[0]+x[2])/2, mid[1]]
origin = 0

# annotation coords
labels = ['v$_{}$'.format(i) for i in range(len(x)-1)]
labels += ['m']
labels += ['$R$']
labels += ['$e$']
labels += ['$d$']
labels += ['$r$']
labels += ['$x_1, y_2$']
labels += ['$0, 0$']

annotation_x = x[:-1] + [mid[0]] + [R_point[0]] + [e_point[0]] + [d_point[0]] + [r_point[0]] + [img[0]] + [origin]
annotation_y = y[:-1] + [mid[1]] + [R_point[1]] + [e_point[1]] + [d_point[1]] + [r_point[1]] + [img[1]] + [origin]

annotation_coords = np.array([annotation_x, annotation_y]).T

annotations = []
for label, coords in zip(labels, annotation_coords):
    x_coor = 0.1*cos(0.5*pi) + coords[0]
    y_coor = 0.1*sin(0.5*pi) + coords[1]

    annotations.append([label, [x_coor, y_coor]])


# visualization
fig, ax = plt.subplots()

ax.set_xlim(left=-0.1, right=8)
ax.set_ylim(bottom=-0.1, top=5.8)
ax.set_aspect('equal')

points = ax.scatter(x, y, marker='x', color='black', zorder=2)
orig = ax.scatter(origin, origin, marker='+', color='black', zorder=2)
mid = ax.scatter(*mid, marker='.', color='black', zorder=2)
bounds = ax.scatter((img[0], img[2]), (img[1], img[3]), marker='x', color='black', zorder=2)
hex = Polygon(hex_coords, closed=True, edgecolor='red', fill=False, zorder=1)
r_line = Line2D(*R_line, zorder=1, linestyle='--')
d_line = Line2D(*d_line, zorder=1, linestyle='--')
img = Rectangle((img[0], img[1]), width=(img[2]-img[0]), height=(img[3]-img[1]), fill=False, edgecolor='black', linestyle=':')
hex_grid = PolyCollection(cells, closed=True, edgecolors='red')
hex_grid.set_facecolor(None)

ax.add_artist(hex)
ax.add_artist(img)
ax.add_artist(r_line)
ax.add_artist(d_line)
ax.add_artist(hex_grid)

ax.get_xaxis().set_visible(False)
ax.get_yaxis().set_visible(False)

for spine in ax.spines.values():
    spine.set_visible(False)


for annotation in annotations:
    ax.annotate(*annotation, zorder=1, fontsize=10, weight='bold')

ax.annotate('Odd row:\n$x_{off}=x_1+r$\n$y_{off}=y_1-v_3+v_0$', (-0.1, 2.3), fontsize=10,)
ax.annotate('Even row:\n$x_{off}=x_1+d$\n$y_{off}=y_1-v_3+v_0$', (-0.1, 3.3), fontsize=10,)

fig.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/hexagons.png',
    format='png'
)
