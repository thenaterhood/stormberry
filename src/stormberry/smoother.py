from collections import deque


class Smoother():

    __slots__ = ('_last_data', '_size')

    def __init__(self, size):
        self._last_data = None
        self._size = size

    def reset(self):
        self._last_data = None

    def smooth(self, value):
        if self._last_data is None:
            self._last_data = deque((value, ) * self._size, self._size)
        else:
            self._last_data.appendleft(value)

        return sum(self._last_data) / self._size
