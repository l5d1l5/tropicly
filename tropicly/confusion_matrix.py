"""
confusion_matrix.py

Author: Tobias Seydewitz
Date: 06.05.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np


class ConfusionMatrix(object):
    def __init__(self, labels):
        self._labels = None
        self.labels = labels

        self.matrix = np.zeros((len(self.labels)+1, len(self.labels)+1), dtype=np.int)

    @property
    def labels(self):
        return self._labels

    @labels.setter
    def labels(self, values):
        unique_labels = sorted(set(values))

        if len(unique_labels) < 2:
            raise ValueError

        self._labels = unique_labels

    @classmethod
    def from_records(cls, records):
        reference, prediction = list(zip(*records))

        obj = cls(reference + prediction)

        for values in records:
            obj.add(*values)

        return obj

    @classmethod
    def from_lists(cls, reference, prediction):
        if len(reference) != len(prediction):
            raise ValueError

        obj = cls(reference + prediction)

        for values in zip(reference, prediction):
            obj.add(*values)

        return obj

    @classmethod
    def from_file(cls, filepath):
        pass

    def add(self, reference, prediction):
        try:
            col = self._labels.index(reference)
            row = self._labels.index(prediction)

            self.matrix[row][col] += 1
            self.matrix[-1][col] += 1
            self.matrix[row][-1] += 1
            self.matrix[-1][-1] += 1

        except ValueError:
            raise
