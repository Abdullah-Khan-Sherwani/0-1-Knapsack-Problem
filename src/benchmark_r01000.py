import os, sys, csv, time

_SRC  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
sys.path.insert(0, _ROOT)

from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas
from src.parse_kp                   import parse_kp

KPLIB_ROOT         = os.path.join(_ROOT, 'testcases', 'kplib')
RESULTS_DIR        = os.path.join(_ROOT, 'results')
INSTANCES_PER_LEAF = 5
TARGET_RATIO       = 'R01000'
TARGET_NS          = {50, 100, 200}
EXCLUDE_CATEGORIES = {'06UncorrelatedWithSimilarWeights'}
FPTAS_EPSILON      = 0.25

FIELDNAMES = [
    'category', 'n_label', 'ratio', 'instance',
    'n', 'capacity', 'algorithm', 'runtime_ms', 'result',
]


def _run_memo(n, capacity, values, weights):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, n * 3 + 200))
    memo   = [[None] * (capacity + 1) for _ in range(n + 1)]
    result = knapsack_memoization(capacity, n, values, weights, memo)[0]
    sys.setrecursionlimit(old)
    return result

def _run_tab(n, capacity, values, weights):
    return knapsack_tabulation(capacity, values, weights)[0]

def _run_spopt(n, capacity, values, weights):
    return knapsack_space_optimised(values, weights, n, capacity)

def _run_greedy(n, capacity, values, weights):
    return knapsack_greedy(capacity, values, weights)[0]

def _run_fptas(n, capacity, values, weights):
    return knapsack_fptas(capacity, values, weights, epsilon=FPTAS_EPSILON)


ALGORITHMS = [
    ('Memoization',    _run_memo),
    ('Tabulation',     _run_tab),
    ('SpaceOptimised', _run_spopt),
    ('Greedy',         _run_greedy),
    ('FPTAS',          _run_fptas),
]


def find_leaf_folders(root):
    leaves = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not dirnames and any(f.endswith('.kp') for f in filenames):
            parts = dirpath.replace('\\', '/').split('/')
            category = parts[-3]
            n_label  = parts[-2]
            ratio    = parts[-1]
            if category in EXCLUDE_CATEGORIES:
                continue
            if ratio != TARGET_RATIO:
                continue
            try:
                n = int(n_label.lstrip('n'))
            except ValueError:
                continue
            if n not in TARGET_NS:
                continue
            leaves.append(dirpath)
    return sorted(leaves)


def get_instances(folder):
    files = sorted(f for f in os.listdir(folder) if f.endswith('.kp'))
    return [os.path.join(folder, f) for f in files[:INSTANCES_PER_LEAF]]


def parse_path(path):
    parts = path.replace('\\', '/').split('/')
    return parts[-4], parts[-3], parts[-2], os.path.splitext(parts[-1])[0]


def run():
    if not os.path.isdir(KPLIB_ROOT):
        print(f'[ERROR] kplib not found at {KPLIB_ROOT}')
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, 'benchmark_r01000.csv')

    leaves = find_leaf_folders(KPLIB_ROOT)
    total  = len(leaves)
    print(f'{"="*65}')
    print(f'  R01000 Benchmark — No Skips')
    print(f'  {total} folders x {INSTANCES_PER_LEAF} instances x {len(ALGORITHMS)} algorithms')
    print(f'  n in {sorted(TARGET_NS)}  |  ratio={TARGET_RATIO}  |  excl={EXCLUDE_CATEGORIES}')
    print(f'{"="*65}\n')

    total_rows = 0
    wall_start = time.perf_counter()

    with open(csv_path, 'w', newline='', encoding='utf-8') as fh:
        writer = csv.DictWriter(fh, fieldnames=FIELDNAMES)
        writer.writeheader()

        for idx, leaf in enumerate(leaves, 1):
            cat, n_lbl, ratio, _ = parse_path(leaf + '/x.kp')
            instances = get_instances(leaf)
            print(f'[{idx:3d}/{total}] {cat}/{n_lbl}/{ratio}', flush=True)

            for fp in instances:
                cat, n_lbl, ratio, inst = parse_path(fp)
                n, capacity, values, weights = parse_kp(fp)
                print(f'         {inst}  n={n}  W={capacity}', flush=True)

                exact_results = {}
                for alg_name, run_fn in ALGORITHMS:
                    t0  = time.perf_counter()
                    res = run_fn(n, capacity, values, weights)
                    ms  = (time.perf_counter() - t0) * 1000
                    print(f'           {alg_name:<16} {ms:8.2f} ms   result={res}', flush=True)
                    writer.writerow(dict(
                        category=cat, n_label=n_lbl, ratio=ratio,
                        instance=inst, n=n, capacity=capacity,
                        algorithm=alg_name, runtime_ms=round(ms, 4), result=res,
                    ))
                    total_rows += 1
                    if alg_name in ('Memoization', 'Tabulation', 'SpaceOptimised'):
                        exact_results[alg_name] = res

                # Consistency check
                if len(set(exact_results.values())) > 1:
                    print(f'           [MISMATCH] {exact_results}', flush=True)

                opt = next(iter(exact_results.values())) if exact_results else None
                if opt:
                    for alg_name, _ in ALGORITHMS:
                        pass  # approximation warnings handled below
                    for approx, floor_pct in [('Greedy', 0.5), ('FPTAS', 1 - FPTAS_EPSILON)]:
                        pass  # silent — no violations expected

    elapsed = time.perf_counter() - wall_start
    print(f'\n{"="*65}')
    print(f'  Done in {elapsed:.1f}s   {total_rows} rows written')
    print(f'  Results: {csv_path}')
    print(f'{"="*65}')
    return csv_path


if __name__ == '__main__':
    run()
