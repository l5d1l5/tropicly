"""
utils.py

Author: Tobias Seydewitz
Date: 20.10.17
Mail: tobi.seyde@gmail.com

Description:
"""
import os
from pathlib import Path
from collections import namedtuple


def get_data_dir(path):
    dir_structure = {
        os.path.split(root)[-1]: Path(root)
        for root, *_ in os.walk(path)
    }
    Directories = namedtuple('Directories', dir_structure.keys())
    return Directories(**dir_structure)


if __name__ == '__main__':
    pass
