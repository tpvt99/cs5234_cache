import random
from math import log
from typing import List
from collections import OrderedDict

from simple_cache_sim import util
from simple_cache_sim.Memory import Memory
from simple_cache_sim.Block import Block
from simple_cache_sim.update_policies import LRUPolicy, LFUPolicy, FIFOPolicy, RandomPolicy


class Cache():
    # Replacement policies
    LRU = "LRU"
    LFU = "LFU"
    FIFO = "FIFO"
    RAND = "RAND"

    # Mapping policies
    WRITE_BACK = "WB"
    WRITE_THROUGH = "WT"

    def __init__(self, cache_size: int, block_size: int, memory_size: int, 
                 mapping_pol: int = None, replace_pol: str = "LRU", write_pol: str = "WT"):
        '''

        :param size: cache size: number of integers to store in cache (must divide by 4 before fetching in) because each address is 4 bytes)
        '''
        # self.blocks = [Block(block_size) for _ in range(cache_size//block_size)]

        self.cache_blocks = cache_size//block_size
        # Mapping policy (1 mean direct, 2 means 2-way, n means n-way associative)
        self._mapping_pol = self.cache_blocks if mapping_pol is None else mapping_pol
        self._replace_pol = replace_pol  # Replacement policy
        self._write_pol = write_pol  # Write policy

        self.num_sets = self.cache_blocks // self._mapping_pol
        self.blocks = [dict() for _ in range(self.num_sets)]
        replace_pol = replace_pol.lower()
        if replace_pol == "lru":
            Pol = LRUPolicy
        elif replace_pol == "lfu":
            Pol = LFUPolicy
        elif replace_pol == "fifo":
            Pol = FIFOPolicy
        elif replace_pol.startswith("rand"):
            Pol = RandomPolicy
        else:
            raise ValueError(f'Invalid eviction policy: {replace_pol}')
        self.eviction_handler = [Pol(self._mapping_pol) for _ in range(self.num_sets)]

        self.map_pol = self._mapping_pol # These 3 lines are hilarious, just expose the protected attributes
        self.rep_pol = self._replace_pol
        self.wri_pol = self._write_pol

        self.cache_size = cache_size  # Cache size
        self.memory_size = memory_size  # Memory size
        self.block_size = block_size  # Block size

        # Bit offset of cache line tag
        self._tag_shift = int(log(self.cache_size // self._mapping_pol, 2))
        # Bit offset of cache line set
        self._set_shift = int(log(self.block_size, 2))


    def read_from_cache(self, address):
        """Read a block of memory from the cache.

        :param int address: memory address for data to read from cache
        :return: block of memory read from the cache (None if cache miss)
        """
        cache_tag = self._get_tag(address)  # Tag of cache line
        cache_set = self._get_set(address)  # Set of cache lines

        # Search for cache line within set
        if cache_tag in self.blocks[cache_set].keys():
            line = self.blocks[cache_set][cache_tag]
            self.eviction_handler[cache_set].update_access(cache_tag)
            return line.data
        else:
            return None

    def load_from_memory(self, address: int, data: Block):
        """Load a block of memory into the cache.

        :param int address: memory address for data to load to cache
        :param data: block from memory to be loaded into cache
        :return: tuple containing victim address and data (None if no victim)
        """
        cache_tag = self._get_tag(address)  # Tag of cache line
        cache_set = self._get_set(address)  # Set of cache lines

        # Select the victim (victim is a block in a set)
        if self.eviction_handler[cache_set].is_full():
            victim_tag = self.eviction_handler[cache_set].remove_one()
            self.blocks[cache_set].pop(victim_tag)

        # Store new block instead
        self.eviction_handler[cache_set].add_in(cache_tag)
        self.blocks[cache_set][cache_tag] = data
        

    def overwrite_cache(self, address: int, byte: int):
        """Write a byte to cache. (the address must be a valid one which means it was loaded from the memory to cache)

        :param int address: memory address for data to write to cache
        :param int byte: byte of data to write to cache
        :return: boolean indicating whether data was written to cache
        """
        cache_tag = self._get_tag(address)  # Tag of cache line
        cache_set = self._get_set(address)  # Set of cache lines

        if cache_tag in self.blocks[cache_set].keys():
            line = self.blocks[cache_set][cache_tag]
            line.data[self.get_offset(address)] = byte
            self.eviction_handler[cache_set].update_access(cache_tag)
            return True
        else:
            return False

    def get_offset(self, address):
        """Get the offset from within a set from a physical address. (position of physical address inside block)
        e.g., block_size = 4, then add = 0 -> offset =0, add = 1 -> offset = 1, add=4 -> offset = 0, add = 5 -> offset = 1

        :param int address: memory address to get offset from
        """
        return address & (self.block_size - 1)

    def _get_tag(self, address):
        """Get the cache line tag from a physical address.
        e.g., cache_size = 32: then add = 0 -> tag = 0, add = 31-> tag = 0, add=32 -> tag = 1, add = 33 -> tag = 1; add 64 -> tag = 2

        :param int address: memory address to get tag from
        """
        return address >> self._tag_shift

    def _get_set(self, address):
        """Get a set of cache lines from a physical address.

        :param int address: memory address to get set from
        """
        set_mask = (self.cache_size // (self.block_size * self._mapping_pol)) - 1
        set_num = (address >> self._set_shift) & set_mask
        return set_num

    def get_physical_address(self, cache_tag, cache_set):
        """Get the physical address of the cache line at index.

        :param int index: index of cache line to get physical address of
        :return: physical address of cache line
        """

        return ((cache_tag << self._tag_shift) +
                (cache_set << self._set_shift))


if __name__ == "__main__":

    mem = Memory(memory_size=2**8, block_size=4)
    cache = Cache(cache_size=2**8, block_size=1,
                  memory_size=2**8, mapping_pol=None,
                  replace_pol="LRU", write_pol="WT")

    block_at_0 = mem.read_block_from_memory(0)
    block_at_2 = mem.read_block_from_memory(2)
    cache.load_from_memory(2, block_at_2)
    pass
