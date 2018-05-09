"""
sheduler.py

Author: Tobias Seydewitz
Date: 09.05.18
Mail: tobi.seyde@gmail.com
"""
from queue import Queue
from tropicly.observer import Signal
from multiprocessing import cpu_count
from threading import Thread, active_count, get_ident


class _ParallelJobShedulerBase(Thread):
    def __init__(self, name, max_threads=None):
        super().__init__(name)

        if max_threads:
            self.limit = max_threads

        else:
            self.limit = cpu_count() - (active_count() + 1)

    def run(self):
        pass


class _FiniteJobSheduler(_ParallelJobShedulerBase):
    def __init__(self, name, max_threads, jobs):
        super().__init__(name, max_threads)

        if not isinstance(jobs, Queue):
            raise ValueError

        self.jobs = jobs
        self.size = jobs.qsize()

        self.on_progress = Signal('progress')
        self.on_finish = Signal('finish')

    def progress(self, active):
        self.on_progress.fire(pending=self.jobs.qsize(),
                              total=self.size,
                              active_jobs=active)

    def run(self):
        while True:
            pass
