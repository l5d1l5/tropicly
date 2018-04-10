"""
__init__.py

Author: Tobias Seydewitz
Date: 06.04.18
Mail: tobi.seyde@gmail.com
"""
from .sampling import worker as sworker
from .harmonization import worker as hworker


__version__ = 0.1

__all__ = [
    'hworker',
    'sworker'
]
