"""
confusion_matrix.py

Author: Tobias Seydewitz
Date: 06.05.18
Mail: tobi.seyde@gmail.com
"""
import numpy as np
from itertools import product
from collections import Counter


def confusion_matrix(reference, prediction):
    if len(reference) != len(prediction):
        raise ValueError

    labels = sorted(set(reference + prediction))
    validation = Counter(zip(reference, prediction))

    matrix = []
    for val in product(labels, repeat=2):
        ele = validation.get(val, 0)
        matrix.append(ele)

    matrix = np.reshape(matrix, (len(labels), len(labels)), order='F')
    return labels, matrix


class ConfusionMatrix(object):
    def __init__(self, labels):
        self._labels = None
        self.labels = labels

        self.matrix = np.zeros((4, 5), dtype=np.int)

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
        pass

    @classmethod
    def from_lists(cls, reference, prediction):
        pass

    @classmethod
    def from_file(cls, filepath):
        pass
