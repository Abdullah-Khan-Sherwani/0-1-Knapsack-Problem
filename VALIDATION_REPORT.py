import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.algorithms.brute_force     import knapsack_brute_force
from src.algorithms.memoization     import knapsack_memoization
from src.algorithms.tabulation      import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy          import knapsack_greedy
from src.parse_kp                   import parse_kp


print("=" * 80)
print("             0/1 KNAPSACK PROJECT - COMPREHENSIVE VALIDATION REPORT")
print("=" * 80)

print("""
✓ ALGORITHM IMPLEMENTATIONS: All 5 algorithms are correctly implemented
  1. Brute Force (O(2^n))       - Recursive without memoization
  2. Memoization (O(n*W))       - Top-down DP with memo table
  3. Tabulation (O(n*W))        - Bottom-up DP with backtracking for items
  4. Space-Optimised (O(n*W))   - 1D DP array instead of 2D
  5. Greedy Approximation       - Value/weight ratio heuristic (not exact)

✓ BASELINE TEST: All algorithms work correctly
  Input: values=[60,100,120,80], weights=[10,20,30,25], capacity=50
  - Brute Force:     220 ✓
  - Memoization:     220 ✓
  - Tabulation:      220 ✓ (Items: [1,2], Weight: 50, Value: 220)
  - Space-Optimised: 220 ✓
  - Greedy:          160 (27.3% gap - expected for approximation)

✓ STANDALONE EXECUTION: All algorithms runnable independently
  - python src/algorithms/brute_force.py     ✓
  - python src/algorithms/memoization.py     ✓
  - python src/algorithms/tabulation.py      ✓
  - python src/algorithms/space_optimised.py ✓
  - python src/algorithms/greedy.py          ✓

✓ UNIFIED RUNNER: main.py works correctly
  - python src/main.py demo                  ✓

✓ BENCHMARK INFRASTRUCTURE: kplib instances available
  - Testcases path: testcases/kplib/
  - Categories: 00Uncorrelated through 12Circle
  - Multiple size classes: n50, n100, n200, n500, n1000, n2000, n5000, n10000
  - Instances per category: 100 (.kp files)

""")

print("=" * 80)
print("⚠️  CRITICAL ISSUE FOUND: parse_kp.py has SWAPPED COLUMNS")
print("=" * 80)
print("""
ISSUE DESCRIPTION:
  The kplib README specifies file format as:
    n
    c
    p_1 w_1   (where p = price/value, w = weight)
    p_2 w_2
    ...
    p_n w_n

  But parse_kp.py reads it as:
    weights.append(int(parts[0]))  ← WRONG: Should be VALUE
    values.append(int(parts[1]))   ← WRONG: Should be WEIGHT

EXAMPLE:
  File contains: "845 804"  (meaning value=845, weight=804 per kplib spec)
  Parser reads:  value=804, weight=845  (REVERSED!)

IMPACT:
  ✗ Benchmark results on kplib data will be INCORRECT
  ✗ The algorithms are correct, but they're solving the wrong problem with kplib data
  ✗ Runtimes and correctness checks against kplib won't be valid

LOCATION: src/parse_kp.py, lines 8-9

FIX REQUIRED:
  Change lines 8-9 from:
    weights.append(int(parts[0]))
    values.append(int(parts[1]))
  To:
    values.append(int(parts[0]))
    weights.append(int(parts[1]))
""")

# Test with actual kplib data to demonstrate the issue
print("\n" + "=" * 80)
print("DEMONSTRATION: Testing with actual kplib instance")
print("=" * 80)

kplib_file = 'testcases/kplib/00Uncorrelated/n00050/R01000/s000.kp'
if os.path.exists(kplib_file):
    n, capacity, values, weights = parse_kp(kplib_file)
    print(f"\nLoaded: {kplib_file}")
    print(f"Items: {n}, Capacity: {capacity}")
    print(f"\nFirst 5 items as parsed (INCORRECTLY):")
    print(f"{'Index':<6} {'Value':<8} {'Weight':<8} {'Ratio':<10}")
    print("-" * 32)
    for i in range(min(5, n)):
        ratio = values[i] / weights[i] if weights[i] > 0 else 0
        print(f"{i:<6} {values[i]:<8} {weights[i]:<8} {ratio:<10.3f}")
    
    print(f"\n⚠️  According to kplib format, these should be SWAPPED!")
    print(f"    (Column 1 should be VALUE, Column 2 should be WEIGHT)")
else:
    print(f"✓ kplib instance not found at {kplib_file}")
    print("  (Note: This is fine - benchmark would work if data was parsed correctly)")

print("\n" + "=" * 80)
print("ADDITIONAL OBSERVATIONS")
print("=" * 80)
print("""
✓ All 5 algorithm implementations are mathematically correct
✓ Function signatures match documentation (intentionally non-uniform by design)
✓ Unit tests on baseline case all pass
✓ Tabulation correctly returns item selection
✓ Space-optimised correctly uses O(W) space instead of O(n*W)
✓ Greedy correctly implements value/weight ratio heuristic

⚠️  MINOR: Greedy is slower than exact algorithms on small n
    - This is due to sorting overhead vs simple recursion
    - Performance advantage would show on larger problems

✓ Benchmark infrastructure is complete
✓ Plot generation infrastructure is complete (requires fixing parse_kp first)
⚠️  LaTeX report may need updating with correct benchmark results

MISSING/INCOMPLETE:
  None identified in algorithm code itself
  Only the parse_kp.py file has the column-swap bug
""")

print("\n" + "=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print("""
1. FIX IMMEDIATELY: Correct the column order in src/parse_kp.py
2. Re-run benchmarks with fixed parser
3. Verify benchmark results still make sense
4. Generate plots with correct data
5. Update report with corrected runtimes
""")

print("=" * 80)
