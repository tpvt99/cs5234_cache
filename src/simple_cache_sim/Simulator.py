
from typing import Optional, Tuple, Any
from functools import reduce

from src.simple_cache_sim.Cache import Cache
from src.simple_cache_sim.Memory import Memory
from src.simple_cache_sim.CPU import CPU

import time

def _get_flat_idx(idx: Tuple[int, ...], dimension: Tuple[int, ...]):
    p = 1
    idx_flat = 0
    for i, d in zip(reversed(idx), reversed(dimension)):
        assert 0 <= i < d, "Index must be at least 0 and less than dimension size"
        idx_flat += i * p
        p *= d
    return idx_flat

class Simulator():
    def __init__(self, memory_size: int, cache_size: int, block_size: int, writing_policy: str,
                 replacement_policy: str):
        # self._data = dict()

        self._data_dim = dict()
        self._start_address_in_memory = dict()

        self.last_assigned_address = 0

        begin = time.time()
        self.cache = Cache(cache_size=cache_size, block_size=block_size,
                      memory_size=memory_size, mapping_pol=1,
                      replace_pol=replacement_policy, write_pol=writing_policy)
        self.memory = Memory(memory_size=memory_size, block_size=block_size)
        self.cpu = CPU(cache=self.cache, memory=self.memory, write_pol=writing_policy)
        end = time.time()
        print(f"Initialization time: {end-begin}s")

    def allocate(self, variable: str, *dimension: int, default_val: Any = None):
        """
        e.g. self.allocate("A") allocates a single value for A
             self.allocate("A", 3) allocates 1-D array of size 3 called A
             self.allocate("A", 3, 6) allocates 2-D array of size 3x6 called A
        """
        if dimension == ():
            self._data_dim[variable] = None
        else:
            self._data_dim[variable] = dimension

        if variable not in self._start_address_in_memory.keys():
            self._start_address_in_memory[variable] = self.last_assigned_address
            self.last_assigned_address += reduce(lambda x, y: x * y, dimension)

    def write(self, variable: str, *idx: int, value: Any):
        """
        e.g. self.write("A", value=4) sets A = 4
             self.write("A", 3, value=4) sets A[3] = 4
             self.write("A", 3, 6, value=4) sets A[3][6] = 4
        """

        dim = self._data_dim[variable]
        assert len(dim) == len(idx), "Dimension of array mismatch"
        address_in_variable = _get_flat_idx(idx, dim)
        mem_address = self._start_address_in_memory[variable] + address_in_variable
        self.cpu.write(mem_address, value)

    def increment(self, variable: str, *idx: int, value: Any):
        """
        e.g. self.write("A", value=4) sets A = 4
             self.write("A", 3, value=4) sets A[3] = 4
             self.write("A", 3, 6, value=4) sets A[3][6] = 4
        """

        dim = self._data_dim[variable]
        assert len(dim) == len(idx), "Dimension of array mismatch"
        address_in_variable = _get_flat_idx(idx, dim)
        mem_address = self._start_address_in_memory[variable] + address_in_variable

        old_value = self.cpu.read(mem_address)
        new_value = old_value + value
        self.cpu.write(mem_address, new_value)

    def read(self, variable: str, *idx: int):
        """
        e.g. self.read("A") returns value of A
             self.read("A", 3) returns value of A[3]
             self.read("A", 3, 6) returns value of A[3][6]
        """

        dim = self._data_dim[variable]
        assert len(dim) == len(idx), "Dimension of array mismatch"
        address_in_variable = _get_flat_idx(idx, dim)
        mem_address = self._start_address_in_memory[variable] + address_in_variable

        return self.cpu.read(mem_address)

    def get_dimension(self, variable: str):
        return self._data_dim[variable]