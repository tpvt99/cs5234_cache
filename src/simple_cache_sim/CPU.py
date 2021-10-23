from src.simple_cache_sim.Cache import Cache
from src.simple_cache_sim.Memory import Memory

class CPU():
    def __init__(self, cache: Cache, memory: Memory, write_pol: str):
        self.cache = cache
        self.memory = memory
        self.write_pol = write_pol

        self.hits = 0
        self.miss = 0
        self.total_access = 0

    def read(self, address):
        # Read a value from cache#
        cache_block = self.cache.read_from_cache(address)
        self.total_access += 1

        if cache_block:
            self.hits += 1
        else:
            self.miss += 1

            block = self.memory.read_from_memory(address)
            victim_info = self.cache.load_from_memory(address, block)
            cache_block = self.cache.read_from_cache(address)

            # Write victim line's block to memory if replaced
            # if victim_info:
            #     self.memory.write_to_memory(victim_info[0], victim_info[1])

        return cache_block[self.cache.get_offset(address)]

    def write(self, address, byte):
        """Write a byte to cache."""
        written = self.cache.overwrite_cache(address, byte)
        self.total_access += 1

        if written:
            self.hits += 1
        else:
            self.miss += 1

        if self.write_pol == "WT":
            block = self.memory.read_from_memory(address)
            block[self.cache.get_offset(address)] = byte
            self.memory.write_to_memory(address, block)

        elif self.write_pol == "WB":
            if not written:
                block = self.memory.read_from_memory(address)
                self.cache.load_from_memory(address, block)
                self.cache.overwrite_cache(address, byte)
        else:
            raise ValueError("Wrong writing protocol")
