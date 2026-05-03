#!/usr/bin/env python3
"""Final verification test for 0/1 Knapsack Project"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.algorithms.brute_force import knapsack_brute_force
from src.algorithms.memoization import knapsack_memoization
from src.algorithms.tabulation import knapsack_tabulation
from src.algorithms.space_optimised import knapsack_space_optimised
from src.algorithms.greedy import knapsack_greedy
from src.parse_kp import parse_kp

print('='*80)
print('FINAL VERIFICATION TEST - ALL SYSTEMS CHECK')
print('='*80)

# Test 1: Baseline
print('\n1. BASELINE TEST (from documentation)')
values = [60, 100, 120, 80]
weights = [10, 20, 30, 25]
capacity = 50
n = 4

bf = knapsack_brute_force(capacity, n, values, weights)
memo = [[None]*(capacity+1) for _ in range(n+1)]
m = knapsack_memoization(capacity, n, values, weights, memo)
tab, items = knapsack_tabulation(capacity, values, weights)
so = knapsack_space_optimised(values, weights, n, capacity)
g = knapsack_greedy(capacity, values, weights)

print(f'  Brute Force:       {bf:3d} (expected: 220) - {"PASS" if bf==220 else "FAIL"}')
print(f'  Memoization:       {m:3d} (expected: 220) - {"PASS" if m==220 else "FAIL"}')
print(f'  Tabulation:        {tab:3d} (expected: 220) - {"PASS" if tab==220 else "FAIL"}')
print(f'  Space-Optimised:   {so:3d} (expected: 220) - {"PASS" if so==220 else "FAIL"}')
print(f'  Greedy Approx:     {g:3d} (expected: 160) - {"PASS" if g==160 else "FAIL"}')

# Test 2: kplib with FIXED parser
print('\n2. KPLIB PARSER TEST (Fixed)')
n2, cap2, vals2, wts2 = parse_kp('testcases/kplib/00Uncorrelated/n00050/R01000/s000.kp')
print(f'  Loaded: n={n2}, capacity={cap2}')
print(f'  Item 0: value={vals2[0]}, weight={wts2[0]} (should be 845, 804)')
parser_ok = vals2[0]==845 and wts2[0]==804
print(f'  Parser status: {"FIXED - CORRECT" if parser_ok else "ERROR"}')

# Test 3: Run a kplib instance
print('\n3. RUNNING ALGORITHM ON KPLIB DATA')
result = knapsack_tabulation(cap2, vals2, wts2)
print(f'  Tabulation on kplib instance: value={result[0]}')
print(f'  Items selected: {len(result[1])} items')

print('\n' + '='*80)
all_pass = (bf==220 and m==220 and tab==220 and so==220 and g==160 and parser_ok)
if all_pass:
    print('ALL TESTS PASSED - PROJECT IS FULLY FUNCTIONAL!')
else:
    print('SOME TESTS FAILED')
print('='*80)
