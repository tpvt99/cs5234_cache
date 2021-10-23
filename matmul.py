from typing import List, Union
import numpy as np

from simple_cache_sim.cache_simulator import CacheSimulator


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
