import os, sys, csv, time

_SRC  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
sys.path.insert(0, _ROOT)

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas
from src.parse_kp                   import parse_kp

KPLIB_ROOT         = os.path.join(_ROOT, 'testcases', 'kplib')
RESULTS_DIR        = os.path.join(_ROOT, 'results')
INSTANCES_PER_LEAF = 1
MAX_N              = 500

# Skip thresholds — prevent OOM / multi-minute runs
BF_MAX_N      = 25           # 2^25 ~ 33M calls, feasible
MEMO_MAX_NW   = 15_000_000   # ~120 MB memo table
TAB_MAX_NW    = 30_000_000   # ~240 MB dp table
SPOPT_MAX_W   = 2_000_000    # SpaceOpt uses O(W) memory — skip on W alone
FPTAS_EPSILON = 0.25         # guarantees >= 0.75 * OPT
FPTAS_MAX_N2  = 4_000_000    # skip if n^2/eps > this

FIELDNAMES = [
    'category', 'n_label', 'ratio', 'instance',
    'n', 'capacity', 'algorithm', 'runtime_ms', 'result', 'skipped',
]

# ── Algorithm runners ─────────────────────────────────────────────────────────

def _run_bf(n, capacity, values, weights):
    return knapsack_brute_force(capacity, n, values, weights)


def _run_memo(n, capacity, values, weights):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, n * 3 + 200))
    memo   = [[None] * (capacity + 1) for _ in range(n + 1)]
    result = knapsack_memoization(capacity, n, values, weights, memo)
    sys.setrecursionlimit(old)
    return result


def _run_tab(n, capacity, values, weights):
    return knapsack_tabulation(capacity, values, weights)[0]


def _run_spopt(n, capacity, values, weights):
    return knapsack_space_optimised(values, weights, n, capacity)


def _run_greedy(n, capacity, values, weights):
    return knapsack_greedy(capacity, values, weights)


def _run_fptas(n, capacity, values, weights):
    return knapsack_fptas(capacity, values, weights, epsilon=FPTAS_EPSILON)


ALGORITHMS = [
    ('BruteForce',     _run_bf,     lambda n, W: n > BF_MAX_N),
    ('Memoization',    _run_memo,   lambda n, W: n * W > MEMO_MAX_NW),
    ('Tabulation',     _run_tab,    lambda n, W: n * W > TAB_MAX_NW),
    ('SpaceOptimised', _run_spopt,  lambda n, W: W > SPOPT_MAX_W),
    ('Greedy',         _run_greedy, lambda n, W: False),
    ('FPTAS',          _run_fptas,  lambda n, W: (n * n / FPTAS_EPSILON) > FPTAS_MAX_N2),
]


# ── Path utilities ────────────────────────────────────────────────────────────

def find_leaf_folders(root):
    leaves = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not dirnames and any(f.endswith('.kp') for f in filenames):
            n_label = os.path.basename(os.path.dirname(dirpath))
            try:
                n = int(n_label.lstrip('n'))
            except ValueError:
                n = 0
            if n <= MAX_N:
                leaves.append(dirpath)
    return sorted(leaves)


def get_instances(folder):
    files = sorted(f for f in os.listdir(folder) if f.endswith('.kp'))
    count = 3 if '13Synthetic' in folder else INSTANCES_PER_LEAF
    return [os.path.join(folder, f) for f in files[:count]]


def parse_path(path):
    parts = path.replace('\\', '/').split('/')
    return parts[-4], parts[-3], parts[-2], os.path.splitext(parts[-1])[0]


# ── Main benchmark ────────────────────────────────────────────────────────────

