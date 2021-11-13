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
        #num_blocks = min(num_blocks, self.blocks_count - len(self.memory_data))
        self.memory_data.extend(Block(self.block_size) for _ in range(num_blocks))
