"""
sheduler.py

Author: Tobias Seydewitz
Date: 09.05.18
Mail: tobi.seyde@gmail.com
"""
from queue import Queue
from tropicly.observer import Signal
from multiprocessing import cpu_count
from threading import Thread, active_count, TIMEOUT_MAX
import random


class _ParallelJobShedulerBase(Thread):
    def __init__(self, name, max_threads=None):
        super().__init__(name=name)

        if max_threads:
            self.limit = max_threads

        else:
            self.limit = cpu_count() - (active_count() + 1)

    def run(self):
        pass


class FiniteJobSheduler(_ParallelJobShedulerBase):
    def __init__(self, name, max_threads, jobs):
        super().__init__(name, max_threads)

        if not isinstance(jobs, Queue):
            raise ValueError

        self.tasks = jobs
        self.size = jobs.qsize()

        self.on_progress = Signal('on progress')
        self.on_finish = Signal('on finish')
        self.on_new_task = Signal('new task')

        self.__active_tasks = []

    def run(self):
        while True:
            if self._can_start_new_task():
                task = self.tasks.get_nowait()
                task.start()

                self.on_new_task.fire(task)
                self.__active_tasks.append(task)

            self.__active_tasks = [task for task in self.__active_tasks if task.is_alive()]

            if self._finished():
                self.on_finish.fire()
                break

    def _finished(self):
        if not self.__active_tasks and self.tasks.empty():
            return True
        return False

    def _can_start_new_task(self):
        if len(self.__active_tasks) <= self.limit and not self.tasks.empty():
            return True
        return False

    def __repr__(self):
        return '<{}(name={}, max_threads={}) at {}>'.format(self.__class__.__name__, self.name,
                                                            self.limit, hex(id(self)))


def matrix_sum(n):
    a = [[random.randint(1, 10) for i in range(n)] for i in range(n)]

    for ridx, row in enumerate(a):
        for cidx, val in enumerate(row):
            a[ridx][cidx] = val + val


def callback(task):
    print(task.name)


if __name__ == '__main__':
    q = Queue()
    for i in range(100):
        t = Thread(target=matrix_sum, args=(100,))
        q.put(t)

    s = FiniteJobSheduler('bal', 4, q)
    s.start()

