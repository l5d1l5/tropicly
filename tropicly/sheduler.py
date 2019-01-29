from multiprocessing import cpu_count
from queue import Queue
from threading import Event
from threading import Thread

from tropicly.observer import Signal


# TODO thesis


class TaskSheduler(Thread):
    def __init__(self, name, max_threads):
        super().__init__(name=name)

        self.on_progress = Signal('on progress')
        self.on_finish = Signal('on finish')
        self.on_new_task = Signal('new task')

        self.__limit = max_threads if max_threads <= cpu_count() else cpu_count()
        self.__tasks = Queue()
        self.__size = 0
        self.__active_tasks = []
        self.__internal_state = Event()
        self.__abort = False
        self.__quite = False
        self.__hard_exit = False

        self.start()

    def add_task(self, task):
        self.__tasks.put(task)
        self.__size += 1
        self.__internal_state.set()

    def add_tasks(self, tasks):
        for task in tasks:
            self.__tasks.put(task)

        self.__size += len(tasks)
        self.__internal_state.set()

    def abort(self):
        self.__abort = True

    def quite(self):
        self.__quite = True
        self.__internal_state.set()

    def hard_exit(self):
        self.__hard_exit = True
        self.__internal_state.set()

    def run(self):
        while True:
            self.__internal_state.wait()

            while self.__tasks.unfinished_tasks > 0:
                if self._start_new():
                    self._start_new_task()

                self.__active_tasks = self._get_active_tasks()

                if self.__abort or self.__hard_exit:
                    self.__abort = False
                    break

            self.__size = 0
            self.__tasks = Queue()
            self.__internal_state.clear()
            self.on_finish.fire('Returning to idle')

            if self.__hard_exit or self.__quite:
                break

    def _start_new_task(self):
        task = self.__tasks.get_nowait()
        task.start()

        self.on_new_task.fire(started=task)
        self.__active_tasks.append(task)

    def _get_active_tasks(self):
        active = []
        finished = []

        for task in self.__active_tasks:
            if task.is_alive():
                active.append(task)
            else:
                finished.append(task)
                self.__tasks.task_done()

        if finished:
            self.on_progress.fire(total=self.__size,
                                  pending=self.__tasks.unfinished_tasks,
                                  queue_size=self.__tasks.qsize(),
                                  finished=finished)

        return active

    def _start_new(self):
        if len(self.__active_tasks) <= self.__limit and not self.__tasks.empty():
            return True
        return False

    def __repr__(self):
        return '<{}(name={}, max_threads={}) at {}>'.format(self.__class__.__name__, self.name,
                                                            self.__limit, hex(id(self)))
