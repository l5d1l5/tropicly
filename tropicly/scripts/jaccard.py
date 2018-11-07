"""
jaccard.py

Author: Tobias Seydewitz
Date: 20.09.18
Mail: tobi.seyde@gmail.com
"""
import pandas as pd
import matplotlib.pyplot as plt


src = pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/harmonization_americas.csv')
src = src.append(pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/harmonization_africa.csv'))
src = src.append(pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/harmonization_asia.csv'))

# initial data clean up
zeros = src[src['JC00'] == 0]
src.drop(zeros.index, axis=0, inplace=True)
src.rename(columns=lambda x: x.upper() if x[:2] == 'jc' else x, inplace=True)
src.dropna(axis=0, how='any', inplace=True)
src.columns = 'JC0 JC1 JC2 JC3 tile region'.split()

fig, axes = plt.subplots(ncols=3, sharey=True, figsize=(5.5, 3))
fig.subplots_adjust(wspace=0.1)

for ax, group in zip(axes, src.groupby(by='region', sort=True)):
    region, df = group

    boxes = ax.boxplot(
        [row for row in df.values.T[0:4]],
        showmeans=True,
        sym='.',
        patch_artist=True
    )

    ax.set_xticklabels(['JC$_0$', 'JC$_1$', 'JC$_2$', 'JC$_3$'], fontsize=10, fontname='Times new roman')
    ax.set_title(region, fontsize=12, fontname='Times new roman')
    for box, med, mean in zip(boxes['boxes'], boxes['medians'], boxes['means']):
        box.set_facecolor('white')
        med.set_color('black')
        mean.set_marker('x')
        mean.set_markeredgecolor('red')


axes[0].set_yticks([tick / 10 for tick in range(11)])
axes[0].set_ylabel('Jaccard score', fontsize=12, fontname='Times new roman')
axes[0].set_ylim(bottom=-.01, top=1.)

plt.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/jaccard.png',
    format='png'
)
