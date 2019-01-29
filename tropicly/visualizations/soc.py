import matplotlib.pyplot as plt
import pandas as pd

from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir

DIRS = cache_directories(get_data_dir())

src = pd.read_csv(DIRS.ana / 'soce.csv')
src.drop(['sc4_me', 'sc4_ma', 'sc4_mi', 'sc2_me', 'sc2_ma', 'sc2_mi'], axis=1, inplace=True)
src = src[['Unnamed: 0', 'sc3_ma', 'sc3_me', 'sc3_mi', 'sc1_ma', 'sc1_me', 'sc1_mi']]
src = src.values

fig, axes = plt.subplots(ncols=3, sharey=True, figsize=(4, 2.5))
fig.subplots_adjust(wspace=0.1)

for ax, row in zip(axes, [src[1], src[2], src[0]]):
    mean = row[2::3]/1000000000
    lower_err = mean - row[3::3]/1000000000
    upper_err = row[1::3]/1000000000 - mean

    ax.bar(
        range(1, 3),
        mean,
        yerr=[lower_err, upper_err],
        width=0.6,
        align='center',
        color='#fc8d59',
        capsize=4
    )

    ax.set_xticklabels(
        ['SC1', 'SC2'],
        minor=False,
        fontsize=10,
        fontname='Times new roman',
    )
    ax.set_title(row[0].capitalize(), fontsize=12, fontname='Times new roman')

axes[0].set_ylabel(r'SOCe [Gt CO$_2$]', fontsize=12, fontname='Times new roman')

#plt.show()
fig.savefig(
    str(DIRS.fig / 'soc.png'),
    format='png'
)
