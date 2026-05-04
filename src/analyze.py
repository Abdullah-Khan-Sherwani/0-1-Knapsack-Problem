import os, sys
import pandas as pd
import numpy as np

_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV     = os.path.join(_ROOT, 'results', 'benchmark_results.csv')

BF_MAX_N      = 25
MEMO_MAX_NW   = 15_000_000
TAB_MAX_NW    = 30_000_000
SPOPT_MAX_W   = 2_000_000
FPTAS_MAX_N2  = 4_000_000
FPTAS_EPSILON = 0.25

ALG_ORDER = ['BruteForce','Memoization','Tabulation','SpaceOptimised','Greedy','FPTAS']
RATIOS    = ['R01000', 'R10000']


def skip_reason(alg, n, W):
    if alg == 'BruteForce'     and n > BF_MAX_N:
        return f'n={n} > BF_MAX_N={BF_MAX_N}  ->  2^n too large'
    if alg == 'Memoization'    and n * W > MEMO_MAX_NW:
        return f'n*W={n*W:,} > {MEMO_MAX_NW:,}  ->  memo table OOM'
    if alg == 'Tabulation'     and n * W > TAB_MAX_NW:
        return f'n*W={n*W:,} > {TAB_MAX_NW:,}  ->  dp table OOM'
    if alg == 'SpaceOptimised' and W > SPOPT_MAX_W:
        return f'W={W:,} > {SPOPT_MAX_W:,}  ->  O(W) array too large'
    if alg == 'FPTAS'          and (n*n / FPTAS_EPSILON) > FPTAS_MAX_N2:
        return f'n^2/eps={n*n/FPTAS_EPSILON:,.0f} > {FPTAS_MAX_N2:,}  ->  scaled DP too slow'
    return 'exception during run'


def sep(title='', w=76):
    if title:
        print(f'\n{"─"*w}')
        print(f'  {title}')
        print(f'{"─"*w}')
    else:
        print(f'{"="*w}')


def load():
    df = pd.read_csv(CSV)
    df['skipped']    = df['skipped'].astype(str) == 'True'
    df['runtime_ms'] = pd.to_numeric(df['runtime_ms'], errors='coerce')
    df['result']     = pd.to_numeric(df['result'],     errors='coerce')
    df['n']          = pd.to_numeric(df['n'],          errors='coerce').astype(int)
    df['capacity']   = pd.to_numeric(df['capacity'],   errors='coerce').astype(int)
    return df


# ── Section 1: Dataset overview ───────────────────────────────────────────────

def section_overview(df):
    sep('1. DATASET OVERVIEW')
    total   = len(df)
    ran     = df[~df['skipped']]
    skipped = df[df['skipped']]
    print(f'  Total rows      : {total}')
    print(f'  Executed        : {len(ran)}  ({len(ran)/total*100:.1f}%)')
    print(f'  Skipped         : {len(skipped)}  ({len(skipped)/total*100:.1f}%)')
    print(f'  Categories      : {sorted(df["category"].unique())}')
    print(f'  n values        : {sorted(df["n"].unique())}')
    print(f'  Capacity ratios : {sorted(df["ratio"].unique())}')
    print(f'  Algorithms      : {ALG_ORDER}')

    print()
    print(f'  Executed rows per algorithm x ratio:')
    pivot = (ran.groupby(['algorithm','ratio']).size()
               .unstack(fill_value=0)
               .reindex(ALG_ORDER))
    print(f'  {"Algorithm":<16}', end='')
    for r in RATIOS:
        print(f'  {r:>10}', end='')
    print(f'  {"Total":>8}')
    print(f'  {"─"*50}')
    for alg in ALG_ORDER:
        if alg not in pivot.index:
            continue
        row = pivot.loc[alg]
        print(f'  {alg:<16}', end='')
        for r in RATIOS:
            print(f'  {row.get(r,0):>10}', end='')
        print(f'  {row.sum():>8}')


# ── Section 2: Skip analysis ──────────────────────────────────────────────────

