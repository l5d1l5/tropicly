"""
confusion_matrix.py

Author: Tobias Seydewitz
Date: 06.05.18
Mail: tobi.seyde@gmail.com
"""
import logging
import numpy as np
import pandas as pd


LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.NullHandler())


class ConfusionMatrixBaseError(Exception):
    """Base class"""


class ConfusionMatrixLabelError(ConfusionMatrixBaseError):
    """Error for malicious label"""


class ConfusionMatrix:
    def __init__(self, label, dtype=np.int):
        self._label = None
        self.label = label

        self.matrix = np.zeros((len(self.label) + 1, len(self.label) + 1), dtype=dtype)

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, values):
        unique_labels = sorted(set(values))

        if len(unique_labels) < 2:
            raise ConfusionMatrixLabelError('Minimal requirement is 2 labels.')

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

    def add(self, reference, prediction):
        if reference not in self.label or prediction not in self.label:
            msg = '{}, {} unknown label for {}.'.format(reference, prediction, self.label)
            raise ConfusionMatrixLabelError(msg)

        col = self._label.index(reference)
        row = self._label.index(prediction)

        self.matrix[row][col] += 1
        self.matrix[-1][col] += 1
        self.matrix[row][-1] += 1
        self.matrix[-1][-1] += 1

    def normalize(self, method='commission'):
        if method in ('c', 'co', 'com', 'commission'):
            mat = self.matrix.T
            ncm = _NormalizedConfusionMatrix(self.label, 'commission')

        else:
            mat = self.matrix
            ncm = _NormalizedConfusionMatrix(self.label, 'omission')

        for idx, val in enumerate(mat[:-1]):
            ncm.add(val, idx)

        return ncm

    def as_dataframe(self):
        pass

    def __str__(self):
        return '{}'.format(self.matrix)

    def __repr__(self):
        return '<{}(label={}) at {}>'.format(self.__class__.__name__, self.label, hex(id(self)))


class _NormalizedConfusionMatrix(ConfusionMatrix):
    def __init__(self, label, method, dtype=np.float):
        super().__init__(label, dtype)

        self._method = method
        self._positive = 0
        self._population = 0

    def add(self, values, index):
        # cache for overall accuracy
        self._positive += values[index]
        self._population += values[-1]

        rates = [
            round(val / values[-1], 2)
            for idx, val in enumerate(values[:-1])
        ]
        rates.append(round((sum(values[:-1]) - values[index]) / values[-1], 2))

        if self._method == 'commission':
            for idx, val in enumerate(rates):
                self.matrix[idx][index] = val

        else:
            self.matrix[index] = rates

        # update overall accuracy
        self.matrix[-1][-1] = round(self._positive / self._population, 2)

    def __repr__(self):
        return '<{}(label={}, method={}) at {}>'.format(self.__class__.__name__, self.label,
                                                        self._method, hex(id(self)))
