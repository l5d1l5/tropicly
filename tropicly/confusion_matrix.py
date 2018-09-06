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
    """
    A simple class to build a confusion matrix for classification
    accuracy assessment.
    """
    def __init__(self, label, dtype=np.int):
        """
        Instance constructor, creates a confusion matrix in dimension of
        NxN derived from length label.

        :param label: list of int, char
            Classification labels/classes.
        :param dtype: optional, np.dtype
            You should not change this value.
        """
        self._label = sorted(set(label))

        if len(self._label) < 2:
            raise ConfusionMatrixLabelError('Minimal requirement is 2 independent labels.')

        self._matrix = np.zeros((len(self._label) + 1, len(self._label) + 1), dtype=dtype)

    @classmethod
    def from_records(cls, records):
        """
        Alternative class constructor returns a instance from ConfusionMatrix.
        Creates a instance from a list of reference and prediction tuples.
        Labels/classes are initialized from a list of all reference values.

        :param records: list of tuple(reference, prediction)
            Classification label.
        :return: ConfusionMatrix
            The instance.
        """
        reference, prediction = list(zip(*records))

        obj = cls(reference)

        for values in records:
            obj.add(*values)

        return obj

    @classmethod
    def from_lists(cls, reference, prediction):
        """
        Alternative class constructor returns a instance from ConfusionMatrix.
        Creates a instance from a list of reference values and a list of prediction
        values. Labels/classes are initialized from the reference values.

        :param reference: list
            Reference labels.
        :param prediction: list
            Predicted labels.
        :return: ConfusionMatrix
            The instance.
        """
        if len(reference) != len(prediction):
            raise ValueError

        obj = cls(reference)

        for values in zip(reference, prediction):
            obj.add(*values)

        return obj

    def add(self, reference, prediction):
        """
        Adds to the confusion matrix a reference prediction value pair.

        :param reference:
            Reference label/class.
        :param prediction:
            Predicted label/class.
        """
        if reference not in self._label or prediction not in self._label:
            msg = '{}, {} unknown label for {}.'.format(reference, prediction, self._label)
            raise ConfusionMatrixLabelError(msg)

        col = self._label.index(reference)
        row = self._label.index(prediction)

        self._matrix[row][col] += 1
        self._matrix[-1][col] += 1
        self._matrix[row][-1] += 1
        self._matrix[-1][-1] += 1

    def normalize(self, method='commission'):
        """
        Returns a instance of NormalizedConfusion matrix. Parameter
        method selects the method of normalization. Select commission for
        a commission error matrix and omission for omission matrix.
        Default is commission.

        :param method: optional, str
            Select the normalization method. Options:
            commission (c, co, com, commission)
            or omission.
        :return: NormalizedConfusionMatrix
            A instance of NormalizedConfusionMatrix.
        """
        if method in ('c', 'co', 'com', 'commission'):
            mat = self._matrix.T
            ncm = _NormalizedConfusionMatrix(self._label, 'commission')

        else:
            mat = self._matrix
            ncm = _NormalizedConfusionMatrix(self._label, 'omission')

        for idx, val in enumerate(mat[:-1]):
            ncm.add(val, idx)

        return ncm

    def as_dataframe(self):
        """
        Returns the confusion matrix as a pandas.DataFrame object.

        :return: pandas.DataFrame
            A pandas data frame.
        """
        return pd.DataFrame.from_records(self._matrix,
                                         index=self._label + ['cc'],
                                         columns=self._label + ['rc'])

    def as_tex_string(self):
        """
        Returns the confusion matrix as a tex table string.

        :return: str
            A tex table string.
        """
        matrix = np.vstack((
            np.array(self._label + ['total'], dtype=np.str),
            self._matrix.astype(np.str)
        ))
        matrix = np.hstack((
            np.array([' '] + self._label + ['total'], dtype=np.str).reshape((len(self._label)+2, 1)),
            matrix
        ))

        return ' \\\\ \n'.join([' & '.join(row) for row in matrix])

    def __str__(self):
        # TODO implement
        """
        rows/columns/cells = matrix_size + 1
        cell_size = 2 + max digits
        line_length = cells*cell_size + cells + 1
        -----------------------------
        |      |   10 |   20 |      |
        -----------------------------
        |   10 | 1000 |   10 | 1010 |
        -----------------------------
        |   20 |   20 | 1000 | 1020 |
        -----------------------------
        |      | 1020 | 1010 | 2030 |
        -----------------------------
        """
        return '{}'.format(self._matrix)

    def __repr__(self):
        return '<{}(label={}) at {}>'.format(self.__class__.__name__, self._label, hex(id(self)))


class _NormalizedConfusionMatrix(ConfusionMatrix):
    """
    Private class, please derive a instance of this class with
    ConfusionMatrix.normalize.
    """
    def __init__(self, label, method, dtype=np.float):
        """
        Not intended for direct instantiation. Please, use ConfusionMatrix.

        :param label: list
            Label/class
        :param method: str
            Commission or else
        :param dtype:
            Don't change cause normalization are type float.
        """
        super().__init__(label, dtype)

        self._method = method
        self._positive = 0
        self._population = 0

    def add(self, values, index):
        # TODO prevent division by zero
        """
        Adds a normalized row to matrix.

        :param values: list
            Row of a confusion matrix,
            must contain as last value row count.
        :param index: int
            Where reference_label == prediction_label or
            true positive index.
        """
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
                self._matrix[idx][index] = val

        else:
            self._matrix[index] = rates

        # update overall accuracy
        self._matrix[-1][-1] = round(self._positive / self._population, 2)

    def __repr__(self):
        return '<{}(label={}, method={}) at {}>'.format(self.__class__.__name__, self._label,
                                                        self._method, hex(id(self)))
