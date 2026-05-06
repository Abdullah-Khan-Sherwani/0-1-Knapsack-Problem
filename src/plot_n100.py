"""Plot generator for the n<=100 benchmark.

Reads results/benchmark_n100.csv, aggregates by MEAN runtime per (n, algorithm),
and produces clean publication-quality figures used by the presentation deck.

Outputs (overwrites existing files in results/plots/):
- fig1_runtime_vs_n.png   — log-log mean runtime, all 5 algorithms, error bars = std
- fig4_approx_ratio.png   — boxplot of approx_value/optimum per instance category
"""
import os, sys
import numpy as np

_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(_ROOT, 'results')
PLOTS   = os.path.join(RESULTS, 'plots')
CSV     = os.path.join(RESULTS, 'benchmark_n100.csv')

ALG_COLORS = {
    'BruteForce':  '#e74c3c',
    'Memoization': '#3498db',
    'Tabulation':  '#2ecc71',
    'Greedy':      '#9b59b6',
    'FPTAS':       '#1abc9c',
}
ALG_ORDER = ['BruteForce', 'Memoization', 'Tabulation', 'Greedy', 'FPTAS']
ALG_MARKERS = {
    'BruteForce':  'o',
    'Memoization': 's',
    'Tabulation':  '^',
    'Greedy':      'D',
    'FPTAS':       'v',
}


def _save(fig, name):
    import matplotlib.pyplot as plt
    os.makedirs(PLOTS, exist_ok=True)
    path = os.path.join(PLOTS, name)
    fig.savefig(path, dpi=160, bbox_inches='tight', facecolor='white')
    plt.close(fig)
    print(f"  Saved: {path}")


def _load():
    import pandas as pd
    df = pd.read_csv(CSV)
    df = df[df['skipped'].astype(str) == 'False'].copy()
    df['runtime_ms'] = pd.to_numeric(df['runtime_ms'], errors='coerce')
    df['n']          = pd.to_numeric(df['n'], errors='coerce')
    df['result']     = pd.to_numeric(df['result'], errors='coerce')
    return df.dropna(subset=['runtime_ms', 'n'])


# ── Fig 1: Runtime vs n (MEAN, with error bars) ──────────────────────────────

def plot_runtime_vs_n(df):
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.family': 'DejaVu Sans'})

    fig, ax = plt.subplots(figsize=(11, 6.5))
    for alg in ALG_ORDER:
        sub = df[df['algorithm'] == alg]
        if sub.empty:
            continue
        g = sub.groupby('n')['runtime_ms'].agg(['mean', 'std', 'count']).reset_index()
        # std can be nan when count==1 — coerce to 0
        g['std'] = g['std'].fillna(0)
        ax.errorbar(
            g['n'], g['mean'], yerr=g['std'],
            marker=ALG_MARKERS[alg], color=ALG_COLORS[alg],
            label=alg, linewidth=2.2, markersize=7,
            capsize=3, elinewidth=1, alpha=0.95,
        )

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Number of Items (n)', fontsize=13)
    ax.set_ylabel('Mean Runtime (ms, log scale)', fontsize=13)
    ax.set_title('0/1 Knapsack — Mean Runtime vs Problem Size  (n ≤ 100)',
                 fontsize=15, fontweight='bold', pad=12)

    # x ticks at actual n values that exist
    n_vals = sorted(df['n'].unique())
    ax.set_xticks(n_vals)
    ax.set_xticklabels([str(int(n)) for n in n_vals], fontsize=10)
    ax.tick_params(axis='y', labelsize=10)

    ax.legend(fontsize=11, loc='upper left', frameon=True,
              fancybox=True, framealpha=0.95)
    ax.grid(True, which='major', alpha=0.35, linewidth=0.7)
    ax.grid(True, which='minor', alpha=0.15, linewidth=0.5)

    # Annotate the BF wall
    bf = df[df['algorithm'] == 'BruteForce']
    if not bf.empty:
        bf_max_n = int(bf['n'].max())
        bf_max_runtime = bf[bf['n'] == bf_max_n]['runtime_ms'].mean()
        ax.annotate(
            f'BruteForce stops at n={bf_max_n}\n(2$^n$ explodes beyond this)',
            xy=(bf_max_n, bf_max_runtime),
            xytext=(bf_max_n * 0.4, bf_max_runtime * 25),
            fontsize=10, color='#a93226',
            arrowprops=dict(arrowstyle='->', color='#a93226', lw=1.2, alpha=0.7),
            bbox=dict(boxstyle='round,pad=0.4', facecolor='#fdedec',
                      edgecolor='#a93226', alpha=0.85),
        )

    fig.tight_layout()
    _save(fig, 'fig1_runtime_vs_n.png')


