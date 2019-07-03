import matplotlib.pyplot as plt
import pandas as pd

from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir

DIRS = cache_directories(get_data_dir())

src = pd.read_csv(DIRS.ana / 'esv.csv').values

fig, axes = plt.subplots(ncols=3, sharey=True, figsize=(4.5, 3))
fig.subplots_adjust(wspace=0.1)

for ax, row in zip(axes, [src[0], src[2], src[1]]):
    ax.bar(
        range(1, 4),
        row[1::2]/(10**9),
        width=-0.4,
        align='edge',
        color='#fc8d59',
        label='Loss'
    )
    ax.bar(
        [i for i in range(1, 4)],
        row[2::2]/(10**9),
        width=0.4,
        align='edge',
        color='#99d594',
        label='Gain'
    )

    ax.set_xticks(range(1, 4))
    ax.set_xticklabels(
        ['Co', 'Dg', 'Wb'],
        fontsize=10,
        fontname='Times new roman',
    )
    ax.set_title(row[0].capitalize(), fontsize=12, fontname='Times new roman')

axes[0].set_ylabel('ESV [billion Int$/y]', fontsize=12, fontname='Times new roman')
axes[-1].legend()

#plt.show()
fig.savefig(
    str(DIRS.fig / 'esv.png'),
    format='png'
)