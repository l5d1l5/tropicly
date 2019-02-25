import matplotlib.pyplot as plt
import pandas as pd

from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir


DIRS = cache_directories(get_data_dir())

src = pd.read_csv(DIRS.textual / 'harmonization_americas.csv')
src = src.append(pd.read_csv(DIRS.textual / 'harmonization_africa.csv'), ignore_index=True)
src = src.append(pd.read_csv(DIRS.textual / 'harmonization_asia.csv'), ignore_index=True)

# initial data clean up
zeros = src[src['JC00'] == 0]
src.drop(zeros.index, axis=0, inplace=True)

fig, axes = plt.subplots(ncols=4, sharey=True, figsize=(5.5, 3))
fig.subplots_adjust(wspace=0.1)

groups = src.groupby(by='region', sort=True)

for ax, selection, region in zip(axes, ['Americas', 'Asia', 'Africa'], ['South America', 'Asia/Australia', 'Africa']):
    df = groups.get_group(selection)

    boxes = ax.boxplot(
        [row for row in df.values.T[0:4]],
        showmeans=True,
        sym='.',
        patch_artist=True
    )

    ax.set_xticklabels(['JI$_0$', 'JI$_1$', 'JI$_2$', 'JI$_3$'], fontsize=10, fontname='Times new roman')
    ax.set_title(region, fontsize=12, fontname='Times new roman')
    for box, med, mean in zip(boxes['boxes'], boxes['medians'], boxes['means']):
        box.set_facecolor('white')
        med.set_color('black')
        mean.set_marker('x')
        mean.set_markeredgecolor('red')

###### TODO refactor
boxes = axes[-1].boxplot(
    [row for row in src.values.T[0:4]],
    showmeans=True,
    sym='.',
    patch_artist=True
)

axes[-1].set_xticklabels(['JI$_0$', 'JI$_1$', 'JI$_2$', 'JI$_3$'], fontsize=10, fontname='Times new roman')
axes[-1].set_title('Global', fontsize=12, fontname='Times new roman')
for box, med, mean in zip(boxes['boxes'], boxes['medians'], boxes['means']):
    box.set_facecolor('white')
    med.set_color('black')
    mean.set_marker('x')
    mean.set_markeredgecolor('red')
#######

axes[0].set_yticks([tick / 10 for tick in range(11)])
axes[0].set_ylabel('Jaccard Index', fontsize=12, fontname='Times new roman')
axes[0].set_ylim(bottom=-.01, top=1.)

plt.show()
fig.savefig(
    str(DIRS.fig / 'jaccard.png'),
    format='png'
)