def section_skips(df):
    sep('2. SKIP ANALYSIS — WHY EACH ALGORITHM WAS SKIPPED')

    for alg in ALG_ORDER:
        sub = df[(df['algorithm'] == alg) & df['skipped']]
        ran = df[(df['algorithm'] == alg) & ~df['skipped']]
        print(f'\n  {alg}   skipped={len(sub)}  ran={len(ran)}')
        if sub.empty:
            print('    -> Never skipped')
            continue

        # Unique skip reasons
        shown = set()
        for _, row in sub.groupby(['n','capacity']).size().reset_index().iterrows():
            r = skip_reason(alg, int(row['n']), int(row['capacity']))
            key = r[:60]
            if key not in shown:
                print(f'    -> {r}')
                shown.add(key)

        # Which (n, ratio) combos always skip — shown per ratio
        always = (df[df['algorithm'] == alg]
                    .groupby(['n','ratio'])['skipped']
                    .all()
                    .reset_index(name='all_skip'))
        for ratio in RATIOS:
            cases = always[(always['all_skip']) & (always['ratio']==ratio)]['n'].tolist()
            if cases:
                print(f'    Always skipped [{ratio}]: n = {cases}')


# ── Section 3: Runtime summary per algorithm x ratio ─────────────────────────

def section_runtime_by_algo(df):
    sep('3. RUNTIME SUMMARY PER ALGORITHM x RATIO (ms)')
    ran = df[~df['skipped']]

    for ratio in RATIOS:
        print(f'\n  [{ratio}]')
        print(f'  {"Algorithm":<16} {"Count":>6} {"Min":>10} {"Median":>10} {"Mean":>10} {"Max":>12}')
        print(f'  {"─"*68}')
        sub = ran[ran['ratio'] == ratio]
        for alg in ALG_ORDER:
            s = sub[sub['algorithm'] == alg]['runtime_ms'].dropna()
            if s.empty:
                print(f'  {alg:<16} {"no data":>6}')
                continue
            print(f'  {alg:<16} {len(s):>6} {s.min():>10.3f} {s.median():>10.3f} '
                  f'{s.mean():>10.3f} {s.max():>12.3f}')

    # BruteForce only has synthetic (R01000 only) — note it
    print(f'\n  Note: BruteForce only ran on 13Synthetic instances (n=5-25, R01000 only).')


# ── Section 4: Median runtime by n x ratio — one table per algorithm ─────────

def section_runtime_vs_n(df):
    sep('4. MEDIAN RUNTIME (ms) BY n x RATIO — PER ALGORITHM')
    ran = df[~df['skipped']]
    ns  = sorted(ran['n'].unique())

    for alg in ALG_ORDER:
        sub = ran[ran['algorithm'] == alg]
        if sub.empty:
            continue
        print(f'\n  {alg}')
        print(f'  {"n":>6}  {"R01000 (ms)":>14}  {"R10000 (ms)":>14}  {"Slowdown":>10}')
        print(f'  {"─"*52}')
        for n in ns:
            r1 = sub[(sub['n']==n) & (sub['ratio']=='R01000')]['runtime_ms'].median()
            r2 = sub[(sub['n']==n) & (sub['ratio']=='R10000')]['runtime_ms'].median()
            has_r1 = not pd.isna(r1)
            has_r2 = not pd.isna(r2)
            if not has_r1 and not has_r2:
                continue  # no data at this n for this alg
            r1s = f'{r1:>14.3f}' if has_r1 else f'{"SKIP":>14}'
            r2s = f'{r2:>14.3f}' if has_r2 else f'{"SKIP":>14}'
            if has_r1 and has_r2:
                factor = f'{r2/r1:>10.1f}x'
            elif not has_r1 and not has_r2:
                factor = f'{"—":>10}'
            else:
                factor = f'{"n/a":>10}'
            print(f'  {n:>6}  {r1s}  {r2s}  {factor}')


# ── Section 5: Runtime by category x ratio (SpaceOptimised) ──────────────────

