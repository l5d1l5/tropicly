"""
test_classification

Author: Tobias Seydewitz
Date: 10.04.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from affine import Affine
from unittest import TestCase
from tests.utilities import random_test_data
from tropicly.classification import (extract_square,
                                     superimpose,
                                     circle_mask,
                                     reclassify)


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

    def test_superimpose_with_malicious_shapes(self):
        a = np.zeros((10, 10), dtype=np.uint8)
        treecover, loss, gain, *_ = random_test_data()

        with self.assertRaises(ValueError) as err:
            superimpose(a, treecover, gain, loss)

    def test_superimpose_with_equal_shaped(self):
        treecover, loss, gain, _, gl30_10 = random_test_data()

        expected = (100, 100)
        actual = superimpose(gl30_10, treecover, gain, loss)

        self.assertEqual(expected, actual.shape)
        self.assertEqual(np.uint8, actual.dtype)

    def test_superimpose_with_valid_data(self):
        treecover, loss, gain, _, gl30_10 = random_test_data((15, 15))

        expected = np.array([[0, 0, 0, 0, 25, 20, 25, 0, 0, 0, 0, 0, 0, 0, 25],
                             [25, 0, 0, 0, 0, 0, 0, 25, 0, 0, 0, 25, 0, 0, 25],
                             [0, 90, 25, 0, 0, 0, 0, 40, 0, 0, 80, 0, 25, 0, 30],
                             [0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 70, 0],
                             [0, 60, 0, 0, 50, 0, 30, 0, 0, 0, 0, 0, 25, 0, 0],
                             [0, 0, 30, 0, 50, 0, 0, 0, 80, 0, 0, 0, 0, 0, 0],
                             [40, 0, 0, 0, 0, 0, 0, 0, 40, 60, 25, 0, 0, 0, 0],
                             [25, 0, 0, 0, 20, 25, 30, 0, 0, 0, 0, 0, 25, 0, 0],
                             [0, 0, 0, 20, 25, 0, 0, 0, 50, 0, 0, 25, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 100, 0, 0, 80, 90, 0, 0, 80, 25],
                             [0, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 0, 0, 0, 25],
                             [0, 0, 40, 25, 0, 0, 0, 0, 25, 0, 0, 0, 0, 0, 25],
                             [0, 25, 0, 0, 25, 0, 0, 0, 0, 100, 90, 0, 0, 0, 0],
                             [0, 0, 0, 0, 0, 0, 60, 40, 0, 0, 0, 25, 0, 100, 60],
                             [0, 0, 0, 20, 0, 25, 0, 0, 0, 0, 0, 0, 20, 0, 100]], dtype=np.uint8)
        actual = superimpose(gl30_10, treecover, gain, loss)

        self.assertTrue(np.array_equal(expected, actual))

    def test_reclassify(self):
        affine = Affine(0.00027041676761241124, 0.0, 120.0000008, 0.0, -0.00027041676761241124, 4.9999992)

        driver = np.array([[0, 0, 0, 0,30,20,20, 0, 0, 0, 0, 0, 0, 0,25],
                           [0, 0, 0, 0,30,20,30, 0, 0, 0, 0,25, 0, 0,25],
                           [0, 0, 0, 0,30,20,30, 0, 0, 0,80, 0,25, 0,30],
                           [0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,70, 0],
                           [0,60, 0, 0,50, 0,30, 0, 0, 0, 0, 0,25, 0, 0],
                           [0, 0,30, 0,50, 0, 0, 0,80, 0, 0, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0, 0, 0,40,60,25, 0, 0, 0, 0],
                           [0, 0, 0, 0,20,25,30, 0, 0, 0, 0, 0,25, 0, 0],
                           [0, 0, 0,20,25, 0, 0, 0,50, 0, 0,25, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0,10, 0, 0,80,90, 0, 0,80,25],
                           [0, 0, 0, 0, 0,25, 0, 0, 0, 0, 0, 0, 0, 0,25],
                           [0, 0,40,25, 0, 0, 0, 0,25, 0, 0, 0, 0, 0,25],
                           [0,25, 0, 0,25, 0, 0, 0, 0,10,90, 0, 0, 0, 0],
                           [0, 0, 0, 0, 0, 0,60,40, 0, 0, 0,25,20,10,60],
                           [0, 0, 0,20, 0,25, 0, 0, 0, 0, 0, 0,20, 0,10]], dtype=np.uint8)

        print(reclassify(driver, buffer_size=500, affine=affine))
