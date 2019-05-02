"""
test_raster.py

Author: Tobias Seydewitz
Date: 02.05.19
Mail: seydewitz@pik-potsdam.de
Institution: Potsdam Institute for Climate Impact Research
"""
from unittest import TestCase
from tropicly.raster import orient_to_int


class TestRaster(TestCase):
    def test_orient_to_int(self):
        self.assertEqual([-10, -90], orient_to_int('010W', '90S'))
        self.assertEqual([10, 90], orient_to_int('010E', '90N'))
        self.assertEqual([-10, 90], orient_to_int('010W', '90N'))
        self.assertEqual([-10, 90], orient_to_int('010___W__414sad', '___000090__N__123213ad'))
