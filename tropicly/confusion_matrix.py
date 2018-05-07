"""
confusion_matrix.py

Author: Tobias Seydewitz
Date: 06.05.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
import pandas as pd


class ConfusionMatrix:
    def __init__(self, label):
        self._label = None
        self.label = label

        self.matrix = np.zeros((len(self.label) + 1, len(self.label) + 1), dtype=np.int)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, values):
        unique_labels = sorted(set(values))

        if len(unique_labels) < 2:
            raise ValueError

        self._label = unique_labels

    @classmethod
    def from_records(cls, records):
        reference, prediction = list(zip(*records))

        obj = cls(reference)

        for values in records:
            obj.add(*values)

        return obj

    @classmethod
    def from_lists(cls, reference, prediction):
        if len(reference) != len(prediction):
            raise ValueError

        obj = cls(reference)

        for values in zip(reference, prediction):
            obj.add(*values)

        return obj

    @classmethod
    def from_file(cls, filepath):
        pass

    def add(self, reference, prediction):
        try:
            col = self._label.index(reference)
            row = self._label.index(prediction)

            self.matrix[row][col] += 1
            self.matrix[-1][col] += 1
            self.matrix[row][-1] += 1
            self.matrix[-1][-1] += 1

        except ValueError:
            raise

    def normalize(self, method='com'):
        return _NormalizedConfusionMatrix(self.label, self.matrix)

    def as_dataframe(self):
        pass

    def __str__(self):
        return '{}'.format(self.matrix)

    def __repr__(self):
        return '<{}(label={}) at {}>'.format(self.__class__.__name__, self.label, hex(id(self)))


class _NormalizedConfusionMatrix(ConfusionMatrix):
    def __init__(self, label, matrix):
        super().__init__(label)

        self.matrix = matrix