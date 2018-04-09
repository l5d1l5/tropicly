"""
test_sampling

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from unittest import TestCase
from tests.utilities import random_test_data
from tropicly.sampling import (draw_sample,
                               sample_occupied)


class TestSampling(TestCase):
    def test_sample_occupied_with_malicious_data(self):
        a = np.random.randint(2, size=10)

        with self.assertRaises(ValueError) as err:
            sample_occupied(a)

    def test_sample_occupied_with(self):
        *_, gl30_10 = random_test_data((5, 5))

        actual = sample_occupied(gl30_10)
        print(gl30_10)
        print(actual)

    def test_draw_sample_with_smaller_sample_space(self):
        data = [1] * 10

        expected = 10
        actual = list(draw_sample(data))

        self.assertEqual(expected, len(actual))

    def test_draw_sample_with_greater_sample_space(self):
        data = [1] * 200

        expected = 100
        actual = list(draw_sample(data))

        self.assertEqual(expected, len(actual))
