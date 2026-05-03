"""
Comprehensive sanity check for all 0/1 Knapsack implementations.
Covers: edge cases, correctness, greedy failure proof, FPTAS guarantee,
        performance timing, memory usage, recursion risk, kplib validation,
        and tabulation item-recovery integrity.

Run: python testing/sanity_check.py
"""

import sys, os, time, tracemalloc, math, random, gc
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas

PASS = "PASS"
FAIL = "FAIL"
WARN = "WARN"

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1 – ALGORITHM SUMMARY
# ─────────────────────────────────────────────────────────────────────────────

def print_section(title):
    print(f"\n{'='*72}")
    print(f"  {title}")
    print(f"{'='*72}")

def print_subsection(title):
    print(f"\n  -- {title} --")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2 – CORRECTNESS HELPERS
# ─────────────────────────────────────────────────────────────────────────────

total_tests = 0
total_pass  = 0
failures    = []   # list of (test_name, algo, expected, got)


def run_exact(name, values, weights, capacity, expected):
    """Run all exact algorithms; record pass/fail."""
    global total_tests, total_pass
    n    = len(values)
    memo = [[None] * (capacity + 1) for _ in range(n + 1)]

    results = {
        "BruteForce": knapsack_brute_force(capacity, n, values, weights),
        "Memoization": knapsack_memoization(capacity, n, values, weights, memo),
        "Tabulation": knapsack_tabulation(capacity, values, weights)[0],
        "SpaceOpt":  knapsack_space_optimised(values, weights, n, capacity),
    }

    tab_val, tab_items = knapsack_tabulation(capacity, values, weights)
    item_weight = sum(weights[i] for i in tab_items)
    item_value  = sum(values[i]  for i in tab_items)
    item_weight_ok = item_weight <= capacity
    item_value_ok  = item_value  == tab_val

    row = f"    {name:<40} exp={expected}  "
    for algo, val in results.items():
        total_tests += 1
        ok = (val == expected)
        if ok:
            total_pass += 1
        else:
            failures.append((name, algo, expected, val))
        row += f"{algo[:4]}={val}({'OK' if ok else 'XX'})  "

    tab_ok = item_weight_ok and item_value_ok
    total_tests += 2
    if tab_ok:
        total_pass += 2
    else:
        if not item_weight_ok:
            failures.append((name, "Tab-ItemWeight", f"<={capacity}", item_weight))
        if not item_value_ok:
            failures.append((name, "Tab-ItemValue",  tab_val, item_value))

    row += f"  Tab-items: wt={item_weight}({'OK' if item_weight_ok else 'XX'}) val={item_value}({'OK' if item_value_ok else 'XX'})"
    print(row)
    return results["BruteForce"]   # return OPT for greedy/FPTAS callers


def run_approx(name, values, weights, capacity, opt):
    """Run greedy and FPTAS; verify their guarantees."""
    global total_tests, total_pass

    gr = knapsack_greedy(capacity, values, weights)
    gap = ((opt - gr) / opt * 100) if opt > 0 else 0.0
    opt2_ok = (opt == 0) or (gr >= opt / 2 - 1e-9)
    total_tests += 1
    if opt2_ok:
        total_pass += 1
    else:
        failures.append((name, "Greedy-OPT/2", f">={opt/2:.1f}", gr))

    for eps in [0.1, 0.25, 0.5]:
        ft = knapsack_fptas(capacity, values, weights, epsilon=eps)
        floor = (1 - eps) * opt
        ft_ok = (opt == 0) or (ft >= floor - 1)
        total_tests += 1
        if ft_ok:
            total_pass += 1
        else:
            failures.append((name, f"FPTAS-eps={eps}", f">={floor:.0f}", ft))

    print(f"    {name:<40} OPT={opt}  Greedy={gr}(gap={gap:.1f}%,'OK' if opt2_ok else 'XX')  "
          f"FPTAS-0.25={knapsack_fptas(capacity, values, weights, 0.25)}")


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3 – PERFORMANCE MEASUREMENT
# ─────────────────────────────────────────────────────────────────────────────

