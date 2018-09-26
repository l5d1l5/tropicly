"""
soc.py

Author: Tobias Seydewitz
Date: 25.09.18
Mail: tobi.seyde@gmail.com
"""
import pandas as pd
import matplotlib.pyplot as plt


src = pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/soce.csv').values

fig, axes = plt.subplots(ncols=3, sharey=True, figsize=(7, 3.5))
fig.subplots_adjust(wspace=0.1)

for ax, row in zip(axes, [src[1], src[0], src[2]]):
    mean = row[2::3]/1000000000
    lower_err = mean - row[3::3]/1000000000
    upper_err = row[1::3]/1000000000 - mean

    ax.bar(
        [i for i in range(1, 5)],
        mean,
        yerr=[lower_err, upper_err],
        width=0.6,
        align='center',
        color='#fc8d59',
    )

    ax.set_xticklabels(
        ['', 'SC1', 'SC2', 'SC3', 'SC4'],
        fontsize=10,
        fontname='Times new roman',
    )
    ax.set_xlabel(row[0].capitalize(), fontsize=12, fontname='Times new roman')

axes[0].set_ylabel(r'Soil organic carbon emissions [PgCO$_2$]', fontsize=12, fontname='Times new roman')

plt.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/soc.png',
    format='png'
)
