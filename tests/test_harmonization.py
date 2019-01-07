"""
test_harmonization

Author: Tobias Seydewitz
Date: 05.04.18
Mail: tobi.seyde@gmail.com
"""
from unittest import TestCase

import numpy as np

from tests.utilities import random_test_data
from tropicly.harmonization import jaccard_index
from tropicly.harmonization import simple_matching_coefficient
from tropicly.harmonization import treecover_similarity


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
                    'JI0': 0,
                    'JI10': 0,
                    'JI20': 0,
                    'JI30': 0}
        actual = treecover_similarity(a, a, compute_smc=True)

        self.assertEqual(expected, actual)

    def test_treecover_similarity_with_mock_data(self):
        gfc, *_, gl30, _ = random_test_data()

        expected = {'SMC0': 0.8521,
                    'SMC10': 0.9026,
                    'SMC20': 0.9517,
                    'SMC30': 1.0,
                    'JI0': 0.7075,
                    'JI10': 0.786,
                    'JI20': 0.881,
                    'JI30': 1.0}
        actual = treecover_similarity(gl30, gfc, compute_smc=True)

        self.assertEqual(expected, actual)

    def test_binary_jaccard_with_non_zero_equal_binary_data(self):
        a = np.random.randint(2, size=(10, 10))

        expected = 1
        actual = jaccard_index(a, a)

        self.assertEqual(expected, actual, 'Must return a jaccard of 1.0 in case of equal image.')

    def test_binary_jaccard_with_zero_binary_data(self):
        a = np.zeros(shape=(10, 10))

        expected = 0
        actual = jaccard_index(a, a)

        self.assertEqual(expected, actual, 'Zero image should return a jaccard of zero.')

    def test_binary_jaccard_with_half_equal_image(self):
        a = [1] * 10
        b = [1] * 5 + [0] * 5

        expected = .5
        actual = jaccard_index(a, b)

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
