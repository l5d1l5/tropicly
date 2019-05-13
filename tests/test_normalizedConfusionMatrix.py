from unittest import TestCase
from legacy.confusion_matrix import _NormalizedConfusionMatrix
import numpy as np


class TestNormalizedConfusionMatrix(TestCase):
    # TODO test division zero
    def setUp(self):
        self.ncm_commission = _NormalizedConfusionMatrix([10, 20, 30], method='commission')
        self.ncm_omission = _NormalizedConfusionMatrix([10, 20, 30], method='omission')

        self.commission = [[10, 8, 1, 19],
                           [1, 10, 1, 12],
                           [3, 0, 10, 13]]
        self.omission = [[10, 1, 3, 14],
                         [8, 10, 0, 18],
                         [1, 1, 10, 12]]

        self.cm = np.array([[0.53, 0.08, 0.23, 0.0],
                            [0.42, 0.83, 0.0, 0.0],
                            [0.05, 0.08, 0.77, 0.0],
                            [0.47, 0.17, 0.23, 0.68]], dtype=np.float)
        self.om = np.array([[0.71, 0.07, 0.21, 0.29],
                            [0.44, 0.56, 0.0, 0.44],
                            [0.08, 0.08, 0.83, 0.17],
                            [0.0, 0.0, 0.0, 0.68]], dtype=np.float)

    def test_add_to_commission(self):
        for idx, row in enumerate(self.commission):
            self.ncm_commission.add(row, idx)

        self.assertTrue(np.array_equal(self.cm, self.ncm_commission._matrix))

    def test_add_to_omission(self):
        for idx, row in enumerate(self.omission):
            self.ncm_omission.add(row, idx)

        self.assertTrue(np.array_equal(self.om, self.ncm_omission._matrix))
