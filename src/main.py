import time
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy


def run_demo():
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    n        = len(values)

    print("=" * 55)
    print("       0/1 KNAPSACK — ALL APPROACHES COMPARISON")
    print("=" * 55)
    print(f"Items    : {n}    Capacity: {capacity}")
    print(f"Values   : {values}")
    print(f"Weights  : {weights}")
    print("-" * 55)

    memo = [[None] * (capacity + 1) for _ in range(n + 1)]

    approaches = [
        ("Brute Force",     lambda: knapsack_brute_force(capacity, n, values, weights)),
        ("Memoization",     lambda: knapsack_memoization(capacity, n, values, weights, memo)),
        ("Tabulation",      lambda: knapsack_tabulation(capacity, values, weights)[0]),
        ("Space-Optimised", lambda: knapsack_space_optimised(values, weights, n, capacity)),
        ("Greedy Approx.",  lambda: knapsack_greedy(capacity, values, weights)),
    ]

    for name, func in approaches:
        start  = time.perf_counter()
        result = func()
        end    = time.perf_counter()
        print(f"{name:<20}: Max Value = {result}  | Time = {(end - start) * 1e6:.2f} µs")

    print("-" * 55)
    max_val, items = knapsack_tabulation(capacity, values, weights)
    print(f"Selected Items (0-indexed): {items}")
    print(f"Total Weight of Selection : {sum(weights[i] for i in items)}")
    print(f"Total Value  of Selection : {max_val}")
    print("=" * 55)


def main():
    cmd = sys.argv[1].lower() if len(sys.argv) > 1 else 'demo'

    if cmd not in ('demo', 'benchmark', 'plot', 'all'):
        print("Usage: python src/main.py [demo|benchmark|plot|all]")
        print("  demo      — run baseline demo instance (default)")
        print("  benchmark — run kplib benchmarks, save CSV")
        print("  plot      — generate plots from existing CSV")
        print("  all       — benchmark then plot")
        sys.exit(1)

    run_demo()

    if cmd in ('benchmark', 'all'):
        print()
        from src.benchmark import run_benchmarks
        csv_path = run_benchmarks()

        if cmd == 'all' and csv_path:
            print()
            from src.plot import generate_all_plots
            generate_all_plots(csv_path)

    elif cmd == 'plot':
        print()
        from src.plot import generate_all_plots
        generate_all_plots()


if __name__ == '__main__':
    main()
