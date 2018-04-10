"""
test_sampling

Author: Tobias Seydewitz
Date: 09.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from affine import Affine
from unittest import TestCase
from tests.utilities import random_test_data
from tropicly.sampling import (draw_sample,
                               sample_occupied)


class TestSampling(TestCase):
    def test_sample_occupied_with_malicious_data(self):
        a = np.random.randint(2, size=10)

        with self.assertRaises(ValueError) as err:
            sample_occupied(a)

    def test_sample_occupied_with_empty(self):
        a = np.zeros((5,5), dtype=np.uint8)

        expected = 0
        actual = list(sample_occupied(a))

        self.assertEqual(expected, len(actual))

    def test_sample_occupied_with_valid(self):
        *_, gl30_10 = random_test_data((2, 2))

        expected = [{'x': None, 'label': 80, 'col': 0, 'y': None, 'row': 1},
                    {'x': None, 'label': 50, 'col': 1, 'y': None, 'row': 0},
                    {'x': None, 'label': 90, 'col': 0, 'y': None, 'row': 0}]
        actual = sample_occupied(gl30_10, seed=42)

        self.assertEqual(expected, actual)

    def test_sample_occupied_with_valid_and_affine(self):
        *_, gl30_10 = random_test_data((2, 2))
        affine = Affine(30, 0, 0, 0, 30, 0)

        expected = [{'col': 0, 'row': 1, 'x': 0.0, 'y': 30.0, 'label': 80},
                    {'col': 1, 'row': 0, 'x': 30.0, 'y': 0.0, 'label': 50},
                    {'col': 0, 'row': 0, 'x': 0.0, 'y': 0.0, 'label': 90}]
        actual = sample_occupied(gl30_10, affine=affine, seed=42)

        self.assertEqual(expected, actual)

    def test_sample_occupied_with_valid_and_affine_and_occupied(self):
        *_, gl30_10 = random_test_data((5, 5))
        affine = Affine(30, 0, 0, 0, 30, 0)

        expected = [{'col': 3, 'x': 90.0, 'y': 30.0, 'row': 1, 'label': 20}]
        actual = sample_occupied(gl30_10, affine=affine, occupied=(20,), seed=42)

        self.assertEqual(expected, actual)

    def test_draw_sample_with_smaller_sample_space(self):
        data = [1] * 10

        expected = 10
        actual = list(draw_sample(data))

        self.assertEqual(expected, len(actual))

    def test_draw_sample_with_greater_sample_space(self):
        data = [1] * 200

        expected = 200
        actual = list(draw_sample(data))

        self.assertEqual(expected, len(actual))

    def test_draw_sample_with_limited_sample_space(self):
        data = [1] * 200

        expected = 100
        actual = list(draw_sample(data, samples=100))

        self.assertEqual(expected, len(actual))

    def test_draw_sample_with_empty_sample_space(self):
        expected = 0
        actual = list(draw_sample([]))

        self.assertEqual(expected, len(actual))
