from typing import List

from simple_cache_sim.Block import Block
from simple_cache_sim import util


class Memory():
    def __init__(self, memory_size, block_size):
        """
        Size of each value (per address) is 4 bytes to store enough an integer
        If memory_size and block_size is bytes, please divide by 4 before fetching into this Memory
        because each address is 4 bytes

        :param memory_size: memory size (in 4*Bytes)
        :param block_size: block size (in 4*Bytes)
        """
        self.memory_size = memory_size
        self.block_size = block_size
        self.blocks_count = self.memory_size // self.block_size
        self.memory_data = []

    # def print_section(self, start, amount):
    #     """Print a section of main memory by decimal forms.

    #     :param int start: start address to print from
    #     :param int amount: amount of blocks to print
    #     """

    #     address_len = len(str(self.memory_size - 1))
    #     start = start - (start % self.block_size)
    #     amount *= self.block_size

    #     if start < 0 or (start + amount) > self.memory_size:
    #         raise IndexError

    #     for address in range(start, start + amount, self.block_size):
    #         print(util.dec_str(address, address_len) + ": ", end = "")
    #         print(" ".join([util.dec_str(i, 2) for i in self.read_block_from_memory(address)]))


    def read_block_from_memory(self, address: int) -> Block:
        """
        Get data inside a block containing this address
        :param address:
        :return: list of data , whose length is block_size
        """
        # # Need to subtract (address % block_size) to find the start address of the block
        # start = address - (address % self.block_size)  # Start address
        # end = start + self.block_size  # End address

        # if start < 0 or end > self.memory_size:
        #     raise IndexError

        return self.memory_data[address//self.block_size]

    def allocate(self, num_blocks: int):
        num_blocks = min(num_blocks, self.blocks_count - len(self.memory_data))
        self.memory_data.extend(Block(self.block_size) for _ in range(num_blocks))

    # def write_block_to_memory(self, address: int, data: List[int]):
    #     """Set the block of main memory (of size self._block_size) that contains
    #     the data at address.

    #     :param int address: address of byte within block of memory
    #     :param list data: bytes to set as block of memory
    #     """
    #     start = address - (address % self.block_size)  # Start address
    #     end = start + self.block_size  # End address

    #     if start < 0 or end > self.memory_size:
    #         raise IndexError

    #     assert len(data) == self.block_size, "Data Length must be equal to self.block_size"

    #     self.memory_data[start:end] = data

    # def allocate_memory(self, address: int, data: List[int]):
    #     """
    #     Allocate any arbitrary data length to memory without blocks (Using this only for initialization of mem)

    #     :param address:
    #     :param data:
    #     :return:
    #     """
    #     data_len = len(data)
    #     start_address = address
    #     end_address = start_address + data_len

    #     assert start_address >= 0
    #     assert end_address < self.memory_size

    #     self.memory_data[start_address:start_address+data_len] = data