def time_func(func, runs=3):
    """Return median wall-time in microseconds over `runs` calls."""
    times = []
    for _ in range(runs):
        t0 = time.perf_counter()
        func()
        times.append((time.perf_counter() - t0) * 1e6)
    return sorted(times)[len(times) // 2]


def measure_peak_memory_kb(func):
    """Return peak RSS increase in KB while running func."""
    gc.collect()
    tracemalloc.start()
    func()
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    return peak / 1024


def gen_random(n, W, seed=42):
    rng = random.Random(seed)
    values  = [rng.randint(1, 100) for _ in range(n)]
    weights = [rng.randint(1, W // 2 or 1) for _ in range(n)]
    return values, weights


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4 – kplib INSTANCE PARSER
# ─────────────────────────────────────────────────────────────────────────────

def parse_kp(path):
    """Parse a Pisinger .kp file; return (n, capacity, values, weights)."""
    with open(path) as f:
        lines = [l.strip() for l in f if l.strip()]
    n        = int(lines[0])
    capacity = int(lines[1])
    values, weights = [], []
    for line in lines[3: 3 + n]:
        v, w = line.split()
        values.append(int(v));  weights.append(int(w))
    return n, capacity, values, weights


# ─────────────────────────────────────────────────────────────────────────────
# MAIN REPORT
# ─────────────────────────────────────────────────────────────────────────────

def main():
    global total_tests, total_pass, failures

    print("=" * 72)
    print("   0/1 KNAPSACK — COMPLETE SANITY CHECK REPORT")
    print("=" * 72)

    # ── 1. ALGORITHMS IDENTIFIED ─────────────────────────────────────────────
    print_section("1. ALGORITHMS IDENTIFIED")
    algo_table = [
        ("Brute Force",      "brute_force.py",     "Recursive exhaustive search",         "O(2^n)",     "O(n) stack"),
        ("Memoization",      "memoization.py",     "Top-down DP (recursive + memo table)", "O(n·W)",     "O(n·W)"),
        ("Tabulation",       "tabulation.py",      "Bottom-up DP (2-D table + traceback)", "O(n·W)",     "O(n·W)"),
        ("Space-Optimised",  "space_optimised.py", "Bottom-up DP (1-D rolling array)",     "O(n·W)",     "O(W)"),
        ("Greedy Approx.",   "greedy.py",          "Sort by value/weight ratio; max(S1,S2)","O(n log n)", "O(n)"),
        ("FPTAS",            "fptas.py",           "Profit-indexed DP after value scaling", "O(n²/ε)",   "O(n/ε)"),
    ]
    print(f"    {'Algorithm':<20} {'File':<22} {'Strategy':<44} {'Time':<12} {'Space'}")
    print(f"    {'-'*20} {'-'*22} {'-'*44} {'-'*12} {'-'*12}")
    for row in algo_table:
        print(f"    {row[0]:<20} {row[1]:<22} {row[2]:<44} {row[3]:<12} {row[4]}")

    # ── 2. CORRECTNESS – STANDARD CASES ──────────────────────────────────────
    print_section("2. CORRECTNESS VERIFICATION — STANDARD CASES")
    print(f"    {'Test Name':<40} {'Results (OK=correct XX=wrong)'}")
    print(f"    {'-'*40} {'-'*60}")

    run_exact("Baseline (CLAUDE.md)",
              [60,100,120,80], [10,20,30,25], 50, 220)
    run_exact("Simple 3-item",
              [10,20,30], [5,10,15], 20, 40)
    run_exact("Single item — fits exactly",
              [100], [50], 50, 100)
    run_exact("Single item — exceeds capacity",
              [100], [60], 50, 0)
    run_exact("All items fit",
              [10,20,30], [5,10,15], 100, 60)
    run_exact("No items fit",
              [10,20,30], [15,20,30], 10, 0)
    run_exact("Capacity = 0",
              [60,100,120], [10,20,30], 0, 0)
    run_exact("Duplicate items — one fits",
              [50,50,50], [60,60,60], 50, 0)
    run_exact("Duplicate items — two fit (cap=50, wt=25 each)",
              [50,50,50], [25,25,25], 50, 100)
    run_exact("High value low weight dominance",
              [1000,1,1], [1,500,500], 500, 1000)
    run_exact("Exact capacity fill",
              [3,4,5], [2,3,5], 5, 7)
    run_exact("All equal values",
              [10,10,10,10], [3,4,5,6], 12, 30)
    run_exact("Adversarial — DP tie-break",
              [5,5,5,5], [3,4,5,6], 10, 10)
    run_exact("Large single item (greedy trap)",
              [10,6,6], [5,4,4], 8, 12)

    # ── 3. EDGE CASES ────────────────────────────────────────────────────────
    print_section("3. EDGE CASE HANDLING")
    print(f"    {'Edge Case':<40} {'Result'}")
    print(f"    {'-'*40} {'-'*40}")

    # n=0 (empty)
    for name, func_result in [
        ("BF  — n=0",        knapsack_brute_force(50, 0, [], [])),
        ("Memo — n=0",       knapsack_memoization(50, 0, [], [],
                                [[None]*51 for _ in range(1)])),
        ("Tab  — n=0",       knapsack_tabulation(50, [], [])[0]),
        ("SpOp — n=0",       knapsack_space_optimised([], [], 0, 50)),
        ("Grdy — n=0",       knapsack_greedy(50, [], [])),
        ("FPTAS— n=0",       knapsack_fptas(50, [], [], 0.25)),
    ]:
        ok = func_result == 0
        total_tests += 1
        if ok: total_pass += 1
        else: failures.append((name, "n=0", 0, func_result))
        print(f"    {name:<40} {func_result}  ({'OK' if ok else 'XX'} expected 0)")

    # capacity=1 (edge)
    val1 = knapsack_brute_force(1, 3, [10,5,3], [2,3,1])
    expected1 = 3
    ok1 = val1 == expected1
    total_tests += 1
    if ok1: total_pass += 1
    else: failures.append(("capacity=1", "BF", expected1, val1))
    print(f"    {'BF  — capacity=1 (lightest item=3)':<40} {val1}  ({'OK' if ok1 else 'XX'} expected {expected1})")

    # ── 4. GREEDY FAILURE PROOF ───────────────────────────────────────────────
    print_section("4. GREEDY FAILURE DETECTION (Expected Approximation Gaps)")
    print()
    print("    Case 1 — 'ratio trap' (OPT=12, greedy should return 10)")
    v, w, cap = [10, 6, 6], [5, 4, 4], 8
    opt_tab = knapsack_tabulation(cap, v, w)[0]
    gr_val  = knapsack_greedy(cap, v, w)
    gap = (opt_tab - gr_val) / opt_tab * 100
    greedy_not_optimal = gr_val < opt_tab
    total_tests += 1
    if greedy_not_optimal: total_pass += 1
    else: failures.append(("Greedy not exact (ratio trap)", "Greedy", f"<{opt_tab}", gr_val))
    print(f"      OPT={opt_tab}  Greedy={gr_val}  Gap={gap:.1f}%  "
          f"Greedy≠OPT: {'OK (expected approximation)' if greedy_not_optimal else 'XX (bug — greedy matched OPT accidentally)'}")
    print(f"      OPT/2 guarantee: {gr_val}>={opt_tab/2:.1f}? {'OK' if gr_val >= opt_tab/2 else 'XX VIOLATED'}")

    print()
    print("    Case 2 — CLAUDE.md baseline (OPT=220, greedy should return 160)")
    v2, w2, cap2 = [60,100,120,80], [10,20,30,25], 50
    gr2 = knapsack_greedy(cap2, v2, w2)
    gap2 = (220 - gr2) / 220 * 100
    print(f"      OPT=220  Greedy={gr2}  Gap={gap2:.1f}%  OPT/2={110}  Greedy>={110}? {'OK' if gr2 >= 110 else 'XX'}")

    # ── 5. FPTAS GUARANTEE SWEEP ──────────────────────────────────────────────
    print_section("5. FPTAS APPROXIMATION GUARANTEE SWEEP")
    print(f"    {'Test':<30} {'OPT':<6} {'eps':<6} {'Result':<8} {'Floor':<8} {'Status'}")
    print(f"    {'-'*30} {'-'*5} {'-'*5} {'-'*7} {'-'*7} {'-'*8}")

    fptas_cases = [
        ("Baseline",    [60,100,120,80], [10,20,30,25], 50,  220),
        ("3-item",      [10,20,30],      [5,10,15],     20,  40),
        ("High n (n=8)",[12,8,15,20,5,11,9,7],[4,3,6,7,2,5,4,3], 15, None),
    ]
    for cname, cv, cw, ccap, copt in fptas_cases:
        if copt is None:
            copt = knapsack_tabulation(ccap, cv, cw)[0]
        for eps in [0.1, 0.25, 0.5]:
            ft = knapsack_fptas(ccap, cv, cw, epsilon=eps)
            floor = (1 - eps) * copt
            ok = (copt == 0) or (ft >= floor - 1)
            total_tests += 1
            if ok: total_pass += 1
            else: failures.append((cname, f"FPTAS-eps={eps}", f">={floor:.0f}", ft))
            print(f"    {cname:<30} {copt:<6} {eps:<6.2f} {ft:<8} {floor:<8.1f} {'PASS OK' if ok else 'FAIL XX'}")

    # ── 6. PERFORMANCE TABLE ──────────────────────────────────────────────────
    print_section("6. PERFORMANCE ANALYSIS")
    print_subsection("6a. Exact Algorithms — increasing n (W=1000, random items)")
    print(f"\n    {'n':>5} {'BF (µs)':>12} {'Memo (µs)':>12} {'Tab (µs)':>12} {'SpOp (µs)':>12} {'Memo mem(KB)':>14}")
    print(f"    {'-'*5} {'-'*12} {'-'*12} {'-'*12} {'-'*12} {'-'*14}")

    W_perf = 1000
    for n_perf in [5, 8, 10, 12, 15, 18, 20]:
        v_p, w_p = gen_random(n_perf, W_perf)
        memo_p   = [[None]*(W_perf+1) for _ in range(n_perf+1)]

        t_bf   = time_func(lambda: knapsack_brute_force(W_perf, n_perf, v_p, w_p))
        t_mem  = time_func(lambda: knapsack_memoization(W_perf, n_perf, v_p, w_p,
                              [[None]*(W_perf+1) for _ in range(n_perf+1)]))
        t_tab  = time_func(lambda: knapsack_tabulation(W_perf, v_p, w_p))
        t_sp   = time_func(lambda: knapsack_space_optimised(v_p, w_p, n_perf, W_perf))
        mem_kb = measure_peak_memory_kb(lambda: knapsack_memoization(W_perf, n_perf, v_p, w_p,
                              [[None]*(W_perf+1) for _ in range(n_perf+1)]))

        print(f"    {n_perf:>5} {t_bf:>12.1f} {t_mem:>12.1f} {t_tab:>12.1f} {t_sp:>12.1f} {mem_kb:>14.1f}")

    print_subsection("6b. DP Algorithms only — larger n (W=500, brute-force excluded)")
    print(f"\n    {'n':>6} {'W':>6} {'Memo (ms)':>11} {'Tab (ms)':>11} {'SpOp (ms)':>11} {'SpOp mem(KB)':>14}")
    print(f"    {'-'*6} {'-'*6} {'-'*11} {'-'*11} {'-'*11} {'-'*14}")

    # Memoization recursion depth = n; default Python limit is 1000.
    # Capping at n=800 (temporarily raise limit to avoid RecursionError in test).
    old_rlimit = sys.getrecursionlimit()
    sys.setrecursionlimit(2000)
    for n_p, W_p in [(50,500),(100,500),(200,500),(500,500),(800,500)]:
        v_p, w_p = gen_random(n_p, W_p)
        t_mem = time_func(lambda: knapsack_memoization(W_p, n_p, v_p, w_p,
                          [[None]*(W_p+1) for _ in range(n_p+1)]), runs=2) / 1000
        t_tab = time_func(lambda: knapsack_tabulation(W_p, v_p, w_p), runs=2) / 1000
        t_sp  = time_func(lambda: knapsack_space_optimised(v_p, w_p, n_p, W_p), runs=2) / 1000
        mem_sp = measure_peak_memory_kb(lambda: knapsack_space_optimised(v_p, w_p, n_p, W_p))
        print(f"    {n_p:>6} {W_p:>6} {t_mem:>11.3f} {t_tab:>11.3f} {t_sp:>11.3f} {mem_sp:>14.1f}")
    sys.setrecursionlimit(old_rlimit)

    print_subsection("6c. Capacity scaling — n=50 fixed, W increasing")
    print(f"\n    {'W':>8} {'Tab (ms)':>10} {'SpOp (ms)':>11} {'Tab mem(KB)':>13} {'SpOp mem(KB)':>14}")
    print(f"    {'-'*8} {'-'*10} {'-'*11} {'-'*13} {'-'*14}")
    n_fixed = 50
    for W_scale in [100, 500, 1000, 5000, 10000]:
        v_s, w_s = gen_random(n_fixed, W_scale)
        t_tab = time_func(lambda: knapsack_tabulation(W_scale, v_s, w_s), runs=2) / 1000
        t_sp  = time_func(lambda: knapsack_space_optimised(v_s, w_s, n_fixed, W_scale), runs=2) / 1000
        mem_t  = measure_peak_memory_kb(lambda: knapsack_tabulation(W_scale, v_s, w_s))
        mem_sp = measure_peak_memory_kb(lambda: knapsack_space_optimised(v_s, w_s, n_fixed, W_scale))
        print(f"    {W_scale:>8} {t_tab:>10.3f} {t_sp:>11.3f} {mem_t:>13.1f} {mem_sp:>14.1f}")

    # ── 7. RECURSION / OVERFLOW RISK ─────────────────────────────────────────
    print_section("7. FAILURE DETECTION — Recursion & Memory Risks")
    real_rlimit = sys.getrecursionlimit()
    print(f"\n    Python default recursion limit: {real_rlimit}")
    print(f"    BruteForce/Memoization depth   : O(n)  => safe up to n ~ {real_rlimit - 20}")
    print(f"    RISK: n >= {real_rlimit - 15} will raise RecursionError for both recursive algos")

    # Use weights > capacity so BF/Memo follow a LINEAR recursion path (O(n) calls, depth n).
    # This lets us safely trigger RecursionError without exponential blowup.
    tmp_limit  = 40
    n_crash    = 35   # depth n=35 > (40 - ~8 existing frames = 32 available)
    v_lin  = [1] * n_crash
    w_lin  = [999] * n_crash   # all weights exceed capacity → single-branch linear recursion
    cap_lin = 10

    print(f"\n    [BruteForce]  RecursionError demo: limit={tmp_limit}, n={n_crash}, "
          f"all-weights-too-heavy (linear O(n) recursion) ...", end="", flush=True)
    sys.setrecursionlimit(tmp_limit)
    try:
        knapsack_brute_force(cap_lin, n_crash, v_lin, w_lin)
        print(" SURVIVED (depth < available frames)")
    except RecursionError:
        print(" RecursionError CONFIRMED")
    finally:
        sys.setrecursionlimit(real_rlimit)

    print(f"\n    [Memoization] RecursionError demo: limit={tmp_limit}, n={n_crash} ...",
          end="", flush=True)
    sys.setrecursionlimit(tmp_limit)
    try:
        memo_r = [[None] * (cap_lin + 1) for _ in range(n_crash + 1)]
        knapsack_memoization(cap_lin, n_crash, v_lin, w_lin, memo_r)
        print(" SURVIVED (depth < available frames)")
    except RecursionError:
        print(" RecursionError CONFIRMED")
    finally:
        sys.setrecursionlimit(real_rlimit)

    # BF timing wall for n=20 (2^20 = 1M calls — fast in Python)
    n_bf_time = 20
    print(f"\n    [BruteForce]  Timing n={n_bf_time} (2^{n_bf_time}~1M calls) ...", end="", flush=True)
    v_t, w_t = gen_random(n_bf_time, 200)
    t0 = time.perf_counter()
    knapsack_brute_force(200, n_bf_time, v_t, w_t)
    elapsed = time.perf_counter() - t0
    print(f" {elapsed:.2f}s  {'OK' if elapsed < 30 else 'SLOW'}")
    print(f"    Extrapolated n=30 (2^30~1B): ~{elapsed * 2**(30 - n_bf_time):.0f}s  (infeasible)")

    # Tabulation large-capacity memory warning
    n_mem, W_mem = 10, 100_000
    print(f"\n    [Tabulation] n={n_mem}, W={W_mem} (table={n_mem*W_mem:,} cells) ...", end="", flush=True)
    v_lw, w_lw = gen_random(n_mem, W_mem)
    mem_tab = measure_peak_memory_kb(lambda: knapsack_tabulation(W_mem, v_lw, w_lw))
    print(f" peak={mem_tab:.0f} KB  (~{mem_tab/1024:.1f} MB)")

    W_huge = 1_000_000
    n_huge = 5
    print(f"\n    [SpaceOpt]   n={n_huge}, W={W_huge} (array={W_huge+1:,} cells) ...", end="", flush=True)
    v_hu, w_hu = gen_random(n_huge, W_huge)
    mem_sp_hu = measure_peak_memory_kb(lambda: knapsack_space_optimised(v_hu, w_hu, n_huge, W_huge))
    print(f" peak={mem_sp_hu:.0f} KB  (~{mem_sp_hu/1024:.1f} MB)")

    # ── 8. USE CASE COVERAGE ─────────────────────────────────────────────────
    print_section("8. USE-CASE COVERAGE")
    print(f"    {'Scenario':<40} {'OPT':<6} {'All Exact Match'}")
    print(f"    {'-'*40} {'-'*5} {'-'*20}")

    uc_cases = [
        ("Dense value dist. (values≈weights)",
         [50,55,60,45,52], [48,50,55,43,49], 100),
        ("Sparse weights (all small)",
         [10,20,30,40,50], [1,1,1,1,1], 3),
        ("High val / low wt dominance",
         [1000,2,3,4], [1,100,100,100], 150),
        ("Uniform distribution",
         [10,10,10,10,10], [10,10,10,10,10], 30),
        ("Adversarial — fractional gap large",
         [10,6,6], [5,4,4], 8),
        ("n=1 item fits",
         [99], [50], 50),
        ("n=1 item too heavy",
         [99], [51], 50),
    ]
    for scenario, sv, sw, sc in uc_cases:
        opt = knapsack_tabulation(sc, sv, sw)[0]
        n_uc = len(sv)
        memo_uc = [[None]*(sc+1) for _ in range(n_uc+1)]
        exact = [
            knapsack_brute_force(sc, n_uc, sv, sw),
            knapsack_memoization(sc, n_uc, sv, sw, memo_uc),
            opt,
            knapsack_space_optimised(sv, sw, n_uc, sc),
        ]
        all_match = len(set(exact)) == 1
        total_tests += 4
        if all_match: total_pass += 4
        else:
            failures.append((scenario, "Consistency", f"all={opt}", str(set(exact))))
        print(f"    {scenario:<40} {opt:<6} {'OK' if all_match else 'XX '+str(set(exact))}")

    # ── 9. KPLIB INSTANCE VALIDATION ────────────────────────────────────────
    print_section("9. KPLIB BENCHMARK VALIDATION (Pisinger Uncorrelated n=50)")
    kplib_base = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "testcases", "kplib", "00Uncorrelated", "n00050", "R01000"
    )
    kp_files = [f"s{str(i).zfill(3)}.kp" for i in range(5)]
    print(f"\n    {'File':<12} {'n':>4} {'W':>8} {'Tab OPT':>9} {'SpOp':>7} {'Memo':>7} {'Match'}")
    print(f"    {'-'*12} {'-'*4} {'-'*8} {'-'*9} {'-'*7} {'-'*7} {'-'*7}")
    for fname in kp_files:
        fpath = os.path.join(kplib_base, fname)
        if not os.path.isfile(fpath):
            print(f"    {fname:<12} NOT FOUND — skipping")
            continue
        kn, kW, kv, kw = parse_kp(fpath)
        tab_opt, _ = knapsack_tabulation(kW, kv, kw)
        sp_opt     = knapsack_space_optimised(kv, kw, kn, kW)
        kmemo      = [[None]*(kW+1) for _ in range(kn+1)]
        m_opt      = knapsack_memoization(kW, kn, kv, kw, kmemo)
        match = (tab_opt == sp_opt == m_opt)
        total_tests += 3
        if match: total_pass += 3
        else: failures.append((fname, "kplib-consistency", str(tab_opt), str({sp_opt, m_opt})))
        print(f"    {fname:<12} {kn:>4} {kW:>8} {tab_opt:>9} {sp_opt:>7} {m_opt:>7} {'OK' if match else 'XX'}")

    # ── FINAL VERDICT ────────────────────────────────────────────────────────
    print_section("FINAL VERDICT")
    print(f"\n    Total assertions : {total_tests}")
    print(f"    Passed           : {total_pass}")
    print(f"    Failed           : {total_tests - total_pass}")

    if failures:
        print(f"\n    FAILED CHECKS:")
        for tc, algo, exp, got in failures:
            print(f"      [{tc}] {algo}: expected={exp}  got={got}")
        verdict = "NEEDS FIXES"
        print(f"\n    VERDICT: XX  {verdict}")
    else:
        print(f"\n    VERDICT: OK  SAFE — all assertions passed")

    # ── COMPLEXITY SUMMARY ───────────────────────────────────────────────────
    print_section("COMPLEXITY ANALYSIS SUMMARY")
    rows = [
        ("Brute Force",     "O(2^n)",   "O(n)",   "O(2^n)",   "O(2^n)",   "O(2^n)",   "Not scalable; n>25 infeasible"),
        ("Memoization",     "O(n·W)",   "O(n·W)", "O(n·W)",   "O(n·W)",   "O(n·W)",   "RecursionError risk for n>~990"),
        ("Tabulation",      "O(n·W)",   "O(n·W)", "O(n·W)",   "O(n·W)",   "O(n·W)",   "OOM risk for large W (e.g. W=10^7)"),
        ("Space-Optimised", "O(n·W)",   "O(W)",   "O(n·W)",   "O(n·W)",   "O(n·W)",   "Best exact for large W"),
        ("Greedy",          "O(n logn)","O(n)",   "O(n logn)","O(n logn)","O(n logn)", "Approx only; OPT/2 guaranteed"),
        ("FPTAS",           "O(n²/ε)", "O(n/ε)", "O(n²/ε)", "O(n²/ε)", "O(n²/ε)",  "(1-ε)·OPT guaranteed"),
    ]
    print(f"\n    {'Algorithm':<18} {'T-Best':<12} {'S-Best':<10} {'T-Avg':<12} {'T-Worst':<12} {'Empirical':<12} {'Notes'}")
    print(f"    {'-'*18} {'-'*12} {'-'*10} {'-'*12} {'-'*12} {'-'*12} {'-'*35}")
    for r in rows:
        print(f"    {r[0]:<18} {r[1]:<12} {r[2]:<10} {r[3]:<12} {r[4]:<12} {r[5]:<12} {r[6]}")

    print()


if __name__ == "__main__":
    main()
