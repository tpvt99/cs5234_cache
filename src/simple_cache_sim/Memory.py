from typing import List

from simple_cache_sim import util


class Memory():
    def __init__(self, memory_size, block_size):
        '''
        Size of each value (per address) is 4 bytes to store enough an integer
        If memory_size and block_size is bytes, please divide by 4 before fetching into this Memory
        because each address is 4 bytes

        :param memory_size: memory size (in 4*Bytes)
        :param block_size: block size (in 4*Bytes)
        '''
        self.memory_size = memory_size
        self.block_size = block_size

        self.memory_data = [util.rand_byte() for i in range(self.memory_size)]

    def print_section(self, start, amount):
        """Print a section of main memory by decimal forms.

        :param int start: start address to print from
        :param int amount: amount of blocks to print
        """

        address_len = len(str(self.memory_size - 1))
        start = start - (start % self.block_size)
        amount *= self.block_size

        if start < 0 or (start + amount) > self.memory_size:
            raise IndexError

        for address in range(start, start + amount, self.block_size):
            print(util.dec_str(address, address_len) + ": ", end = "")
            print(" ".join([util.dec_str(i, 2) for i in self.read_from_memory(address)]))


    def read_from_memory(self, address: int) -> List[int]:
        '''
        Get data inside a block containing this address
        :param address:
        :return: list of data , whose length is block_size
        '''
        # Need to subtract (address % block_size) to find the start address of the block
        start = address - (address % self.block_size)  # Start address
        end = start + self.block_size  # End address

        if start < 0 or end > self.memory_size:
            raise IndexError

        return self.memory_data[start:end]

    def write_to_memory(self, address: int, data: List[int]):
        """Set the block of main memory (of size self._block_size) that contains
        the data (4 bytes) at address.

        :param int address: address of byte within block of memory
        :param list data: bytes to set as block of memory
        """
        start = address - (address % self.block_size)  # Start address
        end = start + self.block_size  # End address

        if start < 0 or end > self.memory_size:
            raise IndexError

        if len(data) > self.block_size:
            raise IOError("Size of data per block is bigger than block_size")

        if len(data) < self.block_size:
            raise IOError("Size of data per block is smaller than block_size")

        self.memory_data[start:end] = data



