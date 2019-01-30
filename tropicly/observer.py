# TODO doc


class Signal:
    """
    Simple implementation of observer pattern.

    Example:
        class Observable:
            def __init__(self):
                self.on_action = Signal('on_action')
            def method(self):
                self.on_action.fire(*args, **kwargs)

        callback(*args, **kwargs):
            print(*args, **kwargs)

        obj = Observable()
        obj.on_action.connect(callback)
    """
    def __init__(self, name=''):
        """
        Signal constructor.

        :param name: str
            Signal name.
        """
        self.name = name
        self.__handler = []

    def connect(self, handler):
        """
        Add a new signal handler.

        :param handler: function or method
        """
        if handler not in self.__handler:
            self.__handler.append(handler)

    def remove(self, handler):
        """
        Remove a signal handler.

        :param handler: function or method
        """
        if handler in self.__handler:
            self.__handler.remove(handler)

    def fire(self, *args, **kwargs):
        """
        Execute all connected handlers.

        :param args:
            Handler arguments.
        :param kwargs:
            Handler key word arguments.
        """
        for handler in self.__handler:
            handler(*args, **kwargs)

    def clear_all(self):
        """
        Disconnect all handlers.
        """
        self.__handler = []

    def __str__(self):
        names = [handler.__name__ for handler in self.__handler]

        return '{}(name={}, handler={})'.format(self.__class__.__name__, self.name, names)

    def __repr__(self):
        return '<{}(name={}) at {}>'.format(self.__class__.__name__, self.name, hex(id(self)))
