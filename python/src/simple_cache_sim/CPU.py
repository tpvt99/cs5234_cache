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

    def change_cache_size(self):
        prob = 0.1
        if random.random() > prob:
            return

        cache_lower_limit = self.cache.map_pol * self.cache.block_size
        cache_upper_limit = 2**12
        # Step 1. Choose increase or decrease cache size
        prob = 0.5
        if random.random() < prob: # Decreasing cache size
            # Step 2.a Decreasing cache size by factor of 2
            current_cache_size = self.cache.cache_size
            new_cache_size = current_cache_size//2
            if new_cache_size < cache_lower_limit:
                return
            # Step 2.b creating new cache
            new_cache = Cache(cache_size=new_cache_size, block_size=self.cache.block_size,
                              memory_size=self.cache.memory_size, mapping_pol=self.cache.map_pol,
                              write_pol=self.cache.wri_pol, replace_pol=self.cache.rep_pol)
            # Step 2.b. Choose block index that go to new cache and block index that to be discarded
            old_block_size = len(self.cache.blocks)
            new_block_size = len(new_cache.blocks)
            accepted_block_index = random.sample(range(old_block_size), k=new_block_size)

            # Step 2.c. For accepted block, copy to new block, if overwritten a valid line, copy back to memory
            # For rejected block, copy back to memory
            for cache_set, line in enumerate(self.cache.blocks):
                if cache_set in accepted_block_index:
                    for cache_tag, block in line.items():
                        phyiscal_address = self.cache.get_physical_address(cache_tag, cache_set)
                        new_cache.load_from_memory(phyiscal_address, block)

            # Step 2.d. Update cache
            self.cache = new_cache

        else:
            current_cache_size = self.cache.cache_size
            new_cache_size = current_cache_size * 2
            if new_cache_size > cache_upper_limit:
                return

            # Step 3.a Creating a new cache
            new_cache = Cache(cache_size=new_cache_size, block_size=self.cache.block_size,
                              memory_size=self.cache.memory_size, mapping_pol=self.cache.map_pol,
                              write_pol=self.cache.wri_pol, replace_pol=self.cache.rep_pol)
            # Step 3.b Copy from old cache to new cache
            for cache_set, line in enumerate(self.cache.blocks):
                for cache_tag, block in line.items():
                    phyiscal_address = self.cache.get_physical_address(cache_tag, cache_set)
                    new_cache.load_from_memory(phyiscal_address, block)

            # Step 3.c. Update cache
            self.cache = new_cache

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
