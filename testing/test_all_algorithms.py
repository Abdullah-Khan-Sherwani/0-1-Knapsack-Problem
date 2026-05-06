import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.algorithms.fptas           import knapsack_fptas

FPTAS_EPSILON = 0.25  # guarantees >= 0.75 * OPT


def test_case(name, values, weights, capacity, expected_optimal):
    print(f"\n{'='*70}")
    print(f"TEST CASE: {name}")
    print(f"{'='*70}")
    print(f"Capacity: {capacity}  |  Values: {values}  |  Weights: {weights}")
    print(f"Expected Optimal: {expected_optimal}")
    print(f"{'-'*70}")

    n = len(values)
    results = {}
    failed = []

    # Brute Force
    bf, bf_items = knapsack_brute_force(capacity, n, values, weights)
    results['BruteForce'] = bf
    ok = bf == expected_optimal
    print(f"Brute Force         : {bf:<6}  items={sorted(bf_items)}  {'PASS' if ok else 'FAIL'}")
    if not ok: failed.append('BruteForce')

    # Memoization
    memo = [[None] * (capacity + 1) for _ in range(n + 1)]
    mem, mem_items = knapsack_memoization(capacity, n, values, weights, memo)
    results['Memoization'] = mem
    ok = mem == expected_optimal
    print(f"Memoization         : {mem:<6}  items={sorted(mem_items)}  {'PASS' if ok else 'FAIL'}")
    if not ok: failed.append('Memoization')

    # Tabulation
    tab, items = knapsack_tabulation(capacity, values, weights)
    results['Tabulation'] = tab
    ok = tab == expected_optimal
    print(f"Tabulation          : {tab:<6}  {'PASS' if ok else 'FAIL'}")
    print(f"  items={sorted(items)}  weight={sum(weights[i] for i in items)}/{capacity}")
    if not ok: failed.append('Tabulation')

    # Space-Optimised
    sp = knapsack_space_optimised(values, weights, n, capacity)
    results['SpaceOpt'] = sp
    ok = sp == expected_optimal
    print(f"Space-Optimised     : {sp:<6}  {'PASS' if ok else 'FAIL'}")
    if not ok: failed.append('SpaceOpt')

    # Greedy — check OPT/2 guarantee
    gr, gr_items = knapsack_greedy(capacity, values, weights)
    results['Greedy'] = gr
    gap = ((expected_optimal - gr) / expected_optimal * 100) if expected_optimal > 0 else 0
    opt2_ok = gr >= expected_optimal / 2
    print(f"Greedy (wiki S2)    : {gr:<6}  items={gr_items}  gap={gap:.1f}%  OPT/2 guarantee={'PASS' if opt2_ok else 'FAIL'}")
    if not opt2_ok: failed.append('Greedy-OPT/2')

    # FPTAS — check (1-eps)*OPT guarantee
    ft = knapsack_fptas(capacity, values, weights, epsilon=FPTAS_EPSILON)
    results['FPTAS'] = ft
    floor = (1 - FPTAS_EPSILON) * expected_optimal
    ft_ok = ft >= floor - 1  # allow 1-unit rounding slack
    print(f"FPTAS (eps={FPTAS_EPSILON})     : {ft:<6}  floor={floor:.0f}  guarantee={'PASS' if ft_ok else 'FAIL'}")
    if not ft_ok: failed.append('FPTAS-guarantee')

    # Exact algorithms must all agree
    exact = [results['BruteForce'], results['Memoization'],
             results['Tabulation'], results['SpaceOpt']]
    if len(set(exact)) == 1 and exact[0] == expected_optimal:
        print(f"Exact consistency   : PASS (all={expected_optimal})")
    elif len(set(exact)) == 1:
        print(f"Exact consistency   : WARN all agree={exact[0]} but expected={expected_optimal}")
    else:
        print(f"Exact consistency   : FAIL {dict(zip(['BF','Memo','Tab','SP'], exact))}")
        failed.append('consistency')

    if failed:
        print(f"\n  FAILED checks: {failed}")
    return len(failed) == 0


def main():
    print("=" * 70)
    print("       0/1 KNAPSACK — FULL ALGORITHM VALIDATION (6 algorithms)")
    print("=" * 70)

    all_passed = True

    # Standard correctness cases
    all_passed &= test_case(
        "Baseline (from CLAUDE.md)",
        values=[60, 100, 120, 80], weights=[10, 20, 30, 25],
        capacity=50, expected_optimal=220
    )
    all_passed &= test_case(
        "Simple 3-item",
        values=[10, 20, 30], weights=[5, 10, 15],
        capacity=20, expected_optimal=40  # items 0+2: weight=5+15=20, value=10+30=40
    )
    all_passed &= test_case(
        "Single item fits exactly",
        values=[100], weights=[50],
        capacity=50, expected_optimal=100
    )
    all_passed &= test_case(
        "Item exceeds capacity",
        values=[100, 50, 50], weights=[60, 20, 30],
        capacity=40, expected_optimal=50
    )
    all_passed &= test_case(
        "All items fit",
        values=[10, 20, 30], weights=[5, 10, 15],
        capacity=100, expected_optimal=60
    )
    all_passed &= test_case(
        "No items fit",
        values=[10, 20, 30], weights=[15, 20, 30],
        capacity=10, expected_optimal=0
    )

    # Greedy S2 (wiki) validation
    # Simple greedy (S1 only) returns 2 here; S2 greedy must return 1000.
    # item0 ratio=2.0 fits (w=1), item1 ratio~1.0 doesn't fit (w=999=capacity).
    # S1=2, S2=1000 -> max=1000 = OPT.
    all_passed &= test_case(
        "Greedy S2 wins over S1",
        values=[2, 1000], weights=[1, 999],
        capacity=999, expected_optimal=1000
    )
    # item0 best ratio fits -> S1=5; item1 doesn't fit but fits individually -> S2=10.
    # max(5,10)=10 = OPT. Without S2, simple greedy would return only 5.
    all_passed &= test_case(
        "Greedy S2 corrects ratio trap",
        values=[5, 10], weights=[3, 8],
        capacity=10, expected_optimal=10
    )
    # OPT/2 stress: greedy gets 50, OPT=50. Confirms no regression.
    all_passed &= test_case(
        "Greedy OPT/2 stress",
        values=[50, 48, 48], weights=[10, 9, 9],
        capacity=10, expected_optimal=50
    )

    print("\n" + "=" * 70)
    print("RESULT:", "ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED")
    print("=" * 70)


if __name__ == '__main__':
    main()
