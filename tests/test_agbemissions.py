import numpy as np
from unittest import TestCase
from tropicly.agb_emissions import agb_emissions


class TestAGBEmissions(TestCase):
    def setUp(self):
        np.random.seed(42)
        self.driver = np.array([0, 10, 20, 25, 30, 40, 50,
                                60, 70, 80, 90, 100, 255], dtype=np.uint8)
        self.biomass = np.round(np.random.rand(13)*100, decimals=2).astype(np.float32)

    def test_agb_emissions(self):
        expected = np.round(0.09 * 3.7 * self.biomass, decimals=2).astype(np.float32)
        actual = agb_emissions(self.driver, self.biomass, pdd_classes=(0, 10, 20, 25, 30, 40, 50, 60,
                                                                       70, 80, 90, 100, 255))

        self.assertTrue(np.array_equal(expected, actual))
