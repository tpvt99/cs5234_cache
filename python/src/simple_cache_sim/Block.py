import numpy as np


class Block():
    """
    Block in cache

    """
    def __init__(self, block_size: int):
        """

        :param block_size: number of values (integers) we want to store per block
        """
        # self.tag = 0 # Tag is changed according to the address of memory
        # self.valid = 0 # If this is valid address
        # self.use = 0 # Number of accessed. The less mean it is less accessed, hence would be discarded if cache is full
        # self.modified = 0

        self.block_size = block_size
        # self.data = [0] * block_size # A list of values (integers)
        self.data = np.full(shape=block_size, fill_value=np.nan, dtype=np.int64)
