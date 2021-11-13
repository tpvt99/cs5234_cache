from simple_cache_sim.Cache import Cache
from simple_cache_sim.Memory import Memory

import random

class CPU():
    def __init__(self, cache: Cache, memory: Memory, write_pol: str = "WT"):
        self.cache = cache
        self.memory = memory
        self.write_pol = write_pol

        self.hits = 0
        self.miss = 0
        self.total_access = 0

    def read(self, address):
        # Read a value from cache #
        cache_block = self.cache.read_from_cache(address)
        self.total_access += 1

        if cache_block is not None:
            self.hits += 1
            value = cache_block.data[self.cache.get_offset(address)]
        else:
            self.miss += 1
            cache_block = self.memory.read_block_from_memory(address)
            victim_info = self.cache.load_from_memory(address, cache_block)
            value = cache_block.data[self.cache.get_offset(address)]
            self.change_cache_size()

        return value

    def write(self, address, byte):
        """Write a byte to cache."""
        written = self.cache.overwrite_cache(address, byte)
        self.total_access += 1

        if written:
            self.hits += 1
        else:
            self.miss += 1
            block = self.memory.read_block_from_memory(address)
            block.data[self.cache.get_offset(address)] = byte
            self.cache.load_from_memory(address, block)
            self.change_cache_size()

    def reset_stats(self):
        self.total_access = 0
        self.hits = 0
        self.miss = 0

    # Do nothing as we do not change anything
    def change_cache_size(self):
        return


if __name__ == "__main__":

    mem = Memory(memory_size=2**8, block_size=2)
    cache = Cache(cache_size=2**3, block_size=2,
                  memory_size=2**8, mapping_pol=2,
                  replace_pol="LRU", write_pol="WT")
    cpu = CPU(cache, mem, write_pol="WT")

    mem.allocate(129)

    block_at_0 = mem.read_block_from_memory(0)
    block_at_1 = mem.read_block_from_memory(2)
    block_at_2 = mem.read_block_from_memory(4)
    block_at_3 = mem.read_block_from_memory(31)
    cache.load_from_memory(0, block_at_0)
    cache.load_from_memory(2, block_at_1)
    cache.load_from_memory(4, block_at_2)
    cache.load_from_memory(31, block_at_3)

    #cpu.temp_dec()

    pass
