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


class TestAlgorithms(TestCase):
    def test_haversine(self):
        self.fail()
