"""
test_harmonization

Author: Tobias Seydewitz
Date: 05.04.18
Mail: tobi.seyde@gmail.com
"""
from unittest import TestCase
import numpy as np
from src.harmonization import (binary_jaccard,
                               simple_matching_coefficient,
                               treecover_similarity,)


class TestHarmonization(TestCase):
    def test_binary_jaccard_with_non_binary_data(self):
        a = np.random.randint(5, size=(10, 10))

        with self.assertRaises(ValueError) as err:
            binary_jaccard(a, a)

    def test_binary_jaccard_with_non_zero_equal_binary_data(self):
        a = np.random.randint(2, size=(10, 10))

        expected = 1
        actual = binary_jaccard(a, a)

        self.assertEqual(expected, actual, 'Must return a jaccard of 1.0 in case of equal image.')

    def test_binary_jaccard_with_zero_binary_data(self):
        a = np.zeros(shape=(10, 10))

        expected = 0
        actual = binary_jaccard(a, a)

        self.assertEqual(expected, actual, 'Zero image should return a jaccard of zero.')

    def test_binary_jaccard_with_half_equal_image(self):
        a = [1] * 10
        b = [1] * 5 + [0] * 5

        expected = .5
        actual = binary_jaccard(a, b)

        self.assertEqual(expected, actual, 'Half equal image should return a jaccard of 0.5.')

    def test_simple_matching_coefficient_with_non_zero_equal_binary_data(self):
        a = np.random.randint(2, size=(10, 10))

        expected = 1
        actual = simple_matching_coefficient(a, a)

        self.assertEqual(expected, actual, 'Must return a smc of 1.0 in case of equal image.')

    def test_simple_matching_coefficient_with_zero_binary_data(self):
        a = np.zeros(shape=(10, 10))

        expected = 1
        actual = simple_matching_coefficient(a, a)

        self.assertEqual(expected, actual, 'Zero image should return a smc of 1.')

    def test_simple_matching_coefficient_with_half_equal_image(self):
        a = [1] * 10
        b = [1] * 5 + [0] * 5

        expected = .5
        actual = simple_matching_coefficient(a, b)

        self.assertEqual(expected, actual, 'Half equal image should return a smc of 0.5.')
