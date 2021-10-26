
from typing import Optional, Tuple, Any
from functools import reduce

from simple_cache_sim.Cache import Cache
from simple_cache_sim.Memory import Memory
from simple_cache_sim.CPU import CPU

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
    def __init__(self, memory_size: int, cache_size: int, block_size: int, 
                 mapping_pol: int = None, replace_pol: str = "LRU", write_pol: str = "WT"):
        # self._data = dict()
        self.memory_size = memory_size
        self.cache_size = cache_size
        self.block_size = block_size

        self._data_dim = dict()
        self._start_address_in_memory = dict()

        self.last_assigned_address = 0

        self.cache = Cache(
            cache_size=cache_size, 
            block_size=block_size,
            memory_size=memory_size, 
            mapping_pol=mapping_pol,
            replace_pol=replace_pol, 
            write_pol=write_pol
        )
        self.memory = Memory(memory_size=memory_size, block_size=block_size)
        self.cpu = CPU(cache=self.cache, memory=self.memory)

    def allocate(self, *dimension: int, default_val: Any = None):
        """
        e.g. self.allocate() allocates a single value
             self.allocate(3) allocates 1-D array of size 3
             self.allocate(3, 6) allocates 2-D array of size 3x6
        """
        addr = self.last_assigned_address
        
        if dimension == ():
            self._data_dim[addr] = None
            self.last_assigned_address += 1
            self.memory.allocate(1)
            if default_val is not None:
                self.cpu.write(addr, default_val)
        else:
            sz = reduce(lambda x, y: x * y, dimension)
            self._data_dim[addr] = dimension
            self.last_assigned_address += sz
            self.memory.allocate((sz//self.block_size) + 1)
            if default_val is not None:
                for a in range(addr, addr + sz):
                    self.cpu.write(a, default_val)

        return addr

    def _get_mem_address(self, pointer: int, *idx: int):
        dim = self._data_dim[pointer]
        assert len(dim) == len(idx), "Dimension of array mismatch"
        address_in_variable = _get_flat_idx(idx, dim)
        mem_address = pointer + address_in_variable
        return mem_address

    def write(self, pointer: int, *idx: int, value: Any):
        """
        e.g. self.write(ptr, value=4) sets *ptr = 4
             self.write(ptr, 3, value=4) sets *ptr[3] = 4
             self.write(ptr, 3, 6, value=4) sets *ptr[3][6] = 4
        """
        mem_address = self._get_mem_address(pointer, *idx)
        self.cpu.write(mem_address, value)

    def increment(self, pointer: int, *idx: int, value: Any):
        """
        e.g. self.increment(ptr, value=4) sets *ptr += 4
             self.increment(ptr, 3, value=4) sets *ptr[3] += 4
             self.increment(ptr, 3, 6, value=4) sets *ptr[3][6] += 4
        """
        mem_address = self._get_mem_address(pointer, *idx)
        old_value = self.cpu.read(mem_address)
        new_value = old_value + value
        self.cpu.write(mem_address, new_value)

    def read(self, pointer: int, *idx: int):
        """
        e.g. self.read(ptr) returns value of *ptr
             self.read(ptr, 3) returns value of *ptr[3]
             self.read(ptr, 3, 6) returns value of *ptr[3][6]
        """
        mem_address = self._get_mem_address(pointer, *idx)
        return self.cpu.read(mem_address)

    def get_dimension(self, pointer: int):
        return self._data_dim[pointer]

    def get_access_summary(self):
        return {
            'cache_hits': self.cpu.hits,
            'cache_misses': self.cpu.miss,
            'total_access': self.cpu.total_access,
            'hit_rate': self.cpu.hits / self.cpu.total_access
        }

    def reset_stats(self):
        self.cpu.reset_stats()
