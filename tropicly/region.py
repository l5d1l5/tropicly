from tropicly.utils import cache_directories
from tropicly.utils import get_data_dir

from itertools import combinations
from scipy.stats import mannwhitneyu

import pandas as pd
from collections import OrderedDict

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
