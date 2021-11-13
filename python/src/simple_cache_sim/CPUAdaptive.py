from simple_cache_sim.Cache import Cache
from simple_cache_sim.Memory import Memory
from simple_cache_sim.CPU import CPU

import random
import math
class CPUAdaptive(CPU):
    def __init__(self, cache: Cache, memory: Memory, write_pol: str = "WT", c1=4):
        super().__init__(cache, memory, write_pol)
        self.c1 = c1
        #self.memory_profile = MemoryProfile(cache=cache, c1=c1)
        self.memory_profile = MemoryProfile2(cache=cache)

    def change_cache_size(self):
        cache_lower_limit = self.cache.map_pol * self.cache.block_size
        new_cache_size = int(self.memory_profile.get_cache_size_at_t(self.cache.cache_size))
        new_cache_size = max(new_cache_size, cache_lower_limit)
        if self.total_access % 100000 == 0:
            print(f'Iter {self.total_access} and miss {self.miss} Current cache size {new_cache_size}')
        # Step 1. Choose increase or decrease cache size
        if new_cache_size < self.cache.cache_size: # Decreasing cache size

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
        elif new_cache_size > self.cache.cache_size:

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

class MemoryProfile():
    def __init__(self, cache: Cache, c1):
        self.cache_size = cache.cache_size # Ensure cache_size = c1 * block_size^2
        self.block_size = cache.block_size
        self.m = c1 * self.block_size

    def get_cache_size_at_t(self, time_step):
        if time_step < self.m**(5/2):
            temp = self.m
        elif time_step < 2*self.m**(5/2) - self.block_size:
            temp = 2*self.m**(5/2) - time_step
        else:
            temp = self.block_size
        new_cache_size = int(math.log2(temp))
        new_cache_size = 2**new_cache_size

        return new_cache_size

class MemoryProfile2():
    def __init__(self,  cache: Cache):
        self.cache = cache
        self.cache_size = cache.cache_size  # Ensure cache_size = c1 * block_size^2
        self.block_size = cache.block_size

        self.cache_lower_limit = self.cache.map_pol * self.cache.block_size
        self.cache_upper_limit = self.cache_size

    def get_cache_size_at_t(self, current_cache_size):
        cache_decreasing_prob = 0.7
        if random.random() < cache_decreasing_prob:
            new_cache_size = current_cache_size // 2
            if new_cache_size < self.cache_lower_limit:
                return self.cache_lower_limit
            return new_cache_size
        else:
            new_cache_size = current_cache_size * 2
            if new_cache_size > self.cache_upper_limit:
                return self.cache_upper_limit
            return new_cache_size


import matplotlib.pyplot as plt

if __name__ == "__main__":

    block_size = 32
    c1=1
    cache_size = c1*block_size**2


    mem = Memory(memory_size=2**8, block_size=block_size)
    cache = Cache(cache_size=cache_size, block_size=block_size,
                  memory_size=2**8, mapping_pol=1,
                  replace_pol="LRU", write_pol="WT")
    cpu = CPUAdaptive(cache, mem, write_pol="WT", c1=c1)


    mp = MemoryProfile2(cache)
    y = []
    temp = cache.cache_size
    for t in range(100):
            temp = mp.get_cache_size_at_t(temp)
            temp = math.log2(temp)
            temp = 2**temp
            y.append(int(temp))

    fig = plt.figure()
    ax = plt.axes()
    print(y)
    ax.plot(range(100), y)
    plt.show()