# ── Fig 4: Approximation quality per instance category ───────────────────────

def plot_approx_quality(df):
    import matplotlib.pyplot as plt
    import pandas as pd

    exact_algs = ['BruteForce', 'Memoization', 'Tabulation']
    key = ['category', 'n_label', 'ratio', 'instance']
    optimal = (df[df['algorithm'].isin(exact_algs)]
                 .groupby(key)['result'].max()
                 .reset_index().rename(columns={'result': 'optimal'}))

    approx_specs = [
        ('Greedy', '#9b59b6', 'Greedy  (≥ OPT/2)', 0.50),
        ('FPTAS',  '#1abc9c', 'FPTAS ε=0.25  (≥ 0.75·OPT)', 0.75),
    ]

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    for ax, (alg, color, title, floor) in zip(axes, approx_specs):
        sub = df[df['algorithm'] == alg][key + ['result', 'n']].rename(
            columns={'result': 'approx'})
        merged = sub.merge(optimal, on=key)
        merged = merged[merged['optimal'] > 0].copy()
        merged['ratio'] = merged['approx'] / merged['optimal']
        merged['cat_short'] = merged['category'].str[2:].str[:18]

        cats = sorted(merged['cat_short'].unique())
        data = [merged[merged['cat_short'] == c]['ratio'].dropna().values for c in cats]

        bp = ax.boxplot(data, patch_artist=True, labels=cats, widths=0.6,
                        medianprops=dict(color='black', linewidth=2),
                        whiskerprops=dict(color='#444'),
                        capprops=dict(color='#444'),
                        flierprops=dict(marker='o', markersize=3, markerfacecolor='#888',
                                        markeredgecolor='#444', alpha=0.6))
        for patch in bp['boxes']:
            patch.set_facecolor(color)
            patch.set_alpha(0.55)

        ax.axhline(1.0, color='#16a085', linestyle='--', linewidth=1.5, alpha=0.75,
                   label='Optimal (1.0)')
        ax.axhline(floor, color='#c0392b', linestyle=':', linewidth=1.5, alpha=0.75,
                   label=f'Theoretical floor ({floor:.0%})')
        ax.set_xlabel('Instance Category', fontsize=11)
        ax.set_title(title, fontsize=13, fontweight='bold', pad=8)
        ax.tick_params(axis='x', rotation=40, labelsize=9)
        ax.tick_params(axis='y', labelsize=10)
        ax.legend(fontsize=9, loc='lower left', framealpha=0.9)
        ax.set_ylim(0.40, 1.05)
        ax.grid(True, axis='y', alpha=0.3)

    axes[0].set_ylabel('approx / optimum', fontsize=12)
    fig.suptitle('Approximation Quality by Instance Category  (n ≤ 100, both ratios)',
                 fontsize=14, fontweight='bold', y=1.02)
    fig.tight_layout()
    _save(fig, 'fig4_approx_ratio.png')


# ── Entry ────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(CSV):
        print(f"[ERROR] No CSV at {CSV} — run benchmark_n50.py first.")
        sys.exit(1)

    import matplotlib
    matplotlib.use('Agg')

    df = _load()
    print(f"Loaded {len(df):,} executed rows from {os.path.basename(CSV)}")
    print(f"  algorithms:  {sorted(df['algorithm'].unique())}")
    print(f"  n values:    {sorted(int(x) for x in df['n'].unique())}")
    print(f"  ratios:      {sorted(df['ratio'].unique())}")
    print()

    plot_runtime_vs_n(df)
    plot_approx_quality(df)
    print(f"\nDone. Plots saved to {PLOTS}")


if __name__ == '__main__':
    main()
