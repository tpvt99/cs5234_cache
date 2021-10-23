from typing import List, Union
import numpy as np

#from src.simple_cache_sim.cache_simulator import CacheSimulator
from src.simple_cache_sim.Simulator import Simulator

def is_power_of_two(n):
    return (n & (n-1) == 0) and n != 0


def load_matrix_to_cs(cs, name, matrix):
    row_num = len(matrix)
    col_num = len(matrix[0])
    cs.allocate(name, row_num, col_num)
    for i in range(row_num):
        for j in range(col_num):
            cs.write(name, i, j, value=matrix[i][j])


def matmul_naive(cs, A, B, C):
    A_r, A_c = cs.get_dimension(A)
    B_r, B_c = cs.get_dimension(B)
    assert A_c == B_r
    
    for i in range(A_r):
        for j in range(B_c):
            c = 0
            for k in range(A_c):
                c += cs.read(A, i, k) * cs.read(B, k, j)
            cs.write(C, i, j, value=c)


def matmul_transposed(cs, A, B_T, C):
    A_r, A_c = cs.get_dimension(A)
    B_c, B_r = cs.get_dimension(B_T)
    assert A_c == B_r
    
    for i in range(A_r):
        for j in range(B_c):
            c = 0
            for k in range(A_c):
                c += cs.read(A, i, k) * cs.read(B_T, j, k)
            cs.write(C, i, j, value=c)


def matmul_cache_eff(cs, A, B, C, block_sz=1):
    A_r, A_c = cs.get_dimension(A)
    B_r, B_c = cs.get_dimension(B)
    assert A_c == B_r
    
    C_r_blocks = ((A_r - 1) // block_sz) + 1
    C_c_blocks = ((B_c - 1) // block_sz) + 1
    k_blocks = ((A_c - 1) // block_sz) + 1
    for blk_i in range(C_r_blocks):
        for blk_j in range(C_c_blocks):
            for blk_k in range(k_blocks):
                for i in range(blk_i * block_sz, min(A_r, (blk_i + 1) * block_sz)):
                    for j in range(blk_j * block_sz, min(B_c, (blk_j + 1) * block_sz)):
                        c = 0
                        for k in range(blk_k * block_sz, min(A_c, (blk_k + 1) * block_sz)):
                            c += cs.read(A, i, k) * cs.read(B, k, j)
                        cs.increment(C, i, j, value=c)


def matmul_recursive(cs, A, B, C, block_sz=1):
    
    def matmul_recursive_helper(cs, n, a_r, a_c, b_r, b_c, base_arr=None):
    
        C_arr = base_arr if base_arr else f'C_{a_r}_{a_c}_{b_r}_{b_c}_{n}'
        if base_arr is None:
            cs.allocate(C_arr, n, n, default_val=0)

        if n <= block_sz:
            for i in range(n):
                for j in range(n):
                    c = 0
                    for k in range(n):
                        c += cs.read(A, a_r + i, a_c + k) * cs.read(B, b_r + k, b_c + j)
                    cs.write(C_arr, i, j, value=c)

        else:
            sub_n = n // 2
            for c_quad_r, c_quad_c in [(0, 0), (0, sub_n), (sub_n, 0), (sub_n, sub_n)]:
                a_quad_r = a_r + c_quad_r
                b_quad_c = b_c + c_quad_c
                for blk in [0, sub_n]:
                    a_quad_c = a_c + blk
                    b_quad_r = b_r + blk
                    C_quad = matmul_recursive_helper(cs, sub_n, a_quad_r, a_quad_c, b_quad_r, b_quad_c)
                    for i in range(sub_n):
                        for j in range(sub_n):
                            cs.increment(C_arr, i + c_quad_r, j + c_quad_c, value=cs.read(C_quad, i, j))

        return C_arr
    
    A_r, A_c = cs.get_dimension(A)
    B_c, B_r = cs.get_dimension(B)
    assert A_r == A_c == B_c == B_r
    assert is_power_of_two(A_r)
    n = A_c
    matmul_recursive_helper(cs, n, 0, 0, 0, 0, base_arr=C)


def matmul_recursive_cache_adaptive(cs, A, B, C, block_sz=1):
    
    def matmul_recursive_helper_cache_adaptive(cs, n, a_r, a_c, b_r, b_c, c_r, c_c):
    
        if n <= block_sz:
            for i in range(n):
                for j in range(n):
                    c = 0
                    for k in range(n):
                        c += cs.read(A, a_r + i, a_c + k) * cs.read(B, b_r + k, b_c + j)
                    cs.increment(C, i + c_r, j + c_c, value=c)

        else:
            sub_n = n // 2
            for blk_r in [0, sub_n]:
                for blk_c in [0, sub_n]:

                    c_quad_r = c_r + blk_r
                    c_quad_c = c_c + blk_c
                    a_quad_r = a_r + blk_r
                    b_quad_c = b_c + blk_c

                    for blk in [0, sub_n]:
                        a_quad_c = a_c + blk
                        b_quad_r = b_r + blk
                        C_quad = matmul_recursive_helper_cache_adaptive(
                            cs, sub_n, a_quad_r, a_quad_c, b_quad_r, b_quad_c, c_quad_r, c_quad_c)
    
    A_r, A_c = cs.get_dimension(A)
    B_c, B_r = cs.get_dimension(B)
    assert A_r == A_c == B_c == B_r
    assert is_power_of_two(A_r)
    n = A_c
    matmul_recursive_helper_cache_adaptive(cs, n, 0, 0, 0, 0, 0, 0)


def main(option):

    # change option here
    n = 8  # should be power of 2 if use block method
    block_sz = 2
    #option = 'recursive'  # see methods below

    A = np.random.randint(-20, 20, size=(n, n))
    B = np.random.randint(-20, 20, size=(n, n))


    cs = Simulator(memory_size=2**(n+2), cache_size=2**4, block_size=block_sz, writing_policy="WT",
                   replacement_policy="LRU")
    load_matrix_to_cs(cs, "A", A)
    load_matrix_to_cs(cs, "B", B)
    cs.allocate("C", n, n, default_val=0)

    if option == 'transpose':
        load_matrix_to_cs(cs, "B", B.T)
    else:
        load_matrix_to_cs(cs, "B", B)

    if option == 'naive':
        matmul_naive(cs, "A", "B", "C")
    elif option == 'transpose':
        matmul_transposed(cs, "A", "B", "C")
    elif option == 'cache_eff':
        matmul_cache_eff(cs, "A", "B", "C", block_sz=block_sz)
    elif option == 'recursive':
        matmul_recursive(cs, "A", "B", "C", block_sz=block_sz)
    elif option == 'cache_adapt':
        matmul_recursive_cache_adaptive(cs, "A", "B", "C", block_sz=block_sz)
    else:
        raise ValueError('Invalid option')

    C = np.array([[cs.read("C", i, j) for j in range(n)] for i in range(n)])
    print(f'Is multiplication correct? {(np.matmul(A, B) == C).all()}')
    print(f'{option} Cache hits: {cs.cpu.hits}, cache miss: {cs.cpu.miss}, total access: {cs.cpu.total_access}')


if __name__ == '__main__':
    main('naive')
    main('transpose')
    main('cache_eff')
    main('recursive')
    main('cache_adapt')
