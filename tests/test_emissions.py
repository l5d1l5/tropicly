from unittest import TestCase

import numpy as np

from emissions import factor_map
from emissions import soc_emissions
from settings import SOCClasses


class TestEmissions(TestCase):
    def setUp(self):
        np.random.seed(42)
        self.driver = np.array([0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 255], dtype=np.uint8)
        self.intact = np.array([1]*13+[0]*13, dtype=np.uint8)
        self.soc = np.round_(np.random.rand(13) * 100, decimals=2).astype(np.float32)
        self.f1 = np.array([[0, .172, 0, 0, .039, .039, 0, 0, .039, 0, .039, 0, 0],
                            [0, .213, 0, 0, .064, .064, 0, 0, .064, 0, .064, 0, 0],
                            [0, .254, 0, 0, .089, .089, 0, 0, .089, 0, .089, 0, 0]], dtype=np.float32)  # secondary
        self.f2 = np.array([[0, .219, 0, .066, .098, .098, 0, 0, .098, 0, .098, 0, 0],
                            [0, .252, 0, .086, .121, .121, 0, 0, .121, 0, .121, 0, 0],
                            [0, .285, 0, .106, .144, .144, 0, 0, .144, 0, .144, 0, 0]], dtype=np.float32)  # primary

    def test_factor_map_secondary(self):
        expected = self.f1
        actual = factor_map(self.driver)

        self.assertTrue(np.array_equal(expected, actual))

    def test_factor_map_primary(self):
        expected = self.f2
        actual = factor_map(self.driver, forest_type=SOCClasses.primary_forest)

        self.assertTrue(np.array_equal(expected, actual))

    def test_factor_map_intact(self):
        expected = np.concatenate((self.f2, self.f1), axis=1)
        actual = factor_map(np.concatenate((self.driver, self.driver)), self.intact)

        self.assertTrue(np.array_equal(expected, actual))

    def test_soc_emissions_secondary(self):
        expected = np.round(0.09 * self.soc * self.f1, decimals=2).astype(np.float32)
        actual = soc_emissions(self.driver, self.soc)

        self.assertTrue(np.array_equal(expected, actual))

    def test_soc_emissions_primary(self):
        expected = np.round(0.09 * self.soc * self.f2, decimals=2).astype(np.float32)
        actual = soc_emissions(self.driver, self.soc, intact=np.ones(13))

        self.assertTrue(np.array_equal(expected, actual))

    def test_soc_emissions_intact(self):
        primary = np.round(0.09 * self.soc * self.f2, decimals=2).astype(np.float32)
        secondary = np.round(0.09 * self.soc * self.f1, decimals=2).astype(np.float32)

        expected = np.concatenate((primary, secondary), axis=1)
        actual = soc_emissions(np.concatenate((self.driver, self.driver)), np.concatenate((self.soc, self.soc)),
                               intact=self.intact)

        self.assertTrue(np.array_equal(expected, actual))
