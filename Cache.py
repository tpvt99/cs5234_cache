from Block import Block
import random
import util
from math import log
from Memory import Memory
from typing import List

class Cache():
    # Replacement policies
    LRU = "LRU"
    LFU = "LFU"
    FIFO = "FIFO"
    RAND = "RAND"

    # Mapping policies
    WRITE_BACK = "WB"
    WRITE_THROUGH = "WT"

    def __init__(self, cache_size: int, block_size: int, memory_size:int, mapping_pol: int, replace_pol: str, write_pol: str):
        '''

        :param size: cache size: number of integers to store in cache (must divide by 4 before fetching in) because each address is 4 bytes)
        '''
        self.blocks = [Block(block_size) for _ in range(cache_size//block_size)]

        self._mapping_pol = mapping_pol  # Mapping policy (1 mean direct, 2 means 2-way, n means n-way associative)
        self._replace_pol = replace_pol  # Replacement policy
        self._write_pol = write_pol  # Write policy

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
        tag = self._get_tag(address)  # Tag of cache line
        set = self._get_set(address)  # Set of cache lines
        line = None

        # Search for cache line within set
        for candidate in set:
            if candidate.tag == tag and candidate.valid:
                line = candidate
                break

        # Update use bits of cache line
        if line:
            if (self._replace_pol == Cache.LRU) or (self._replace_pol == Cache.LFU):
                self._update_use(line, set)

        return line.data if line else line

    def load_from_memory(self, address: int, data: List[int]):
        """Load a block of memory into the cache.

        :param int address: memory address for data to load to cache
        :param data: block from memory to be loaded into cache
        :return: tuple containing victim address and data (None if no victim)
        """
        tag = self._get_tag(address)  # Tag of cache line
        set = self._get_set(address)  # Set of cache lines
        victim_info = None

        # Select the victim ( victim is a block in a set)
        if (self._replace_pol == Cache.LRU or
            self._replace_pol == Cache.LFU or
            self._replace_pol == Cache.FIFO):
            victim = set[0]

            for index in range(len(set)):
                if set[index].use < victim.use:
                    victim = set[index]

            victim.use = 0

            if self._replace_pol == Cache.FIFO:
                self._update_use(victim, set)
        elif self._replace_pol == Cache.RAND:
            index = random.randint(0, self._mapping_pol - 1)
            victim = set[index]

        # Store victim info if modified
        if victim.modified:
            victim_info = (index, victim.data)

        # Replace victim
        victim.modified = 0
        victim.valid = 1
        victim.tag = tag
        victim.data = data

        return victim_info

    def overwrite_cache(self, address: int, byte: int):
        """Write a byte to cache. (the address must be a valid one which means it is loaded from the memory to cache)

        :param int address: memory address for data to write to cache
        :param int byte: byte of data to write to cache
        :return: boolean indicating whether data was written to cache
        """
        tag = self._get_tag(address)  # Tag of cache line
        set = self._get_set(address)  # Set of cache lines
        line = None

        # Search for cache line within set
        for candidate in set:
            if candidate.tag == tag and candidate.valid:
                line = candidate
                break

        # Update data of cache line
        if line:
            line.data[self.get_offset(address)] = byte
            line.modified = 1

            if (self._replace_pol == Cache.LRU or
                self._replace_pol == Cache.LFU):
                self._update_use(line, set)

        return True if line else False

    def get_offset(self, address):
        """Get the offset from within a set from a physical address.

        :param int address: memory address to get offset from
        """
        return address & (self.block_size - 1)

    def _get_tag(self, address):
        """Get the cache line tag from a physical address.

        :param int address: memory address to get tag from
        """
        return address >> self._tag_shift

    def _get_set(self, address):
        """Get a set of cache lines from a physical address.

        :param int address: memory address to get set from
        """
        set_mask = (self.cache_size // (self.block_size * self._mapping_pol)) - 1
        set_num = (address >> self._set_shift) & set_mask
        index = set_num * self._mapping_pol
        return self.blocks[index:index + self._mapping_pol]

    def print_section(self, start, amount):
        """Print a section of the cache.

        :param int start: start address to print from
        :param int amount: amount of lines to print
        """
        line_len = len(str(self.cache_size // self.block_size - 1))
        use_len = max([len(str(i.use)) for i in self.blocks])
        tag_len = int(log(self._mapping_pol * self.memory_size // self.cache_size, 2))
        address_len = int(log(self.memory_size, 2))

        if start < 0 or (start + amount) > (self.cache_size // self.block_size):
            raise IndexError

        print("\n" + " " * line_len + " " * use_len + " U M V T" +
              " " * tag_len + "<DATA @ ADDRESS>")

        for i in range(start, start + amount):
            print(util.dec_str(i, line_len) + ": ", end="")
            print(util.dec_str(self.blocks[i].use, use_len) + " ", end="") # Number of Use
            print(util.bin_str(self.blocks[i].modified, 1) + " ", end="")  # If Modified
            print(util.bin_str(self.blocks[i].valid, 1) + " ", end="") # Valid
            print(util.bin_str(self.blocks[i].tag, tag_len) + " <", end="") # Tag
            print(" ".join([util.dec_str(i, 8) for i in self.blocks[i].data]) + " @ " +
                  util.dec_str(self.get_physical_address(i), address_len) + ">")
        print()

    def get_physical_address(self, index):
        """Get the physical address of the cache line at index.

        :param int index: index of cache line to get physical address of
        :return: physical address of cache line
        """
        set_num = index // self._mapping_pol

        return ((self.blocks[index].tag << self._tag_shift) +
                (set_num << self._set_shift))


    def _update_use(self, line, set):
        """Update the use bits of a cache line.

        :param line line: cache line to update use bits of
        """
        if (self._replace_pol == Cache.LRU) or (self._replace_pol == Cache.FIFO):
            use = line.use

            if line.use < self._mapping_pol:
                line.use = self._mapping_pol
                for other in set:
                    if other is not line and other.use > use:
                        other.use -= 1
        elif self._replace_pol == Cache.LFU:
                line.use += 1


mem = Memory(memory_size=2**5, block_size=2)
cache = Cache(cache_size=2**3, block_size=2, memory_size=2**5, mapping_pol=2, replace_pol="LRU", write_pol="WR", memory=mem)

cache.load_from_memory(0)
cache.load_from_memory(2)
cache.overwrite_cache(3, 0x11ff)
cache.print_section(0, 4)