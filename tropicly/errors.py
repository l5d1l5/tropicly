"""
Author: Tobias Seydewitz
Mail: tobi.seyde@gmail.com
"""


class TropiclyExceptions(Exception):
    """Base class for tropicly exceptions"""


class TropiclySamplingError(TropiclyExceptions):
    """Raise if sampling image dimension is != 3"""


class TropiclyConfusionMatrixError(TropiclyExceptions):
    """Common error"""


class TropiclyConfusionMatrixLabelError(TropiclyExceptions):
    """Raise if got malicious label"""
