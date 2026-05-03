"""
Best / Average / Worst case timing for all 6 knapsack algorithms.

Best-case inputs:
  BruteForce / Memo : all weights > capacity  (single-branch linear recursion, O(n))
  Tabulation        : capacity = 1, all weights = 2  (inner body always takes 'else' path)
  SpaceOpt          : same as tabulation
  Greedy            : n=1 (trivial sort + single pass)
  FPTAS             : epsilon = 0.9  (aggressively coarse scaling -> tiny DP table)

Average-case inputs:
  All algorithms    : random values + random weights in [1, W//2], W = capacity

Worst-case inputs:
  BruteForce / Memo : all weights <= capacity  (both branches always taken, full 2^n tree)
  Tabulation        : large n x W, all weights = 1  (every cell a max() comparison)
  SpaceOpt          : same
  Greedy            : input reverse-sorted by ratio  (Python's Timsort worst-case path)
  FPTAS             : epsilon = 0.01  (fine-grained scaling -> huge DP table)

Timing: median of 5 runs, reported in milliseconds.
"""

import sys, os, time, random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas


def ms(func, runs=5):
    """Median wall-clock time in ms."""
    t = sorted((time.perf_counter(), func(), time.perf_counter())[2] -
               (time.perf_counter(), func(), time.perf_counter())[0]
               for _ in range(runs))
    # cleaner version:
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        func()
        times.append((time.perf_counter() - t0) * 1000)
    return sorted(times)[runs // 2]


def rng_items(n, W, seed=42):
    r = random.Random(seed)
    v = [r.randint(1, 100)   for _ in range(n)]
    w = [r.randint(1, W // 2 or 1) for _ in range(n)]
    return v, w


def header(title):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")


# ─────────────────────────────────────────────────────────────────────────────
# 1. BRUTE FORCE  (n capped at 20 — anything larger is impractical)
# ─────────────────────────────────────────────────────────────────────────────
header("BRUTE FORCE  — n=20")
print(f"  Case         Input description                        Time (ms)")
print(f"  ------------ ---------------------------------------- ----------")

N_BF, W_BF = 20, 200
v_avg, w_avg = rng_items(N_BF, W_BF)

# Best: all weights > capacity -> single-branch, O(n) recursion
v_best = [1] * N_BF
w_best = [W_BF + 1] * N_BF          # every weight exceeds capacity
t_best = ms(lambda: knapsack_brute_force(W_BF, N_BF, v_best, w_best))
print(f"  Best         all weights > capacity (O(n) recursion)  {t_best:>10.4f}")

# Average: random
t_avg = ms(lambda: knapsack_brute_force(W_BF, N_BF, v_avg, w_avg))
print(f"  Average      random weights in [1,{W_BF//2}]              {t_avg:>10.4f}")

# Worst: all weights <= capacity -> both branches always taken, O(2^n)
v_worst = [1] * N_BF
w_worst = [1] * N_BF                # all fit, maximum branching
t_worst = ms(lambda: knapsack_brute_force(W_BF, N_BF, v_worst, w_worst))
print(f"  Worst        all weights <= capacity (O(2^n) tree)    {t_worst:>10.4f}")
print(f"\n  Ratio worst/best: {t_worst/t_best:.0f}x  (confirms exponential gap)")


# ─────────────────────────────────────────────────────────────────────────────
# 2. MEMOIZATION  (n=20 to compare with BF; then n=100 to show DP benefit)
# ─────────────────────────────────────────────────────────────────────────────
header("MEMOIZATION  — n=20 then n=100")

def memo_call(cap, n, v, w):
    m = [[None]*(cap+1) for _ in range(n+1)]
    return knapsack_memoization(cap, n, v, w, m)

# n=20
print(f"  n=20 --")
t_best20  = ms(lambda: memo_call(W_BF, N_BF, v_best, w_best))
t_avg20   = ms(lambda: memo_call(W_BF, N_BF, v_avg,  w_avg))
t_worst20 = ms(lambda: memo_call(W_BF, N_BF, v_worst, w_worst))
print(f"  Best (all wt>cap, O(n) subproblems):   {t_best20:>8.4f} ms")
print(f"  Average (random, O(n*W) subproblems):  {t_avg20:>8.4f} ms")
print(f"  Worst (all wt<=cap, O(n*W) subprob):   {t_worst20:>8.4f} ms")

# n=100, W=500
N2, W2 = 100, 500
v2, w2 = rng_items(N2, W2)
v2_best  = [1]*N2;  w2_best  = [W2+1]*N2
v2_worst = [1]*N2;  w2_worst = [1]*N2

sys.setrecursionlimit(2000)   # raise for n=100
print(f"\n  n=100, W=500 --")
t_b2 = ms(lambda: memo_call(W2, N2, v2_best,  w2_best))
t_a2 = ms(lambda: memo_call(W2, N2, v2,       w2))
t_w2 = ms(lambda: memo_call(W2, N2, v2_worst, w2_worst))
sys.setrecursionlimit(1000)
print(f"  Best (all wt>cap, O(n) subproblems):   {t_b2:>8.4f} ms")
print(f"  Average (random):                      {t_a2:>8.4f} ms")
print(f"  Worst (all wt<=cap, all cells filled):  {t_w2:>8.4f} ms")


# ─────────────────────────────────────────────────────────────────────────────
# 3. TABULATION  — n=100, W=500
# ─────────────────────────────────────────────────────────────────────────────
header("TABULATION  — n=100, W=500")
print("  (All cells always computed — best ~= worst ~= avg)")
print(f"  Case         Description                              Time (ms)")
print(f"  ------------ ---------------------------------------- ----------")

# Best: all weights > W -> inner loop always takes 'else' branch (simpler op)
v_tb = [1]*N2;  w_tb = [W2+1]*N2
t_tb_best = ms(lambda: knapsack_tabulation(W2, v_tb, w_tb))
print(f"  Best         all weights > capacity (else-branch)    {t_tb_best:>10.4f}")

t_tb_avg  = ms(lambda: knapsack_tabulation(W2, v2, w2))
print(f"  Average      random weights                          {t_tb_avg:>10.4f}")

# Worst: all weights = 1 (every cell triggers max() comparison)
v_tw = [1]*N2;  w_tw = [1]*N2
t_tb_worst = ms(lambda: knapsack_tabulation(W2, v_tw, w_tw))
print(f"  Worst        all weights = 1 (every cell max())      {t_tb_worst:>10.4f}")
print(f"\n  Ratio worst/best: {t_tb_worst/t_tb_best:.2f}x  (nearly constant — DP is O(n*W) regardless)")


# ─────────────────────────────────────────────────────────────────────────────
# 4. SPACE-OPTIMISED  — n=100, W=500
# ─────────────────────────────────────────────────────────────────────────────
header("SPACE-OPTIMISED  — n=100, W=500")
print(f"  Case         Description                              Time (ms)")
print(f"  ------------ ---------------------------------------- ----------")

v_sb = [1]*N2;  w_sb = [W2+1]*N2
t_sb_best  = ms(lambda: knapsack_space_optimised(v_sb, w_sb, N2, W2))
t_sb_avg   = ms(lambda: knapsack_space_optimised(v2,   w2,   N2, W2))
v_sw = [1]*N2;  w_sw = [1]*N2
t_sb_worst = ms(lambda: knapsack_space_optimised(v_sw, w_sw, N2, W2))
print(f"  Best         all weights > capacity                  {t_sb_best:>10.4f}")
print(f"  Average      random weights                          {t_sb_avg:>10.4f}")
print(f"  Worst        all weights = 1                         {t_sb_worst:>10.4f}")
print(f"\n  Ratio worst/best: {t_sb_worst/t_sb_best:.2f}x")


# ─────────────────────────────────────────────────────────────────────────────
# 5. GREEDY  — n=100
# ─────────────────────────────────────────────────────────────────────────────
header("GREEDY  — n=100, W=500")
print(f"  Case         Description                              Time (ms)")
print(f"  ------------ ---------------------------------------- ----------")

# Best: already sorted by v/w ratio (Timsort O(n) on sorted data)
v_gb = list(range(100, 0, -1))        # descending values
w_gb = list(range(1, 101))            # ascending weights -> ratios already decreasing
t_gb_best = ms(lambda: knapsack_greedy(W2, v_gb, w_gb))
print(f"  Best         pre-sorted by ratio (Timsort O(n))     {t_gb_best:>10.4f}")

t_gb_avg  = ms(lambda: knapsack_greedy(W2, v2, w2))
print(f"  Average      random input                            {t_gb_avg:>10.4f}")

# Worst: reverse-sorted by ratio (maximum reordering for Timsort)
v_gw = list(range(1, 101))            # ascending values
w_gw = list(range(100, 0, -1))        # descending weights -> ratios ascending -> sort reverses
t_gb_worst = ms(lambda: knapsack_greedy(W2, v_gw, w_gw))
print(f"  Worst        reverse-sorted by ratio (max reorder)  {t_gb_worst:>10.4f}")
print(f"\n  All cases O(n log n) — ratio: {t_gb_worst/t_gb_best:.2f}x  (sort dominates)")


# ─────────────────────────────────────────────────────────────────────────────
# 6. FPTAS  — n=20, W=500, varying epsilon
# ─────────────────────────────────────────────────────────────────────────────
header("FPTAS  — n=20, W=200, varying epsilon")
print(f"  Case         epsilon    Description                   Time (ms)")
print(f"  ------------ ---------- ----------------------------- ----------")

v_fp, w_fp = rng_items(20, 200)

for label, eps, desc in [
    ("Best",    0.9,  "coarse scaling -> tiny profit table"),
    ("Average", 0.25, "default epsilon"),
    ("Worst",   0.05, "fine scaling  -> large profit table"),
]:
    t_fp = ms(lambda e=eps: knapsack_fptas(200, v_fp, w_fp, epsilon=e))
    print(f"  {label:<12} {eps:<10.2f} {desc:<29} {t_fp:>10.4f}")


# ─────────────────────────────────────────────────────────────────────────────
# CONSOLIDATED SUMMARY TABLE
# ─────────────────────────────────────────────────────────────────────────────
header("CONSOLIDATED SUMMARY (ms)")
print(f"  {'Algorithm':<18} {'n':>5} {'W':>5} {'Best (ms)':>12} {'Avg (ms)':>12} {'Worst (ms)':>12} {'Worst/Best':>12}")
print(f"  {'-'*18} {'-'*5} {'-'*5} {'-'*12} {'-'*12} {'-'*12} {'-'*12}")

rows = [
    ("BruteForce",     N_BF, W_BF,  t_best,    t_avg,    t_worst),
    ("Memoization",    N_BF, W_BF,  t_best20,  t_avg20,  t_worst20),
    ("Tabulation",     N2,   W2,    t_tb_best, t_tb_avg, t_tb_worst),
    ("SpaceOpt",       N2,   W2,    t_sb_best, t_sb_avg, t_sb_worst),
    ("Greedy",         N2,   W2,    t_gb_best, t_gb_avg, t_gb_worst),
    ("FPTAS eps=0.25", 20,   200,   ms(lambda: knapsack_fptas(200, v_fp, w_fp, 0.9)),
                                    ms(lambda: knapsack_fptas(200, v_fp, w_fp, 0.25)),
                                    ms(lambda: knapsack_fptas(200, v_fp, w_fp, 0.05))),
]
for name, n, w, tb, ta, tw in rows:
    ratio = tw / tb if tb > 0 else float('inf')
    print(f"  {name:<18} {n:>5} {w:>5} {tb:>12.4f} {ta:>12.4f} {tw:>12.4f} {ratio:>11.1f}x")
