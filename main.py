

from src.simple_cache_sim.Memory import Memory
from src.simple_cache_sim.CPU import CPU
from src.simple_cache_sim.Cache import Cache

# Initialize Array A
A = [[1, 2, 3],[0,1,2],[2,5,6]]
B = [[7,1,2],[2,1,1],[5,0,0]]
C = [[0,0,0],[0,0,0],[0,0,0]]

matrix_size = 3

memory_size = 2**8 # ensure to store enough A
cache_size = 2**4
block_size = 2**2

cache = Cache(cache_size=cache_size, block_size=block_size,
              memory_size=memory_size, mapping_pol=1,
              replace_pol="LRU", write_pol="WT")
memory = Memory(memory_size=memory_size, block_size=block_size)
cpu = CPU(cache=cache,memory=memory, write_pol="WT")

def initialize_memory(A, B):
    '''
    Row-ordering memory
    :param A: matrix A
    :param B: matrix B
    :return:
    '''
    #Step 1. Flat matrix A and B
    a = [item for sublist in A for item in sublist]
    b = [item for sublist in B for item in sublist]
    # Step 2. Store continuously in memory
    c = a + b
    memory.allocate_memory(0, c)

def getElementA(i: int, j: int):
    a = cpu.read(matrix_size * i + j)
    return a

def getElementB(i: int, j : int):
    b = cpu.read(matrix_size**2 + matrix_size*i + j)
    return b

initialize_memory(A, B)

for i in range(0,3):
    for j in range(0,3):
        for k in range(0,3):
            C[i][j] += getElementA(i,k) * getElementB(k,j)

print(C)
print(f'Cache hits: {cpu.hits}')
print(f'Cache miss: {cpu.miss}')
print(f'Cache total: {cpu.total_access}')