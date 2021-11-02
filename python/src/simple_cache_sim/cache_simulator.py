from typing import Optional, Tuple, Any
from functools import reduce


def _get_flat_idx(idx: Tuple[int, ...], dimension: Tuple[int, ...]):
    p = 1
    idx_flat = 0
    for i, d in zip(reversed(idx), reversed(dimension)):
        assert 0 <= i < d, "Index must be at least 0 and less than dimension size"
        idx_flat += i * p
        p *= d
    return idx_flat


class CacheSimulator:

    def __init__(self):
        self._data = dict()
        self._data_dim = dict()

    def allocate(self, variable: str, *dimension: int, default_val: Any = None):
        """
        e.g. self.allocate("A") allocates a single value for A
             self.allocate("A", 3) allocates 1-D array of size 3 called A
             self.allocate("A", 3, 6) allocates 2-D array of size 3x6 called A
        """
        if dimension == ():
            self._data[variable] = default_val
            self._data_dim[variable] = None
        else:
            self._data[variable] = [default_val for _ in range(reduce(lambda x, y: x * y, dimension))]
            self._data_dim[variable] = dimension

    def write(self, variable: str, *idx: int, value: Any):
        """
        e.g. self.write("A", value=4) sets A = 4
             self.write("A", 3, value=4) sets A[3] = 4
             self.write("A", 3, 6, value=4) sets A[3][6] = 4
        """
        if idx == ():
            assert self._data_dim[variable] is None, "Accessing array requires an index."
            self._data[variable] = value
        else:
            dim = self._data_dim[variable]
            assert len(dim) == len(idx), "Dimension of array mismatch"
            self._data[variable][_get_flat_idx(idx, dim)] = value

    def increment(self, variable: str, *idx: int, value: Any):
        """
        e.g. self.write("A", value=4) sets A = 4
             self.write("A", 3, value=4) sets A[3] = 4
             self.write("A", 3, 6, value=4) sets A[3][6] = 4
        """
        if idx == ():
            assert self._data_dim[variable] is None, "Accessing array requires an index."
            self._data[variable] += value
        else:
            dim = self._data_dim[variable]
            assert len(dim) == len(idx), "Dimension of array mismatch"
            self._data[variable][_get_flat_idx(idx, dim)] += value

    def read(self, variable: str, *idx: int):
        """
        e.g. self.read("A") returns value of A
             self.read("A", 3) returns value of A[3]
             self.read("A", 3, 6) returns value of A[3][6]
        """
        if idx == ():
            assert self._data_dim[variable] is None, "Accessing array requires an index."
            return self._data[variable]
        else:
            dim = self._data_dim[variable]
            assert len(dim) == len(idx), "Dimension of array mismatch"
            return self._data[variable][_get_flat_idx(idx, dim)]

    def get_dimension(self, variable: str):
        return self._data_dim[variable]

    def get_cache_summary(self):
        pass
