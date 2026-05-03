#!/usr/bin/env python3
"""Force brute force testing on small n=50 instance to verify correctness"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.getcwd(), 'src'))

from algorithms.brute_force import knapsack_brute_force
from algorithms.space_optimised import knapsack_space_optimised
from parse_kp import parse_kp

# Test brute force on ONE small n=50 instance
test_file = "testcases/kplib/00Uncorrelated/n00050/R01000/s000.kp"

print("="*80)
print("FORCING BRUTE FORCE TEST - Verifying Correctness")
print("="*80)

n, capacity, values, weights = parse_kp(test_file)

print(f"\nTest File: {test_file}")
print(f"Problem Size: n={n}, capacity={capacity}")
print(f"Operations: 2^{n} = {2**n:,}")

# Run Space-Optimised first (fast reference)
print(f"\n[1] Running Space-Optimised DP (reference)...")
start = time.time()
so_result = knapsack_space_optimised(values, weights, n, capacity)
so_time = (time.time() - start) * 1000
print(f"    Result: {so_result}")
print(f"    Time: {so_time:.2f}ms")

# Force Brute Force
print(f"\n[2] Running Brute Force (forced on n={n})...")
print(f"    WARNING: 2^{n} = {2**n:,} recursive calls")
print(f"    This may take a while... patience!\n")

start = time.time()
bf_result = knapsack_brute_force(capacity, n, values, weights)
bf_time = (time.time() - start) * 1000
print(f"    Result: {bf_result}")
print(f"    Time: {bf_time:.2f}ms")

# Verify consistency
print(f"\n[3] Verification:")
if bf_result == so_result:
    print(f"    ✓ BRUTE FORCE MATCHES SPACE-OPTIMISED!")
    print(f"    ✓ Both algorithms return: {bf_result}")
    print(f"    ✓ Brute Force is working correctly!")
else:
    print(f"    ✗ MISMATCH! BF={bf_result}, SO={so_result}")

print(f"\nPerformance:")
print(f"    Brute Force: {bf_time:.2f}ms (exact but slow)")
print(f"    Space-Opt:   {so_time:.2f}ms (optimized)")
print(f"    Ratio:       {bf_time/so_time:.1f}x slower")

print("\n" + "="*80)
print("✓ BRUTE FORCE VERIFICATION COMPLETE")
print("="*80)
