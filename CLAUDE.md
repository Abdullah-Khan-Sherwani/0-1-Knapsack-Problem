# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Course Requirements (CSE 317, Spring 2026)

Group project (4–5 members) worth 10% of grade. Report due **15 May 2026**.

Report must cover: (1) Introduction with formal problem formulation, (2) Algorithm descriptions, (3) Theoretical complexity (best/avg/worst), (4) Implementation details — machine spec, language, test case strategy, (5) Results & Discussion — runtime graphs/tables, theoretical vs. empirical comparison, strengths/weaknesses, (6) Conclusion, (7) References.

## Project

0/1 Knapsack Problem — empirical comparison of **5 algorithms**: Brute Force · Memoization · Tabulation · Space-Optimised DP · Greedy Approximation. Python 3, stdlib only (`time`, `sys`, `os`). Baseline instance: `values=[60,100,120,80]`, `weights=[10,20,30,25]`, `capacity=50`, optimal=220. Greedy returns 160 on this instance (27.3% gap), demonstrating it is not exact.

## Commands

```bash
python src/main.py          # run and time all 5 algorithms
cd docs && pdflatex report.tex && pdflatex report.tex   # build PDF (twice for TOC)
```

Each algorithm file is also independently runnable: `python src/algorithms/<name>.py`.

## Architecture

`src/algorithms/` — one file per algorithm, each independently runnable. `src/main.py` — unified runner that imports all five and times them. `docs/report.tex` — LaTeX report (PDF is gitignored). `testcases/kplib/` — Pisinger benchmark instances (clone of github.com/likr/kplib; currently incomplete).

### Function signatures — intentionally non-uniform (match their reference sources)

| File | Signature | Returns |
|---|---|---|
| `brute_force.py` | `knapsack_brute_force(capacity, n, values, weights)` | `int` |
| `memoization.py` | `knapsack_memoization(capacity, n, values, weights, memo)` | `int` |
| `tabulation.py` | `knapsack_tabulation(capacity, values, weights)` | `(int, list)` |
| `space_optimised.py` | `knapsack_space_optimised(values, weights, n, W)` | `int` |
| `greedy.py` | `knapsack_greedy(capacity, values, weights)` | `int` |

Critical gotchas:
- `memoization`: caller must pre-allocate `memo = [[None]*(capacity+1) for _ in range(n+1)]` and pass it in.
- `tabulation`: returns `(max_value, items_0indexed_list)` — the only function that returns a tuple.
- `space_optimised`: parameter is named `W` (not `capacity`); argument order differs from all others.
- `tabulation` item list is **0-indexed**; report displays them as such.

### Report placeholders

`docs/report.tex` has placeholder rows in the kplib benchmark tables (Section 5) that need real measured runtimes once benchmarks are run against kplib instances.
