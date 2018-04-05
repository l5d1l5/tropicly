"""
utilities.py

Author: Tobias Seydewitz
Date: 05.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np


def test_data(size=(100, 100)):
    # tree distribution
    distribution = np.random.uniform(size=size)

    # Hansen treecover
    treecover = np.random.uniform(size=size) * 100
    treecover = np.round_(treecover)
    treecover[distribution > .5] = 0

    # Hansen loss
    loss = np.random.choice([i for i in range(1, 13)], size=size)
    loss[treecover == 0] = 0
    loss[distribution > .3] = 0

    # Gain
    gain = np.random.randint(2, size=size)
    gain[distribution > .6] = 0

    # GL30 2000
    gl30_00 = np.random.choice([i * 10 for i in range(11) if i != 2], size=size)
    gl30_00[treecover > 30] = 20

    # GL30 2010
    gl30_100 = np.random.choice([i * 10 for i in range(11)], size=size)

    return (treecover.astype(np.uint8),
            loss.astype(np.uint8),
            gain.astype(np.uint8),
            gl30_00.astype(np.uint8),
            gl30_100.astype(np.uint8))
