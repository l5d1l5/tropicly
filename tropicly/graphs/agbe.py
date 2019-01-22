import matplotlib.pyplot as plt
import pandas as pd


src = pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/agbe.csv').T
src = src[[1, 0, 2]]
src = src.values

fig, ax = plt.subplots(squeeze=True, figsize=(3, 2))

ax.bar(
    range(1, 4),
    src[1]/1000000000,
    width=0.6,
    color='#fc8d59'
)
ax.set_ylabel(
    r'AGBe [Gt CO$_2$]',
    fontsize=12,
    fontname='Times new roman'
)
ax.set_xticks([1, 2, 3])
ax.set_xticklabels(
    map(lambda x: x.capitalize(), src[0]),
    minor=False,
    fontsize=10,
    fontname='Times new roman',
)


plt.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/agbe.png',
    format='png'
)