def section_category_ratio(df):
    sep('5. RUNTIME BY CATEGORY x RATIO — SpaceOptimised (ms)')
    ran = df[(~df['skipped']) & (df['algorithm'] == 'SpaceOptimised')]

    for ratio in RATIOS:
        print(f'\n  [{ratio}]')
        sub = ran[ran['ratio'] == ratio]
        if sub.empty:
            print('  No data.')
            continue
        g = (sub.groupby(['category','n'])['runtime_ms']
                .median().unstack('n'))
        ns = sorted(g.columns)
        print(f'  {"Category":<40}', end='')
        for n in ns:
            print(f'  {f"n={n}":>9}', end='')
        print()
        print(f'  {"─"*( 40 + 11*len(ns) )}')
        for cat, row in g.iterrows():
            print(f'  {cat:<40}', end='')
            for n in ns:
                val = row.get(n, float('nan'))
                print(f'  {"SKIP" if pd.isna(val) else f"{val:.1f}":>9}', end='')
            print()


# ── Section 6: R10000 vs R01000 slowdown — all algorithms ────────────────────

def section_ratio_impact(df):
    sep('6. R10000 vs R01000 SLOWDOWN — ALL ALGORITHMS')
    ran = df[~df['skipped']]
    print(f'  {"Algorithm":<16} {"n":>6}  {"R01000 (ms)":>13}  {"R10000 (ms)":>13}  {"Slowdown":>10}')
    print(f'  {"─"*66}')

    for alg in ALG_ORDER:
        sub = ran[ran['algorithm'] == alg]
        ns  = sorted(sub['n'].unique())
        printed_any = False
        for n in ns:
            r1 = sub[(sub['n']==n) & (sub['ratio']=='R01000')]['runtime_ms'].median()
            r2 = sub[(sub['n']==n) & (sub['ratio']=='R10000')]['runtime_ms'].median()
            if pd.isna(r1) and pd.isna(r2):
                continue
            r1s = f'{r1:>13.3f}' if not pd.isna(r1) else f'{"SKIP":>13}'
            r2s = f'{r2:>13.3f}' if not pd.isna(r2) else f'{"SKIP":>13}'
            if not pd.isna(r1) and not pd.isna(r2):
                factor = f'{r2/r1:>10.2f}x'
            else:
                factor = f'{"—":>10}'
            print(f'  {alg:<16} {n:>6}  {r1s}  {r2s}  {factor}')
            printed_any = True
        if printed_any:
            print()


# ── Section 7: Approximation quality x ratio ─────────────────────────────────

def section_approx_quality(df):
    sep('7. APPROXIMATION QUALITY — GREEDY & FPTAS vs OPTIMAL (by ratio)')
    ran = df[~df['skipped']]

    exact_algs = ['BruteForce','Memoization','Tabulation','SpaceOptimised']
    key = ['category','n_label','ratio','instance']

    optimal = (ran[ran['algorithm'].isin(exact_algs)]
                  .groupby(key)['result'].max()
                  .reset_index().rename(columns={'result':'optimal'}))

    for approx_alg in ['Greedy', 'FPTAS']:
        floor = 50.0 if approx_alg == 'Greedy' else (1 - FPTAS_EPSILON) * 100
        sub   = (ran[ran['algorithm'] == approx_alg][key + ['result','n']]
                    .rename(columns={'result':'approx'}))
        merged = sub.merge(optimal, on=key)
        merged = merged[merged['optimal'] > 0].copy()
        merged['ratio_pct'] = merged['approx'] / merged['optimal'] * 100

        print(f'\n  {approx_alg}  (guarantee floor: {floor:.0f}%)')

        for ratio in RATIOS:
            m = merged[merged['ratio'] == ratio]
            if m.empty:
                continue
            print(f'\n    [{ratio}]')
            print(f'    {"Category":<35} {"N":>5} {"Min%":>8} {"Med%":>8} {"Mean%":>8} {"Viols":>7}')
            print(f'    {"─"*75}')
            for cat in sorted(m['category'].unique()):
                c = m[m['category'] == cat]['ratio_pct']
                viols = (c < floor - 0.1).sum()
                print(f'    {cat:<35} {len(c):>5} {c.min():>8.2f} {c.median():>8.2f} '
                      f'{c.mean():>8.2f} {viols:>7}')
            overall = m['ratio_pct']
            viols   = (overall < floor - 0.1).sum()
            print(f'    {"OVERALL":<35} {len(overall):>5} {overall.min():>8.2f} '
                  f'{overall.median():>8.2f} {overall.mean():>8.2f} {viols:>7}')


