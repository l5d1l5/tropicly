import matplotlib.pyplot as plt
from matplotlib.markers import MarkerStyle
import pandas as pd

from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir


DIRS = cache_directories(get_data_dir())

src = pd.read_csv(DIRS.ana / 'harmonization_americas.csv')


# initial data clean up
zeros = src[src['JC00'] == 0]
src.drop(zeros.index, axis=0, inplace=True)
src.sort_values('key', ascending=False, inplace=True)

fig, ax = plt.subplots(figsize=(10, 5))

markers = [
    MarkerStyle(marker='o', fillstyle='none'),
    MarkerStyle(marker='s', fillstyle='none'),
    MarkerStyle(marker='^', fillstyle='none'),
    MarkerStyle(marker='X', fillstyle='none')
]

for marker, label in zip(markers, ['JC00', 'JC10', 'JC20', 'JC30']):
    ax.scatter(range(0, len(src)), src[label], s=24, marker=marker, edgecolors='black', facecolor='none')


fig.show()
