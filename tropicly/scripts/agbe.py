"""
agbe.py

Author: Tobias Seydewitz
Date: 26.09.18
Mail: tobi.seyde@gmail.com
"""
import pandas as pd
import matplotlib.pyplot as plt


src = pd.read_csv('/home/tobi/Documents/Master/code/python/Master/data/proc/ana/agbe.csv').T.values
print(src)
fig, ax = plt.subplots(squeeze=True, figsize=(3.2, 3))

ax.bar([1, 2, 3], src[1]/1000000000, width=0.6)
ax.set_ylabel(r'AGB emissions [PgCO$_2$]', fontsize=12, fontname='Times new roman')

plt.show()
fig.savefig(
    '/home/tobi/Documents/Master/code/python/Master/doc/thesis/img/agbe.png',
    format='png'
)