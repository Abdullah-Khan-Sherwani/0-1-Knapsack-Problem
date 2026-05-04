# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Course Requirements (CSE 317, Spring 2026)

Group project (4–5 members) worth 10% of grade. Report due **15 May 2026**.

Report must cover: (1) Introduction with formal problem formulation, (2) Algorithm descriptions, (3) Theoretical complexity (best/avg/worst), (4) Implementation details — machine spec, language, test case strategy, (5) Results & Discussion — runtime graphs/tables, theoretical vs. empirical comparison, strengths/weaknesses, (6) Conclusion, (7) References.

## Grading Criteria

We will be judged on:
- **Edge cases** — what inputs break or stress each algorithm, and why
- **Best/average/worst case analysis** — per algorithm, with justification tied to the instance structure (n, W, correlation type)
- **Why** these cases are best/worst — not just stating complexity but explaining what property of the input causes it
- **General algorithmic understanding** — trade-offs between exact vs approximate, time vs space, pseudo-polynomial vs polynomial

## Project

0/1 Knapsack Problem — empirical comparison of **6 algorithms**: Brute Force · Memoization · Tabulation · Space-Optimised DP · Greedy Approximation · FPTAS. Python 3, stdlib only (`time`, `sys`, `os`). Baseline instance: `values=[60,100,120,80]`, `weights=[10,20,30,25]`, `capacity=50`, optimal=220. Greedy returns 160 on this instance (27.3% gap), demonstrating it is not exact.

## Commands

```bash
python src/benchmark.py             # full benchmark (all n, both ratios, 1 instance/leaf)
python src/benchmark_r01000.py      # R01000 only, n=50–200, 5 instances/leaf, zero skips
python src/benchmark_n100.py        # n<=100 only, both ratios, 5 instances/leaf, BF skip only
python src/analyze.py               # detailed analysis of benchmark_results.csv
python generate_and_verify.py       # generate synthetic instances + verify category properties
python generate_synthetic.py        # regenerate 13Synthetic (n=5–25, BF-compatible)
python testing/test_all_algorithms.py  # unit tests for all 6 algorithms
cd docs && pdflatex report.tex && pdflatex report.tex   # build PDF (twice for TOC)
```

## Architecture

`src/algorithms/` — one file per algorithm, each independently runnable.
`src/benchmark.py` — full benchmark across all kplib instances, saves to `results/benchmark_results.csv`.
`src/benchmark_r01000.py` — R01000-only, n=50–200, no skips except BruteForce, saves to `results/benchmark_r01000.csv`.
`src/benchmark_n100.py` — n≤100 only, both ratios, no skips except BruteForce, saves to `results/benchmark_n100.csv`.
`src/analyze.py` — reads any benchmark CSV and prints detailed analysis split by ratio, category, n.
`src/plot.py` — generates 7 plots from benchmark CSV into `results/plots/`.
`docs/report.tex` — LaTeX report (PDF is gitignored).

## Testcases

`testcases/kplib/` — Pisinger benchmark instances. Structure: `{category}/n{n:05d}/{ratio}/{instance}.kp`

**kplib categories (06 excluded — W too large for DP):**
- `00Uncorrelated` through `05SubsetSum` — standard types, formulas well-verified
- `07–09 Spanner` variants — spanner-based generation, partial verification only
- `10MultipleStronglyCorrelated`, `11ProfitCeiling`, `12Circle` — formula-verified
- `13Synthetic` — simple random instances (n=5–25, R01000 only, BruteForce-compatible)

**Available n values:** 5, 8, 10, 12, 15, 18, 20, 22, 25 (synthetic), 30, 40, 45, 60, 75, 90 (generated), 50, 100, 200, 500 (original kplib)

**Available ratios:** R01000 (R=1000), R10000 (R=10000). R is the weight/value range; capacity = floor(sum(weights)/2).

**Instances per leaf:** original kplib has 100 files per leaf; generated synthetic has 10; 13Synthetic has 3.

**Instance generators:**
- `generate_synthetic.py` — regenerates `13Synthetic` (simple random, small n)
- `generate_and_verify.py` — generates kplib-style instances at intermediate n values (30,40,45,60,75,90) for both ratios, verifies category properties match definitions

## Function signatures — intentionally non-uniform (match their reference sources)

| File | Signature | Returns |
|---|---|---|
| `brute_force.py` | `knapsack_brute_force(capacity, n, values, weights)` | `int` |
| `memoization.py` | `knapsack_memoization(capacity, n, values, weights, memo)` | `int` |
| `tabulation.py` | `knapsack_tabulation(capacity, values, weights)` | `(int, list)` |
| `space_optimised.py` | `knapsack_space_optimised(values, weights, n, W)` | `int` |
| `greedy.py` | `knapsack_greedy(capacity, values, weights)` | `int` |
| `fptas.py` | `knapsack_fptas(capacity, values, weights, epsilon)` | `int` |

Critical gotchas:
- `memoization`: caller must pre-allocate `memo = [[None]*(capacity+1) for _ in range(n+1)]` and pass it in.
- `tabulation`: returns `(max_value, items_0indexed_list)` — the only function that returns a tuple.
- `space_optimised`: parameter is named `W` (not `capacity`); argument order differs from all others.
- `fptas`: returns approximate value (int), not the actual optimal. Uses 1D profit-indexed DP.
- `greedy`: implements wiki S2 — takes max(greedy_pack, best_single_item), guarantees ≥ OPT/2.

## Skip thresholds (benchmark.py)

| Algorithm | Skip condition | Reason |
|---|---|---|
| BruteForce | n > 25 | 2^n too large |
| Memoization | n×W > 15M | memo table OOM |
| Tabulation | n×W > 30M | dp table OOM |
| SpaceOptimised | W > 2M | O(W) array too large |
| Greedy | never | O(n log n), W-immune |
| FPTAS | n²/ε > 4M | scaled DP too slow |

`benchmark_r01000.py` and `benchmark_n100.py` remove all skip conditions except BruteForce (n>25).
