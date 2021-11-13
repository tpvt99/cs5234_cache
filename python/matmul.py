from typing import List, Union
import numpy as np
import time
import argparse

from simple_cache_sim.Simulator import Simulator


def is_power_of_two(n):
    return (n & (n-1) == 0) and n != 0


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


def matmul_cache_aware(cs, A, B, C, cache_sz=1):
    A_r, A_c = cs.get_dimension(A)
    B_r, B_c = cs.get_dimension(B)
    assert A_c == B_r

    size_each_block = int(np.sqrt(cache_sz / 2))
    
    C_r_blocks = ((A_r - 1) // size_each_block) + 1
    C_c_blocks = ((B_c - 1) // size_each_block) + 1
    k_blocks = ((A_c - 1) // size_each_block) + 1
    for blk_i in range(C_r_blocks):
        for blk_j in range(C_c_blocks):
            for blk_k in range(k_blocks):
                for i in range(blk_i * size_each_block, min(A_r, (blk_i + 1) * size_each_block)):
                    for j in range(blk_j * size_each_block, min(B_c, (blk_j + 1) * size_each_block)):
                        c = 0
                        for k in range(blk_k * size_each_block, min(A_c, (blk_k + 1) * size_each_block)):
                            c += cs.read(A, i, k) * cs.read(B, k, j)
                        cs.increment(C, i, j, value=c)

def matmul_cache_oblivious(cs, A, B, C):
    
    def matmul_recursive_helper(cs, n, a_r, a_c, b_r, b_c, base_arr=None):
    
        if base_arr is None:
            C_arr = cs.allocate(n, n, default_val=0)
        else:
            C_arr = base_arr

        if n <= 2:
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


def matmul_cache_adaptive(cs, A, B, C):
    
    def matmul_recursive_helper_cache_adaptive(cs, n, a_r, a_c, b_r, b_c, c_r, c_c):
    
        if n <= 2:
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


def load_matrix_to_cs(cs, matrix):
    row_num = len(matrix)
    col_num = len(matrix[0])
    addr = cs.allocate(row_num, col_num)
    for i in range(row_num):
        for j in range(col_num):
            cs.write(addr, i, j, value=matrix[i][j])
    return addr


def test(option, args):

    # change option here
    n = args.n  # should be power of 2 if use block method
    block_sz = args.block_sz
    cache_sz = args.cache_sz

    A = np.random.randint(-20, 20, size=(n, n))
    B = np.random.randint(-20, 20, size=(n, n))

    #A = np.array([[-15, -11], [-1, -8]])
    #B = np.array([[3,0],[11,-17]])

    begin = time.time()

    cs = Simulator(
        memory_size=2**24, 
        cache_size=cache_sz, 
        block_size=block_sz, 
        mapping_pol=None,
        write_pol="WT",
        replace_pol="LRU"
    )

    A_addr = load_matrix_to_cs(cs, A)
    B_addr = load_matrix_to_cs(cs, B)
    C_addr = cs.allocate(n, n, default_val=0)

    end = time.time()
    print(f"Initialization time (sec): {end-begin:.6f}")

    begin = time.time()
    if option == 'naive':
        matmul_naive(cs, A_addr, B_addr, C_addr)
    elif option == 'transpose':
        matmul_transposed(cs, A_addr, B_addr, C_addr)
    elif option == 'cache_eff':
        matmul_cache_eff(cs, A_addr, B_addr, C_addr, block_sz=block_sz)
    elif option == 'recursive':
        matmul_recursive(cs, A_addr, B_addr, C_addr)
    elif option == 'cache_adapt':
        matmul_recursive_cache_adaptive(cs, A_addr, B_addr, C_addr)
    else:
        raise ValueError('Invalid option')
    end = time.time()

    C = np.array([[cs.read(C_addr, i, j) for j in range(n)] for i in range(n)])

    stats = cs.get_access_summary()
    print(f'Option: {option}\n'
          f'N: {n}\n'
          f'Block size: {block_sz}\n'
          f'Cache size: {cache_sz}\n'
          f'Is multiplication correct: {(np.matmul(A, B) == C).all()}\n'
          f'Runtime (sec): {end - begin:.6f}\n'
          f'Cache hits: {stats["cache_hits"]}\n'
          f'Cache misses: {stats["cache_misses"]}\n'
          f'Total access: {stats["total_access"]}\n'
          f'Hit rate: {stats["hit_rate"]:.8f}\n'
          f'--------------------------')


def main():

    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-N', dest='n', type=int, default=32,
                        help='Matrix size')
    parser.add_argument('-B', dest='block_sz', type=int, default=8,
                        help='Block size')
    parser.add_argument('-M', dest='cache_sz', type=int, default=64,
                        help='Cache size size')

    args = parser.parse_args()

    test('naive', args)
    test('transpose', args)
    test('cache_eff', args)
    test('recursive', args)
    test('cache_adapt', args)

if __name__ == '__main__':
    main()
