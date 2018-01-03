"""
utils.py

Author: Tobias Seydewitz
Date: 20.10.17
Mail: tobi.seyde@gmail.com

Description:
"""
import os
import time
from pathlib import Path
from collections import namedtuple
from contextlib import contextmanager


def get_data_dir(path: str) -> namedtuple:
    dir_structure = {
        os.path.split(root)[-1]: Path(root)
        for root, *_ in os.walk(path)
    }
    Directories = namedtuple('Directories', dir_structure.keys())
    return Directories(**dir_structure)


@contextmanager
def benchmark_context():
    start = time.time()
    try:
        yield None
    finally:
        print(time.time() - start)


if __name__ == '__main__':
    pass
