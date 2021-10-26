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
        else:
            self.miss += 1

            # block = self.memory.read_block_from_memory(address)
            # victim_info = self.cache.load_from_memory(address, block)
            # cache_block = self.cache.read_from_cache(address)

            cache_block = self.memory.read_block_from_memory(address)
            victim_info = self.cache.load_from_memory(address, cache_block)

            # # When reading from cache, it might be miss, then needs to read from memory.
            # # And this can overwrite content in cache. If block is modified which means it has instructions modified the content
            # # of block after accessing from memory, so we need to write this back to memory
            # # Write victim line's block to memory if replaced
            # if victim_info:
            #     self.memory.write_block_to_memory(victim_info[0], victim_info[1])


        value = cache_block.data[self.cache.get_offset(address)]

        # self.change_cache_size()

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
            # self.cache.overwrite_cache(address, byte)

        # if self.write_pol == "WT":
        #     block = self.memory.read_block_from_memory(address)
        #     block[self.cache.get_offset(address)] = byte
        #     self.memory.write_block_to_memory(address, block)

        # elif self.write_pol == "WB":
        #     if not written:
        #         block = self.memory.read_block_from_memory(address)
        #         self.cache.load_from_memory(address, block)
        #         self.cache.overwrite_cache(address, byte)
        # else:
        #     raise ValueError("Wrong writing protocol")

        # self.change_cache_size()

    def reset_stats(self):
        self.total_access = 0
        self.hits = 0
        self.miss = 0

    def change_cache_size(self):
        prob = 0.05
        if random.random() > prob:
            return

        cache_lower_limit = 2**4
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
            old_block_size = self.cache.block_size
            new_block_size = new_cache.block_size
            accepted_block_index = [random.randint(0, old_block_size) for _ in range(new_block_size)]

            # Step 2.c. For accepted block, copy to new block, if overwritten a valid line, copy back to memory
            # For rejected block, copy back to memory
            for index, line in enumerate(self.cache.blocks):
                if line.valid:
                    if index in accepted_block_index:
                        phyiscal_address = self.cache.get_physical_address(index)
                        victim_info = new_cache.load_from_memory(phyiscal_address, line.data)

                        if victim_info:
                            self.memory.write_block_to_memory(victim_info[0], victim_info[1])
                    else:
                        phyiscal_address = self.cache.get_physical_address(index)
                        self.memory.write_block_to_memory(phyiscal_address, line.data)

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
            for index, line in enumerate(self.cache.blocks):
                if line.valid:
                    phyiscal_address = self.cache.get_physical_address(index)
                    victim_info = new_cache.load_from_memory(phyiscal_address, line.data)

                    # A protective condition (this should not be called)
                    if victim_info:
                        self.memory.write_block_to_memory(victim_info[0], victim_info[1])

            # Step 3.c. Update cache
            self.cache = new_cache

    def temp_dec(self):
        cache_lower_limit = 2 ** 2
        cache_upper_limit = 2 ** 12

        current_cache_size = self.cache.cache_size
        new_cache_size = current_cache_size // 2
        if new_cache_size < cache_lower_limit:
            return
        # Step 2.b creating new cache
        new_cache = Cache(cache_size=new_cache_size, block_size=self.cache.block_size,
                          memory_size=self.cache.memory_size, mapping_pol=self.cache.map_pol,
                          write_pol=self.cache.wri_pol, replace_pol=self.cache.rep_pol)
        # Step 2.b. Choose block index that go to new cache and block index that to be discarded
        old_block_size = self.cache.block_size
        new_block_size = new_cache.block_size
        accepted_block_index = [0,2]

        # Step 2.c. For accepted block, copy to new block, if overwritten a valid line, copy back to memory
        # For rejected block, copy back to memory
        for index, line in enumerate(self.cache.blocks):
            if index in accepted_block_index:
                phyiscal_address = self.cache.get_physical_address(index)
                victim_info = new_cache.load_from_memory(phyiscal_address, line.data)

                if victim_info:
                    self.memory.write_block_to_memory(victim_info[0], victim_info[1])
            else:
                phyiscal_address = self.cache.get_physical_address(index)
                self.memory.write_block_to_memory(phyiscal_address, line.data)

        # Step 2.d. Update cache
        self.cache = new_cache

if __name__ == "__main__":

    mem = Memory(memory_size=2**8, block_size=2)
    cache = Cache(cache_size=2**3, block_size=2,
                  memory_size=2**8, mapping_pol=1,
                  replace_pol="LRU", write_pol="WT")
    cpu = CPU(cache, mem, write_pol="WT")

    block_at_0 = mem.read_block_from_memory(0)
    block_at_1 = mem.read_block_from_memory(2)
    block_at_2 = mem.read_block_from_memory(4)
    block_at_3 = mem.read_block_from_memory(6)
    cache.load_from_memory(0, block_at_0)
    cache.load_from_memory(2, block_at_1)
    cache.load_from_memory(4, block_at_2)
    cache.load_from_memory(6, block_at_3)

    cpu.temp_dec()

    pass
