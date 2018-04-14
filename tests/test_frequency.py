"""
test_frequency

Author: Tobias Seydewitz
Date: 10.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from unittest import TestCase
from tropicly.frequency import (frequency,
                                most_common_class)
from collections import OrderedDict
from tests.utilities import random_test_data


class TestFrequency(TestCase):
    def test_frequency_with_float(self):
        a = np.zeros((100, 100), dtype=np.float16)

        with self.assertRaises(ValueError) as err:
            frequency(a)

    def test_frequency_with_valid(self):
        *_, gl30_10 = random_test_data()

        expected = OrderedDict(OrderedDict([(0, 877), (10, 888), (20, 919),
                                            (30, 876), (40, 938), (50, 957),
                                            (60, 916), (70, 915), (80, 930),
                                            (90, 903), (100, 881)]))
        actual = frequency(gl30_10)

        self.assertEqual(expected, actual)

    def test_most_common_class_with_zeros(self):
        a = np.zeros((10, 10), dtype=np.uint8)

        expected = 20
        actual = most_common_class(a)

        self.assertEqual(expected, actual)

    def test_most_common_class_with_valid(self):
        *_, gl30_10 = random_test_data()

        expected = 50
        actual = most_common_class(gl30_10)

        self.assertEqual(expected, actual)

    def test_most_common_class_with_default_fallback(self):
        a = np.array([[20] * 5] * 5, dtype=np.uint8)

        expected = 20
        actual = most_common_class(a)

        self.assertEqual(expected, actual)

    def test_most_common_class_with_fallback(self):
        a = np.array([[20, 20, 10] * 5] * 5, dtype=np.uint8)

        expected = 10
        actual = most_common_class(a)

        self.assertEqual(expected, actual)
