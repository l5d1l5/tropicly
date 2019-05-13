"""
observer
****

:Author: Tobias Seydewitz
:Date: 06.05.19
:Mail: seydewitz@pik-potsdam.de
:Institution: `Potsdam Institute for Climate Impact Research (PIK) <https://www.pik-potsdam.de/>`_
"""


class Signal:
    """ A Simple implementation of observer pattern.

    Attributes:
        name (str): Name of the signal.
    """
    def __init__(self, name=''):
        self.name = name
        self._handler = []

    def connect(self, handler):
        """Add a new signal handler.

        Args:
            handler (func): Handler function.
        """
        if handler not in self._handler:
            self._handler.append(handler)

    def remove(self, handler):
        """Remove a signal handler.

        Args:
            handler (func): Handler to remove.
        """
        if handler in self._handler:
            self._handler.remove(handler)

    def fire(self, *args, **kwargs):
        """Execute all connected handlers with args and kwargs.

        Args:
            args: Args passed to handlers.
            kwargs: Kwargs passed to handlers.
        """
        for handler in self._handler:
            handler(*args, **kwargs)

    def clear_all(self):
        """Disconnect all handlers."""
        self._handler = []

    def __str__(self):
        names = [handler.__name__ for handler in self._handler]

        return '{}(name={}, handler={})'.format(__class__.__name__, self.name, names)

    def __repr__(self):
        return '<{}(name={}) at {}>'.format(__class__.__name__, self.name, hex(id(self)))
