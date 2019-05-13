"""**test_definition**

:Author: Tobias Seydewitz
:Date: 05.04.18
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""
from unittest import TestCase

import numpy as np

from tests.utilities import random_test_data
from tropicly.definition import jaccard_index
from tropicly.definition import treecover_agreement


class TestHarmonization(TestCase):
    def test_treecover_similarity_with_false_shaped_data(self):
        gl30 = np.zeros(shape=(10, 10))
        gfc = np.zeros(shape=(5, 5))

        with self.assertRaises(ValueError):
            treecover_agreement(gl30, gfc, canopy_densities=(0, 10, 20, 30), cover_classes=(10,))

    def test_treecover_similarity_with_zero_data(self):
        a = np.zeros(shape=(10, 10))

        expected = [0, 0, 0, 0]
        actual = treecover_agreement(a, a, canopy_densities=(0, 10, 20, 30), cover_classes=(10,))

        self.assertEqual(expected, actual)

    def test_treecover_similarity_with_mock_data(self):
        gfc, *_, gl30, _ = random_test_data()

        expected = [0.7075, 0.786, 0.881, 1.0]
        actual = treecover_agreement(gl30, gfc, canopy_densities=(0, 10, 20, 30), cover_classes=(20,))

        self.assertEqual(expected, actual)

    def test_binary_jaccard_with_non_zero_equal_binary_data(self):
        a = np.random.randint(2, size=(10, 10))

        expected = 1
        actual = jaccard_index(a, a)

        self.assertEqual(expected, actual, 'Must return a fordef of 1.0 in case of equal image.')

    def test_binary_jaccard_with_zero_binary_data(self):
        a = np.zeros(shape=(10, 10))

        expected = 0
        actual = jaccard_index(a, a)

        self.assertEqual(expected, actual, 'Zero image should return a fordef of zero.')

    def test_binary_jaccard_with_half_equal_image(self):
        a = [1] * 10
        b = [1] * 5 + [0] * 5

        expected = .5
        actual = jaccard_index(a, b)

        self.assertEqual(expected, actual, 'Half equal image should return a fordef of 0.5.')
