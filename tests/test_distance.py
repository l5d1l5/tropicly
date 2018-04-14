"""
test_distance

Author: Tobias Seydewitz
Date: 12.04.18
Mail: tobi.seyde@gmail.com
"""
from unittest import TestCase
from tropicly.distance import (Distance,
                               haversine,
                               euclidean)


class TestDistance(TestCase):
    def test_distance_with_malicious_algorithm(self):
        with self.assertRaises(ValueError) as err:
            Distance('foo')

    def test_distance_with_valid(self):
        obj = Distance('euc')

        expected = 'euclidean'
        actual = obj.func.__name__

        self.assertEqual(expected, actual)

    def test_distance_with_args(self):
        obj = Distance('euc')

        expected = (float, int)
        actual = obj((4, 5), (1, 1))

        self.assertTrue(isinstance(actual, expected))

    def test_distance_with_wrong_number_of_args(self):
        obj = Distance('euc')

        with self.assertRaises(ValueError) as err:
            obj(1)


class TestAlgorithms(TestCase):
    def test_euclidean(self):
        expected = 5.
        actual = euclidean((1, 1), (4, 5))

        self.assertEqual(expected, actual)

    def test_haversine(self):
        expected = 157425
        actual = int(haversine((1, 1), (0, 0)))

        self.assertEqual(expected, actual)
