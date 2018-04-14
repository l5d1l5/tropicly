"""
test_classification

Author: Tobias Seydewitz
Date: 10.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from unittest import TestCase
from tropicly.classification import (extract_square,
                                     circle_mask)


class TestClassification(TestCase):
    def test_extract_square_with_real_world_length(self):
        a = np.ones(shape=(25, 25), dtype=np.uint8)

        expected = (17, 17)
        actual = extract_square(a, (12, 12), side_length=510, res=30)

        self.assertEqual(expected, actual.shape)

    def test_extract_square_with_block_size(self):
        a = np.ones(shape=(25, 25), dtype=np.uint8)

        expected = (17, 17)
        actual = extract_square(a, (12, 12), block_size=17)

        self.assertEqual(expected, actual.shape)

