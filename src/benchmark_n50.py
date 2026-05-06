import os, sys, csv, time

_SRC  = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(_SRC)
sys.path.insert(0, _ROOT)

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
# from src.algorithms.space_optimised import knapsack_space_optimised  # deprecated
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas
from src.parse_kp                   import parse_kp

KPLIB_ROOT         = os.path.join(_ROOT, 'testcases', 'kplib')
RESULTS_DIR        = os.path.join(_ROOT, 'results')
MAX_N              = 100
INSTANCES_PER_LEAF = 5
FPTAS_EPSILON      = 0.25
BF_MAX_N           = 25
MEMO_MAX_NW        = 8_000_000     # avoid pathological memoization runs
TAB_MAX_NW         = 12_000_000

FIELDNAMES = [
    'category', 'n_label', 'ratio', 'instance',
    'n', 'capacity', 'algorithm', 'runtime_ms', 'result', 'skipped',
]


# ── Runners ───────────────────────────────────────────────────────────────────

def _run_bf(n, capacity, values, weights):
    return knapsack_brute_force(capacity, n, values, weights)[0]

def _run_memo(n, capacity, values, weights):
    old = sys.getrecursionlimit()
    sys.setrecursionlimit(max(old, n * 3 + 200))
    memo   = [[None] * (capacity + 1) for _ in range(n + 1)]
    result = knapsack_memoization(capacity, n, values, weights, memo)[0]
    sys.setrecursionlimit(old)
    return result

def _run_tab(n, capacity, values, weights):
    return knapsack_tabulation(capacity, values, weights)[0]

def _run_greedy(n, capacity, values, weights):
    return knapsack_greedy(capacity, values, weights)[0]

def _run_fptas(n, capacity, values, weights):
    return knapsack_fptas(capacity, values, weights, epsilon=FPTAS_EPSILON)[0]


ALGORITHMS = [
    ('BruteForce',     _run_bf,     lambda n, W: n > BF_MAX_N),
    ('Memoization',    _run_memo,   lambda n, W: n * W > MEMO_MAX_NW),
    ('Tabulation',     _run_tab,    lambda n, W: n * W > TAB_MAX_NW),
    # ('SpaceOptimised', _run_spopt,  lambda n, W: False),  # deprecated
    ('Greedy',         _run_greedy, lambda n, W: False),
    ('FPTAS',          _run_fptas,  lambda n, W: False),
]


# ── Folder discovery ──────────────────────────────────────────────────────────

def find_leaf_folders(root):
    leaves = []
    for dirpath, dirnames, filenames in os.walk(root):
        if not dirnames and any(f.endswith('.kp') for f in filenames):
            parts = dirpath.replace('\\', '/').split('/')
            n_label = parts[-2]
            try:
                n = int(n_label.lstrip('n'))
            except ValueError:
                continue
            if n <= MAX_N:
                leaves.append(dirpath)
    return sorted(leaves)


def get_instances(folder):
    files = sorted(f for f in os.listdir(folder) if f.endswith('.kp'))
    return [os.path.join(folder, f) for f in files[:INSTANCES_PER_LEAF]]


def parse_path(path):
    parts = path.replace('\\', '/').split('/')
    return parts[-4], parts[-3], parts[-2], os.path.splitext(parts[-1])[0]


# ── Main ──────────────────────────────────────────────────────────────────────

def run():
    if not os.path.isdir(KPLIB_ROOT):
        print(f'[ERROR] kplib not found at {KPLIB_ROOT}')
        return

    os.makedirs(RESULTS_DIR, exist_ok=True)
    csv_path = os.path.join(RESULTS_DIR, 'benchmark_n100.csv')

    leaves = find_leaf_folders(KPLIB_ROOT)
    total  = len(leaves)
    n_algs = len(ALGORITHMS)

    print(f'{"="*65}')
    print(f'  Knapsack Benchmark — n <= {MAX_N}')
    print(f'  {total} leaf folders x up to {INSTANCES_PER_LEAF} instances x {n_algs} algorithms')
    print(f'  BruteForce skips n > {BF_MAX_N}  |  all other algos: no skips')
    print(f'{"="*65}\n')

    total_rows    = 0
    skipped_bf    = 0
    wall_start    = time.perf_counter()

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

                alg_results = {}
                for alg_name, run_fn, should_skip in ALGORITHMS:
                    row = dict(
                        category=cat, n_label=n_lbl, ratio=ratio,
                        instance=inst, n=n, capacity=capacity,
                        algorithm=alg_name,
                    )
                    if should_skip(n, capacity):
                        row.update(runtime_ms=None, result=None, skipped=True)
                        skipped_bf += 1
                        print(f'           {alg_name:<16} SKIP (n>{BF_MAX_N})', flush=True)
                    else:
                        try:
                            t0  = time.perf_counter()
                            res = run_fn(n, capacity, values, weights)
                            ms  = (time.perf_counter() - t0) * 1000
                            row.update(runtime_ms=round(ms, 4), result=res, skipped=False)
                            alg_results[alg_name] = res
                            print(f'           {alg_name:<16} {ms:8.2f} ms   result={res}', flush=True)
                        except Exception as exc:
                            row.update(runtime_ms=None, result=None, skipped=True)
                            print(f'           {alg_name:<16} ERROR: {exc}', flush=True)

                    writer.writerow(row)
                    total_rows += 1

                # Exact consistency check
                exact = {k: v for k, v in alg_results.items()
                         if k in ('BruteForce', 'Memoization', 'Tabulation')}
                if len(set(exact.values())) > 1:
                    print(f'           [MISMATCH] {exact}', flush=True)

                # Approximation bounds
                if exact:
                    opt = next(iter(exact.values()))
                    for approx, floor_pct in [('Greedy', 0.5), ('FPTAS', 1-FPTAS_EPSILON)]:
                        if approx in alg_results:
                            val = alg_results[approx]
                            if val > opt:
                                print(f'           [WARN] {approx}={val} exceeds OPT={opt}', flush=True)
                            elif val < floor_pct * opt - 1:
                                print(f'           [WARN] {approx}={val} violates {floor_pct:.0%} guarantee (OPT={opt})', flush=True)

    elapsed = time.perf_counter() - wall_start
    print(f'\n{"="*65}')
    print(f'  Done in {elapsed:.1f}s   {total_rows} rows written')
    print(f'  BruteForce skipped: {skipped_bf} (n > {BF_MAX_N})')
    print(f'  Results: {csv_path}')
    print(f'{"="*65}')
    return csv_path


if __name__ == '__main__':
    run()
