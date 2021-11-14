
# Naive first with multiple configurations
from matmul import matmul_naive, load_matrix_to_cs, matmul_cache_aware, matmul_cache_oblivious, matmul_cache_adaptive
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

from simple_cache_sim.Simulator import Simulator

def test(option, n, block_sz, cache_sz, mapping_pol, replace_pol):

    A = np.random.randint(-20, 20, size=(n, n))
    B = np.random.randint(-20, 20, size=(n, n))

    begin = time.time()

    cs = Simulator(
        memory_size=2**24,
        cache_size=cache_sz,
        block_size=block_sz,
        mapping_pol=mapping_pol,
        write_pol="WT",
        replace_pol=replace_pol
    )

    A_addr = load_matrix_to_cs(cs, A)
    B_addr = load_matrix_to_cs(cs, B)
    C_addr = cs.allocate(n, n, default_val=0)

    end = time.time()
    print(f"Initialization time (sec): {end-begin:.6f}")

    begin = time.time()
    if option == "naive":
        matmul_naive(cs, A_addr, B_addr, C_addr)
    elif option == 'aware':
        matmul_cache_aware(cs, A_addr, B_addr, C_addr, cache_sz=cache_sz)
    elif option == "oblivious":
        matmul_cache_oblivious(cs, A_addr, B_addr, C_addr)
    elif option == "adaptive":
        matmul_cache_adaptive(cs, A_addr, B_addr, C_addr)
    else:
        raise ValueError('Invalid option')
    end = time.time()

    C = np.array([[cs.read(C_addr, i, j) for j in range(n)] for i in range(n)])

    stats = cs.get_access_summary()
    print(f'N: {n} Block size: {block_sz} Cache size: {cache_sz}\n'
          f'Is multiplication correct: {(np.matmul(A, B) == C).all()}\n'
          f'Runtime (sec): {end - begin:.6f}\n'
          f'Cache hits: {stats["cache_misses"]} Total access: {stats["total_access"]} '
          f'Hit rate: {stats["hit_rate"]:.8f}\n'
          f'--------------------------')

    return stats["cache_misses"], stats["total_access"], end-begin

def draw_superimposed_bar_graph(hits, access, title, x_ticks_labels):
    ind = np.arange(len(hits))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x=ind, height=hits, width=0.3, align='center', label="Miss")
    ax.bar(x=ind, height=access, width=0.3/3, align='center', label="Access")
    ax.legend()

    plt.xticks(ind, x_ticks_labels)

    rects = ax.patches
    rects = rects[len(rects)//2:]
    # Make some labels.
    #Divide by 2 because we have 2 bars per each change
    labels = [f"{hits[i]/access[i]:.2f}" for i in range(len(rects))]

    for rect, label in zip(rects, labels):
        height = rect.get_height()
        ax.text(
                rect.get_x() + rect.get_width() / 2, height + 5, label, ha="center", va="bottom"
        )

    plt.title(title)
    plt.show()

def draw_bar_together(miss, access, title, x_ticks_labels, legends):
    ind = np.arange(miss.shape[1])
    ratio = miss / access

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for size_index in range(miss.shape[1]):
        ax.bar(x=ind+0.2*size_index, height=ratio[:, size_index], width=0.2, align='center', label=legends[size_index])
    ax.legend()

    plt.xticks(ind, x_ticks_labels)

    rects = ax.patches
    # Make some labels.
    #Divide by 2 because we have 2 bars per each change
    # labels = [f"{hits[i]/access[i]:.2f}" for i in range(len(rects))]

    for rect in rects:
        height = rect.get_height()
        ax.text(
                 rect.get_x() + rect.get_width() / 2, height + 0.002, round(height,2), ha="center", va="bottom",
        fontsize='small')

    plt.title(title)
    plt.show()

# Set 1. Testing mapping policy

def set_1_testing_separately_naive():
    n = 16
    block_size = [2, 4, 8, 16, 32]#[8, 32, 64, 128, 256]
    mapping_policy = None # Ideal cache should be None
    cache_size = [4, 16, 64, 256, 1024]#[64, 1024, 4096, 16384, 65536] # Tall-cache size
    replace_policy = "lru"

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "naive"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_aware():
    n = 256
    block_size = [2, 4, 8, 16, 32]#[8, 32, 64, 128, 256]
    mapping_policy = None # Ideal cache should be None
    cache_size = [4, 16, 64, 256, 1024]#[64, 1024, 4096, 16384, 65536] # Tall-cache size
    replace_policy = "lru"

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "aware"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_oblivious():
    n = 64
    block_size = [2, 4, 8, 16, 32]#[8, 32, 64, 128, 256]
    mapping_policy = None # Ideal cache should be None
    cache_size = [4, 16, 64, 256, 1024]#[64, 1024, 4096, 16384, 65536] # Tall-cache size
    replace_policy = "lru"

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "oblivious"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_adaptive():
    n = 256
    block_size = [2, 4, 8, 16, 32]#[8, 32, 64, 128, 256]
    mapping_policy = None # Ideal cache should be None
    cache_size = [4, 16, 64, 256, 1024]#[64, 1024, 4096, 16384, 65536] # Tall-cache size
    replace_policy = "lru"

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "adaptive"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)


def set_2_testing_together():
    n = 256
    block_size = [4, 8, 16, 32]  # [8, 32, 64, 128, 256]
    mapping_policy = None  # Ideal cache should be None
    cache_size = [16, 64, 256, 1024]  # [64, 1024, 4096, 16384, 65536] # Tall-cache size
    replace_policy = "lru"
    option = ["naive", "aware", "oblivious", "adaptive"]

    cache_misses = np.zeros(shape=(len(cache_size), len(option)))
    cache_access = np.zeros(shape=(len(cache_size), len(option)))
    label = []

    for j in range(len(cache_size)):
        for i in range(len(option)):
            miss, access, run_time = test(option[i], n=n, block_sz=block_size[j], cache_sz=cache_size[j],
                                         mapping_pol=mapping_policy, replace_pol=replace_policy)
            cache_misses[j][i] = miss
            cache_access[j][i] = access
        label.append(f"bs:{block_size[j]}, cs:{cache_size[j]}")

    draw_bar_together(cache_misses, cache_access,
                                f"Cache miss ratio of 4 different algorithms when n={n}",
                                label, option)

# Stress-test with
#set_1_testing_separately_aware()
#set_1_testing_separately_naive()
#set_1_testing_separately_oblivious()
#set_1_testing_separately_adaptive()
set_2_testing_together()