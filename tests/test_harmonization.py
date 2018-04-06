"""
test_harmonization

Author: Tobias Seydewitz
Date: 05.04.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
from unittest import TestCase
from tests.utilities import random_test_data
from src.harmonization import (binary_jaccard,
                               treecover_similarity,
                               simple_matching_coefficient,)


class TestHarmonization(TestCase):
    def test_treecover_similarity_with_false_shaped_data(self):
        gl30 = np.zeros(shape=(10, 10))
        gfc = np.zeros(shape=(5, 5))

        with self.assertRaises(ValueError) as err:
            treecover_similarity(gl30, gfc)

    def test_treecover_similarity_with_zero_data(self):
        a = np.zeros(shape=(10, 10))

        expected = {'SMC0': 1.0,
                    'SMC10': 1.0,
                    'SMC20': 1.0,
                    'SMC30': 1.0,
                    'JC0': 0,
                    'JC10': 0,
                    'JC20': 0,
                    'JC30': 0}
        actual = treecover_similarity(a, a, compute_smc=True)

        self.assertEqual(expected, actual)

    def test_treecover_similarity_with_mock_data(self):
        gfc, *_, gl30, _ = random_test_data((5,5))

        actual = treecover_similarity(gl30, gfc, compute_smc=True)
        print(actual)

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
