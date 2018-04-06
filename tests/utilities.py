"""
utilities.py

Author: Tobias Seydewitz
Date: 05.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np


def random_test_data(size=(100, 100)):
    """
    Creates random test data sets, data properties meet Hansen et al. and
    Chen et al..

    :param size: numeric tuple
        Shape of test data, default is a 100x100 2D array.
    :return: treecover, loss, gain, gl30_00, gl30_10
        The returned data has the dtype uint8 and dimensionality of size.
        Treecover, value range 0 to 100. Loss, value range 0-12, values between 1 to 12
        appear only within treecover 1 to 100. Gain, value range 0-1 randomly distributed.
        GL30_00, value range 0,10,20,30,40,50,60,70,80,90,100, value 20 appears only within
        treecover > 30.
    """
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
    gl30_10 = np.random.choice([i * 10 for i in range(11)], size=size)

    return (treecover.astype(np.uint8),
            loss.astype(np.uint8),
            gain.astype(np.uint8),
            gl30_00.astype(np.uint8),
            gl30_10.astype(np.uint8))