# ── Section 8: Approximation quality by n ────────────────────────────────────

def section_approx_vs_n(df):
    sep('8. APPROXIMATION QUALITY BY n — GREEDY & FPTAS')
    ran = df[~df['skipped']]
    exact_algs = ['BruteForce','Memoization','Tabulation','SpaceOptimised']
    key = ['category','n_label','ratio','instance','n']

    optimal = (ran[ran['algorithm'].isin(exact_algs)]
                  .groupby(key)['result'].max()
                  .reset_index().rename(columns={'result':'optimal'}))

    for approx_alg in ['Greedy', 'FPTAS']:
        floor = 50.0 if approx_alg == 'Greedy' else (1 - FPTAS_EPSILON) * 100
        sub   = (ran[ran['algorithm'] == approx_alg][key + ['result']]
                    .rename(columns={'result':'approx'}))
        merged = sub.merge(optimal, on=key)
        merged = merged[merged['optimal'] > 0].copy()
        merged['ratio_pct'] = merged['approx'] / merged['optimal'] * 100

        print(f'\n  {approx_alg}  (guarantee floor: {floor:.0f}%)')
        print(f'  {"n":>6}  {"Ratio":>8}  {"Instances":>9}  {"Min%":>8}  {"Median%":>9}  {"Mean%":>8}  {"Viols":>7}')
        print(f'  {"─"*70}')
        for n in sorted(merged['n'].unique()):
            for ratio in RATIOS:
                m = merged[(merged['n']==n) & (merged['ratio']==ratio)]
                if m.empty:
                    continue
                c = m['ratio_pct']
                viols = (c < floor - 0.1).sum()
                print(f'  {n:>6}  {ratio:>8}  {len(c):>9}  {c.min():>8.2f}  '
                      f'{c.median():>9.2f}  {c.mean():>8.2f}  {viols:>7}')


# ── Section 9: Hardest instances per ratio ───────────────────────────────────

def section_hardest(df):
    sep('9. TOP 10 HARDEST INSTANCES PER RATIO (by SpaceOptimised runtime)')
    ran = df[(~df['skipped']) & (df['algorithm'] == 'SpaceOptimised')]

    for ratio in RATIOS:
        print(f'\n  [{ratio}]')
        sub = ran[ran['ratio'] == ratio]
        if sub.empty:
            print('  No data.')
            continue
        top = sub.nlargest(10, 'runtime_ms')[['category','n','capacity','runtime_ms']]
        print(f'  {"Category":<40} {"n":>5}  {"W":>12}  {"Runtime(ms)":>13}')
        print(f'  {"─"*76}')
        for _, r in top.iterrows():
            print(f'  {r["category"]:<40} {r["n"]:>5}  {r["capacity"]:>12,}  {r["runtime_ms"]:>13.1f}')


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(CSV):
        print(f'[ERROR] No CSV at {CSV} — run benchmark first.')
        sys.exit(1)

    df = load()
    sep()
    print('  KNAPSACK BENCHMARK — DETAILED ANALYSIS')
    print(f'  Source: {CSV}')
    sep()

    section_overview(df)
    section_skips(df)
    section_runtime_by_algo(df)
    section_runtime_vs_n(df)
    section_category_ratio(df)
    section_ratio_impact(df)
    section_approx_quality(df)
    section_approx_vs_n(df)
    section_hardest(df)

    sep()
    print('  END OF ANALYSIS')
    sep()


if __name__ == '__main__':
    main()