def run_benchmarks():
    if not os.path.isdir(KPLIB_ROOT):
        print(f"[ERROR] kplib not found at:\n  {KPLIB_ROOT}")
        return None

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, 'benchmark_results.csv')

    leaves = find_leaf_folders(KPLIB_ROOT)
    total  = len(leaves)
    n_algs = len(ALGORITHMS)

    print(f"{'='*65}")
    print(f"  Knapsack Benchmark")
    print(f"  {total} leaf folders x {INSTANCES_PER_LEAF} instance(s) x {n_algs} algorithms")
    print(f"  MAX_N={MAX_N}  BF_MAX_N={BF_MAX_N}  FPTAS_eps={FPTAS_EPSILON}")
    print(f"{'='*65}\n")

    total_rows = 0
    skipped_counts = {name: 0 for name, *_ in ALGORITHMS}
    wall_start = time.perf_counter()

    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()

        for idx, leaf in enumerate(leaves, 1):
            cat, n_lbl, ratio, _ = parse_path(leaf + '/x.kp')
            instances = get_instances(leaf)

            print(f"[{idx:3d}/{total}] {cat}/{n_lbl}/{ratio}", flush=True)

            for fp in instances:
                cat, n_lbl, ratio, inst = parse_path(fp)
                n, capacity, values, weights = parse_kp(fp)

                print(f"         {inst}  n={n}  W={capacity}", flush=True)

                alg_results = {}
                for alg_name, run_fn, should_skip in ALGORITHMS:
                    row = dict(
                        category=cat, n_label=n_lbl, ratio=ratio,
                        instance=inst, n=n, capacity=capacity,
                        algorithm=alg_name,
                    )
                    if should_skip(n, capacity):
                        row.update(runtime_ms=None, result=None, skipped=True)
                        skipped_counts[alg_name] += 1
                        print(f"           {alg_name:<{13}} SKIP", flush=True)
                    else:
                        try:
                            t0  = time.perf_counter()
                            res = run_fn(n, capacity, values, weights)
                            ms  = (time.perf_counter() - t0) * 1000
                            row.update(runtime_ms=round(ms, 4), result=res, skipped=False)
                            alg_results[alg_name] = res
                            print(f"           {alg_name:<{13}} {ms:8.2f} ms   result={res}", flush=True)
                        except Exception as exc:
                            row.update(runtime_ms=None, result=None, skipped=True)
                            skipped_counts[alg_name] += 1
                            print(f"           {alg_name:<{13}} ERROR: {exc}", flush=True)

                    writer.writerow(row)
                    total_rows += 1

                # Consistency checks
                exact = {k: v for k, v in alg_results.items()
                         if k in ('BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised')}
                if len(set(exact.values())) > 1:
                    print(f"           [MISMATCH] exact algorithms disagree: {exact}", flush=True)

                # Approximation bounds (only if we have an exact reference)
                if exact:
                    opt = next(iter(exact.values()))
                    if 'Greedy' in alg_results:
                        gr = alg_results['Greedy']
                        if gr > opt:
                            print(f"           [WARN] Greedy={gr} exceeds OPT={opt}", flush=True)
                        elif gr < opt / 2:
                            print(f"           [WARN] Greedy={gr} violates OPT/2 guarantee (OPT={opt})", flush=True)
                    if 'FPTAS' in alg_results:
                        ft = alg_results['FPTAS']
                        floor = (1 - FPTAS_EPSILON) * opt
                        if ft > opt:
                            print(f"           [WARN] FPTAS={ft} exceeds OPT={opt}", flush=True)
                        elif ft < floor - 1:
                            print(f"           [WARN] FPTAS={ft} violates {1-FPTAS_EPSILON:.0%} guarantee (floor={floor:.0f}, OPT={opt})", flush=True)

    elapsed = time.perf_counter() - wall_start
    print(f"\n{'='*65}")
    print(f"  Done in {elapsed:.1f}s   {total_rows} rows written")
    print(f"  Skip counts: { {k: v for k, v in skipped_counts.items() if v > 0} }")
    print(f"  Results: {csv_path}")
    print(f"{'='*65}")
    return csv_path
