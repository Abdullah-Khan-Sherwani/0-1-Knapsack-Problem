import os, sys, csv, time

_SRC  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
sys.path.insert(0, _ROOT)

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.parse_kp                   import parse_kp

KPLIB_ROOT         = os.path.join(_ROOT, 'testcases', 'kplib')
RESULTS_DIR        = os.path.join(_ROOT, 'results')
INSTANCES_PER_LEAF = 5

# Skip thresholds — prevent OOM / multi-minute runs
BF_MAX_N     = 20          # 2^20 ≈ 1M recursive calls
MEMO_MAX_NW  = 15_000_000  # ~120 MB memo table
TAB_MAX_NW   = 30_000_000  # ~240 MB dp table
SPOPT_MAX_NW = 50_000_000  # ~50M loop iterations

FIELDNAMES = [
    'category', 'n_label', 'ratio', 'instance',
    'n', 'capacity', 'algorithm', 'runtime_ms', 'result', 'skipped',
]


# ── Algorithm runners (named functions avoid closure issues) ──────────────────

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


ALGORITHMS = [
    ('BruteForce',     _run_bf,     lambda n, W: n > BF_MAX_N),
    ('Memoization',    _run_memo,   lambda n, W: n * W > MEMO_MAX_NW),
    ('Tabulation',     _run_tab,    lambda n, W: n * W > TAB_MAX_NW),
    ('SpaceOptimised', _run_spopt,  lambda n, W: n * W > SPOPT_MAX_NW),
    ('Greedy',         _run_greedy, lambda n, W: False),
]


# ── Path utilities ────────────────────────────────────────────────────────────

def find_leaf_folders(root):
    """Return all directories that directly contain .kp files."""
    leaves = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not dirnames and any(f.endswith('.kp') for f in filenames):
            leaves.append(dirpath)
    return sorted(leaves)


def get_instances(folder, count=INSTANCES_PER_LEAF):
    files = sorted(f for f in os.listdir(folder) if f.endswith('.kp'))
    return [os.path.join(folder, f) for f in files[:count]]


def parse_path(path):
    """Extract (category, n_label, ratio, instance) from a .kp filepath."""
    parts = path.replace('\\', '/').split('/')
    return parts[-4], parts[-3], parts[-2], os.path.splitext(parts[-1])[0]


# ── Main benchmark ────────────────────────────────────────────────────────────

def run_benchmarks():
    if not os.path.isdir(KPLIB_ROOT):
        print(f"[ERROR] kplib not found at:\n  {KPLIB_ROOT}\n"
              f"Clone it with: git clone https://github.com/likr/kplib.git testcases/kplib")
        return None

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, 'benchmark_results.csv')

    leaves = find_leaf_folders(KPLIB_ROOT)
    total  = len(leaves)
    print(f"Found {total} leaf folders — running first {INSTANCES_PER_LEAF} instances each.\n")

    with open(csv_path, 'w', newline='') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()

        for idx, leaf in enumerate(leaves, 1):
            cat, n_lbl, ratio, _ = parse_path(leaf + '/x.kp')
            instances = get_instances(leaf)
            print(f"[{idx:3d}/{total}] {cat}/{n_lbl}/{ratio}  "
                  f"({len(instances)} instances)", flush=True)

            for fp in instances:
                cat, n_lbl, ratio, inst = parse_path(fp)
                n, capacity, values, weights = parse_kp(fp)

                for alg_name, run_fn, should_skip in ALGORITHMS:
                    row = dict(
                        category=cat, n_label=n_lbl, ratio=ratio,
                        instance=inst, n=n, capacity=capacity,
                        algorithm=alg_name,
                    )
                    if should_skip(n, capacity):
                        row.update(runtime_ms=None, result=None, skipped=True)
                    else:
                        try:
                            t0  = time.perf_counter()
                            res = run_fn(n, capacity, values, weights)
                            ms  = (time.perf_counter() - t0) * 1000
                            row.update(
                                runtime_ms=round(ms, 4),
                                result=res,
                                skipped=False,
                            )
                        except Exception as exc:
                            print(f"    [WARN] {alg_name} on {os.path.basename(fp)}: {exc}")
                            row.update(runtime_ms=None, result=None, skipped=True)
                    writer.writerow(row)

    print(f"\nResults saved to: {csv_path}")
    return csv_path
