 
from typing import Optional, Tuple, Any
from simple_cache_sim.Simulator import Simulator
from simple_cache_sim.CPUAdaptive import CPUAdaptive


class SimulatorAdaptive(Simulator):
    def __init__(self, memory_size: int, cache_size: int, block_size: int,
                 mapping_pol: int = None, replace_pol: str = "LRU", write_pol: str = "WT", c1: int = 4):

        super().__init__( memory_size, cache_size, block_size,
                 mapping_pol, replace_pol, write_pol)

        self.cpu = CPUAdaptive(cache=self.cache, memory=self.memory, write_pol=write_pol, c1=c1)
