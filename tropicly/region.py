from collections import OrderedDict
from itertools import combinations

import pandas as pd
from scipy.stats import mannwhitneyu

from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir

DIRS = cache_directories(get_data_dir())

data = OrderedDict([
    ('americas', pd.read_csv(DIRS.ana / 'harmonization_americas.csv')),
    ('asia', pd.read_csv(DIRS.ana / 'harmonization_asia.csv')),
    ('africa', pd.read_csv(DIRS.ana / 'harmonization_africa.csv'))
])

for key, val in data.items():
    zeros = val[val['JC00'] == 0]
    val.drop(zeros.index, axis=0, inplace=True)

two_sided_equal_results = OrderedDict()
one_sided_greater_results = OrderedDict()

for region1, region2 in combinations(data.keys(), 2):
    X1, X2 = data[region1], data[region2]
    two_sided_equal = []
    one_sided_greater = []

    for column in ['JC00', 'JC10', 'JC20', 'JC30']:
        two_sided_equal.append(
            round(mannwhitneyu(X1[column], X2[column], alternative='two-sided').pvalue, 4)
        )
        one_sided_greater.append(
            round(mannwhitneyu(X1[column], X2[column], alternative='greater').pvalue, 4)
        )

    two_sided_equal_results['%s == %s' % (region1, region2)] = two_sided_equal
    one_sided_greater_results['%s <= %s' % (region1, region2)] = one_sided_greater

print(two_sided_equal_results)
print(one_sided_greater_results)


# TODO refactor
df = pd.read_csv(DIRS.ana / 'harmonization_americas.csv')
nw = df[df.key.str.contains(r'\d{2}N_\d{3}W')]
sw = df[df.key.str.contains(r'\d{2}S_\d{3}W')]

nw = list(nw)
nw = list(map(list, nw))

sw = list(sw)
sw = list(map(list, sw))

nw = sorted(nw, key=lambda x: (x[4][2:3], x[4][-1], int(x[4][:2]), int(x[4][4:7])), reverse=True)
sw = sorted(sw, key=lambda x: (x[4][2:3], x[4][-1], int(x[4][:2]), int(x[4][4:7])))

df = pd.DataFrame.from_records(nw + sw)