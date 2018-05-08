from unittest import TestCase
import numpy as np
from tropicly.confusion_matrix import ConfusionMatrix


class TestConfusionMatrix(TestCase):
    def setUp(self):
        self.char_cm = ConfusionMatrix(['a', 'b', 'c'])
        self.digi_cm = ConfusionMatrix([10, 20, 30])

        self.reference = [10]*19 + [20]*12 + [30]*13
        self.prediction = [10] * 10 + [20] * 8 + [30, 10] + [20] * 10 + [30, 10, 10, 10] + [30] * 10

        self.records = list(zip(self.reference, self.prediction))

        self.expected = np.array([[10, 1, 3, 14],
                                  [8, 10, 0, 18],
                                  [1, 1, 10, 12],
                                  [19, 12, 13, 44]], dtype=np.int)

    def test_confusionMatrix_from_records(self):
        cm = ConfusionMatrix.from_records(self.records)

        self.assertTrue(np.array_equal(self.expected, cm.matrix))

    def test_confusionMatrix_from_lists(self):
        cm = ConfusionMatrix.from_lists(self.reference, self.prediction)

        self.assertTrue(np.array_equal(self.expected, cm.matrix))

    def test_confusionMatrix_with_char_labels(self):
        ref = np.array(self.reference, dtype=np.unicode)
        pre = np.array(self.prediction, dtype=np.unicode)

        ref[ref == '10'] = 'A'
        ref[ref == '20'] = 'B'
        ref[ref == '30'] = 'C'
        pre[pre == '10'] = 'A'
        pre[pre == '20'] = 'B'
        pre[pre == '30'] = 'C'

        cm = ConfusionMatrix.from_lists(ref, pre)

        self.assertTrue(np.array_equal(self.expected, cm.matrix))

    def test_add(self):
        self.fail()

    def test_normalize(self):
        self.fail()

    def test_as_dataframe(self):
        self.fail()
