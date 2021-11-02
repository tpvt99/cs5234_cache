
# Naive first with multiple configurations
from matmul import matmul_naive, load_matrix_to_cs, matmul_cache_eff
import numpy as np
import time
import argparse
import matplotlib.pyplot as plt

from src.simple_cache_sim.Simulator import Simulator

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
    elif option == 'cache_eff':
        matmul_cache_eff(cs, A_addr, B_addr, C_addr, block_sz=cache_sz)
    else:
        raise ValueError('Invalid option')
    end = time.time()

    C = np.array([[cs.read(C_addr, i, j) for j in range(n)] for i in range(n)])

    stats = cs.get_access_summary()
    print(f'N: {n} Block size: {block_sz} Cache size: {cache_sz}\n'
          f'Is multiplication correct: {(np.matmul(A, B) == C).all()}\n'
          f'Runtime (sec): {end - begin:.6f}\n'
          f'Cache hits: {stats["cache_hits"]} Total access: {stats["total_access"]} '
          f'Hit rate: {stats["hit_rate"]:.8f}\n'
          f'--------------------------')

    return stats["cache_hits"], stats["total_access"], end-begin

def draw_superimposed_bar_graph(hits, access, title, x_ticks_labels):
    ind = np.arange(len(hits))

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.bar(x=ind, height=hits, width=0.35, align='center', label="Hit")
    ax.bar(x=ind, height=access, width=0.35/3, align='center', label="Access")
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
n = 128
block_size = [2, 8, 16, 32, 64]
mapping_policy = 2
cache_size = 1024
replace_policy = "lru"

cache_hits = []
cache_access = []
total_time = []
for i in range(len(block_size)):
    hit, access, run_time = test("cache_eff", n = n, block_sz=block_size[i], cache_sz=cache_size,
         mapping_pol = mapping_policy, replace_pol = replace_policy)
    cache_hits.append(hit)
    cache_access.append(access)
    total_time.append(run_time)


draw_superimposed_bar_graph(cache_hits, cache_access,
                            f"Naive Matmul n={n}, bs={block_size}, "
                            f"cs = {cache_size}, \n with varying block_size",
                            ["bs:2", "bs:8", "bs:16", "bs:32", "bs:64"])

# Stress-test with
