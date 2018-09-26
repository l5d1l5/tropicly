"""
esv.py

Author: Tobias Seydewitz
Date: 21.09.18
Mail: tobi.seyde@gmail.com
"""
import pandas as pd
import matplotlib.pyplot as plt


src = pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/esv.csv').values

fig, axes = plt.subplots(ncols=3, sharey=True, figsize=(5.5, 3.6))
fig.subplots_adjust(wspace=0.1)

for ax, row in zip(axes, src):
    ax.bar(
        [i for i in range(1, 4)],
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

    ax.set_xticklabels(
        ['', 'Costanza', 'DeGroot', 'Worldbank'],
        fontsize=10,
        fontname='Times new roman',
        rotation=60
    )
    ax.set_xlabel(row[0].capitalize(), fontsize=12, fontname='Times new roman')

axes[0].set_ylabel('Ecosystem service value [billion Int$/y]', fontsize=12, fontname='Times new roman')
axes[-1].legend()

plt.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/esv.png',
    format='png'
)