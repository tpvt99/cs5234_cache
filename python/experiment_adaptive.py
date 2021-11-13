
# Naive first with multiple configurations
from matmul import matmul_naive, load_matrix_to_cs, matmul_cache_aware, matmul_cache_oblivious, matmul_cache_adaptive
import numpy as np
import time

import matplotlib.pyplot as plt
from simple_cache_sim.SimulatorAdaptive import SimulatorAdaptive


def test(option, n, block_sz, cache_sz, mapping_pol, replace_pol, c1):

    A = np.random.randint(-20, 20, size=(n, n))
    B = np.random.randint(-20, 20, size=(n, n))

    begin = time.time()

    cs = SimulatorAdaptive(
        memory_size=2**24,
        cache_size=cache_sz,
        block_size=block_sz,
        mapping_pol=mapping_pol,
        write_pol="WT",
        replace_pol=replace_pol,
        c1=c1
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


# Set 1. Testing mapping policy

def set_1_testing_separately_naive(n, block_size, cache_size, mapping_policy, replace_policy, c1):

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "naive"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy, c1=c1)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_aware(n, block_size, cache_size, mapping_policy, replace_policy, c1):

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "aware"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy, c1=c1)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_oblivious(n, block_size, cache_size, mapping_policy, replace_policy, c1):

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "oblivious"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy, c1=c1)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)

def set_1_testing_separately_adaptive(n, block_size, cache_size, mapping_policy, replace_policy, c1):

    cache_misses = []
    cache_access = []
    total_time = []
    label = []
    option = "adaptive"
    for i in range(len(block_size)):
        miss, access, run_time = test(option, n = n, block_sz=block_size[i], cache_sz=cache_size[i],
                mapping_pol = mapping_policy, replace_pol = replace_policy, c1=c1)
        cache_misses.append(miss)
        cache_access.append(access)
        total_time.append(run_time)
        label.append(f"cs:{cache_size[i]}\nbs:{block_size[i]}")


    draw_superimposed_bar_graph(cache_misses, cache_access,
                                f"{option} n={n}, bs={block_size}, "
                                f"cs = {cache_size}, \n with varying block_size and cache_size",
                                label)


# Stress-test with
c1 = 1
n = 256
block_size = [2, 4, 8, 16, 32]#[8, 32, 64, 128, 256]
mapping_policy = 1 # Ideal cache should be None
cache_size = [c1*i**2 for i in block_size]#[64, 1024, 4096, 16384, 65536] # Tall-cache size
replace_policy = "lru"

set_1_testing_separately_naive(n, block_size, cache_size, mapping_policy, replace_policy, c1)
set_1_testing_separately_aware(n, block_size, cache_size, mapping_policy, replace_policy, c1)
set_1_testing_separately_oblivious(n, block_size, cache_size, mapping_policy, replace_policy, c1)
set_1_testing_separately_adaptive(n, block_size, cache_size, mapping_policy, replace_policy, c1)
