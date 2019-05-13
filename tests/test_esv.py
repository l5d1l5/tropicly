from unittest import TestCase
from legacy.enums import ESV_costanza, ESV_deGroot, ESV_worldbank
from legacy.esv import forest_loss, landcover_gain
import numpy as np


class TestESV(TestCase):
    def setUp(self):
        self.gr, self.co, self.wb = ESV_deGroot, ESV_costanza, ESV_worldbank
        self.driver = np.array([0, 10, 20, 25, 30, 40, 50, 60, 70, 80, 90, 100, 255], dtype=np.uint8)

    def test_esv_groot_gain(self):
        actual = landcover_gain(
            self.driver,
            self.gr,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0, 0, 0, 473.76, 258.39, 0, 0, 0, 0, 0, 0, 0, 0])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))

    def test_esv_groot_loss(self):
        actual = forest_loss(
            self.driver,
            self.gr,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0., 473.76, 0., 473.76, 473.76, 473.76, 0., 0., 473.76, 473.76, 473.76, 0., 0.])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))

    def test_esv_costanza_gain(self):
        actual = landcover_gain(
            self.driver,
            self.co,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0, 501.03, 0, 484.38, 374.94, 0, 0, 0, 0, 599.49, 0, 0, 0])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))

    def test_esv_costanza_loss(self):
        actual = forest_loss(
            self.driver,
            self.co,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0., 484.38, 0., 484.38, 484.38, 484.38, 0., 0., 484.38, 484.38, 484.38, 0., 0.])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))

    def test_esv_worldbank_gain(self):
        actual = landcover_gain(
            self.driver,
            self.wb,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0, 0, 0, 118.08, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))

    def test_esv_worldbank_loss(self):
        actual = forest_loss(
            self.driver,
            self.wb,
            area=900,
            gl30=(10, 25, 30, 40, 70, 80, 90)
        )
        expected = np.array([0., 118.08, 0., 118.08, 118.08, 118.08, 0., 0., 118.08, 118.08, 118.08, 0., 0.])

        actual = np.round(actual)
        expected = np.round(expected)

        self.assertTrue(np.array_equal(actual, expected))
