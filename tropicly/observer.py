"""
observer.py

Author: Tobias Seydewitz
Date: 09.05.18
Mail: tobi.seyde@gmail.com
"""


class Signal:
    def __init__(self, name):
        self.name = name
        self.__handler = []

    def connect(self, handler):
        if handler not in self.__handler:
            self.__handler.append(handler)

    def remove(self, handler):
        if handler in self.__handler:
            self.__handler.remove(handler)

    def fire(self, *args, **kwargs):
        for handler in self.__handler:
            handler(*args, **kwargs)

    def clear_all(self):
        self.__handler = []

    def __str__(self):
        names = [handler.__name__ for handler in self.__handler]

        return '{}(name={}, handler={})'.format(self.__class__.__name__, self.name, names)

    def __repr__(self):
        return '<{}(name={}) at {}>'.format(self.__class__.__name__, self.name, hex(id(self)))
