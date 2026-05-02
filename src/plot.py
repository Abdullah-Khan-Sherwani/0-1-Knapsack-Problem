import os, sys
import numpy as np

_ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(_ROOT, 'results')
PLOTS   = os.path.join(RESULTS, 'plots')

ALG_COLORS = {
    'BruteForce':     '#e74c3c',
    'Memoization':    '#3498db',
    'Tabulation':     '#2ecc71',
    'SpaceOptimised': '#f39c12',
    'Greedy':         '#9b59b6',
}
ALG_ORDER = ['BruteForce', 'Memoization', 'Tabulation', 'SpaceOptimised', 'Greedy']


def _save(fig, name):
    import matplotlib.pyplot as plt
    os.makedirs(PLOTS, exist_ok=True)
    path = os.path.join(PLOTS, name)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    plt.close(fig)
    print(f"  Saved: {path}")


def _load(csv_path):
    import pandas as pd
    df = pd.read_csv(csv_path)
    df = df[df['skipped'].astype(str) == 'False'].copy()
    df['runtime_ms'] = pd.to_numeric(df['runtime_ms'], errors='coerce')
    df['n']          = pd.to_numeric(df['n'], errors='coerce')
    df['result']     = pd.to_numeric(df['result'], errors='coerce')
    return df.dropna(subset=['runtime_ms', 'n'])


# ── Fig 1: Runtime vs n — all algorithms ──────────────────────────────────────

def plot_runtime_vs_n(df):
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(10, 6))
    for alg in ALG_ORDER:
        sub = df[df['algorithm'] == alg]
        if sub.empty:
            continue
        g = sub.groupby('n')['runtime_ms'].median().reset_index()
        ax.plot(g['n'], g['runtime_ms'], marker='o',
                label=alg, color=ALG_COLORS[alg], linewidth=2, markersize=5)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Number of Items (n)', fontsize=12)
    ax.set_ylabel('Runtime (ms, median)', fontsize=12)
    ax.set_title('Runtime vs Problem Size — All Algorithms', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig1_runtime_vs_n.png')


# ── Fig 2: DP variants comparison ─────────────────────────────────────────────

def plot_dp_comparison(df):
    import matplotlib.pyplot as plt

    dp_algs = ['Memoization', 'Tabulation', 'SpaceOptimised']
    fig, ax = plt.subplots(figsize=(10, 6))
    for alg in dp_algs:
        sub = df[df['algorithm'] == alg]
        if sub.empty:
            continue
        g = sub.groupby('n')['runtime_ms'].median().reset_index()
        ax.plot(g['n'], g['runtime_ms'], marker='o',
                label=alg, color=ALG_COLORS[alg], linewidth=2, markersize=5)

    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.set_xlabel('Number of Items (n)', fontsize=12)
    ax.set_ylabel('Runtime (ms, median)', fontsize=12)
    ax.set_title('DP Variants — Runtime Comparison (O(nW) each)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, which='both', alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig2_dp_variants.png')


# ── Fig 3: Brute Force vs DP for small n ──────────────────────────────────────

def plot_brute_force_small(df):
    import matplotlib.pyplot as plt

    small = df[df['n'] <= 20]
    if small.empty:
        print("  [skip] No small-n data for brute force plot.")
        return

    fig, ax = plt.subplots(figsize=(9, 6))
    for alg in ['BruteForce', 'Tabulation', 'SpaceOptimised']:
        sub = small[small['algorithm'] == alg]
        if sub.empty:
            continue
        g = sub.groupby('n')['runtime_ms'].median().reset_index()
        ax.plot(g['n'], g['runtime_ms'], marker='o',
                label=alg, color=ALG_COLORS[alg], linewidth=2, markersize=6)

    # O(2^n) reference curve anchored to BF data
    bf = small[small['algorithm'] == 'BruteForce'].groupby('n')['runtime_ms'].median()
    if len(bf) >= 2:
        ns     = np.arange(int(bf.index.min()), 21)
        ref_n  = int(bf.index[-1])
        ref_ms = bf.iloc[-1]
        theory = ref_ms * (2.0 ** (ns - ref_n))
        ax.plot(ns, theory, 'k--', alpha=0.55, linewidth=1.5, label='O(2ⁿ) theoretical')

    ax.set_xlabel('Number of Items (n)', fontsize=12)
    ax.set_ylabel('Runtime (ms, median)', fontsize=12)
    ax.set_title('Brute Force vs DP — Small Instances (n ≤ 20)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig3_brute_force_small_n.png')


# ── Fig 4: Greedy approximation ratio ─────────────────────────────────────────

def plot_greedy_ratio(df):
    import matplotlib.pyplot as plt
    import pandas as pd

    dp = df[df['algorithm'].isin(['Tabulation', 'SpaceOptimised', 'Memoization'])]
    optimal = (dp.groupby(['category', 'n_label', 'ratio', 'instance'])['result']
                 .max().reset_index().rename(columns={'result': 'optimal'}))

    greedy = (df[df['algorithm'] == 'Greedy']
              [['category', 'n_label', 'ratio', 'instance', 'result']]
              .rename(columns={'result': 'greedy_result'}))

    merged = greedy.merge(optimal, on=['category', 'n_label', 'ratio', 'instance'])
    merged = merged[merged['optimal'] > 0].copy()
    merged['approx_ratio'] = merged['greedy_result'] / merged['optimal']
    merged['cat_short']    = merged['category'].str[2:].str.replace(r'(?<=[a-z])(?=[A-Z])', ' ', regex=True).str[:20]

    cats = sorted(merged['cat_short'].unique())
    data = [merged[merged['cat_short'] == c]['approx_ratio'].dropna().values for c in cats]

    fig, ax = plt.subplots(figsize=(14, 6))
    bp = ax.boxplot(data, patch_artist=True, labels=cats,
                    medianprops=dict(color='black', linewidth=2))
    for patch in bp['boxes']:
        patch.set_facecolor('#3498db')
        patch.set_alpha(0.6)

    ax.axhline(1.0, color='red', linestyle='--', linewidth=1.5, label='Optimal (ratio = 1.0)')
    ax.set_xlabel('Instance Category', fontsize=12)
    ax.set_ylabel('Greedy Result / Optimal DP Result', fontsize=12)
    ax.set_title('Greedy Approximation Quality by Instance Category', fontsize=14, fontweight='bold')
    ax.tick_params(axis='x', rotation=45)
    ax.legend(fontsize=10)
    ax.set_ylim(0, 1.12)
    ax.grid(True, axis='y', alpha=0.3)
    fig.tight_layout()
    _save(fig, 'fig4_greedy_approx_ratio.png')


# ── Fig 5: Runtime heatmap — categories × sizes ───────────────────────────────

def plot_heatmap(df):
    import matplotlib.pyplot as plt
    import pandas as pd

    alg = 'Tabulation' if 'Tabulation' in df['algorithm'].values else 'SpaceOptimised'
    sub = df[df['algorithm'] == alg].copy()
    if sub.empty:
        print("  [skip] No tabulation data for heatmap.")
        return

    sub['cat_short'] = sub['category'].str[2:].str[:18]
    pivot = sub.groupby(['cat_short', 'n'])['runtime_ms'].median().unstack('n')

    fig, ax = plt.subplots(figsize=(14, 7))
    data     = pivot.values.astype(float)
    data_log = np.log10(np.where(data > 0, data, np.nan))

    im   = ax.imshow(data_log, aspect='auto', cmap='YlOrRd')
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label('log₁₀(Runtime ms)', fontsize=10)

    ax.set_xticks(range(len(pivot.columns)))
    ax.set_xticklabels([str(int(c)) for c in pivot.columns], rotation=45, fontsize=9)
    ax.set_yticks(range(len(pivot.index)))
    ax.set_yticklabels(pivot.index, fontsize=8)
    ax.set_xlabel('Number of Items (n)', fontsize=12)
    ax.set_ylabel('Instance Category', fontsize=12)
    ax.set_title(f'{alg} Runtime Heatmap — Category × Problem Size',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    _save(fig, 'fig5_runtime_heatmap.png')


# ── Fig 6: Theoretical vs empirical growth ────────────────────────────────────

def plot_theoretical_vs_empirical(df):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Left — DP empirical with fitted power-law overlay
    ax = axes[0]
    for alg in ['Memoization', 'Tabulation', 'SpaceOptimised']:
        sub = df[df['algorithm'] == alg]
        if sub.empty:
            continue
        g = sub.groupby('n')['runtime_ms'].median().reset_index()
        ax.plot(g['n'], g['runtime_ms'], marker='o',
                label=alg, color=ALG_COLORS[alg], linewidth=2, markersize=5)

    tab = df[df['algorithm'] == 'Tabulation'].groupby('n')['runtime_ms'].median()
    if len(tab) >= 3:
        xs = np.log(tab.index.values.astype(float))
        ys = np.log(tab.values.astype(float))
        m, b = np.polyfit(xs, ys, 1)
        ns_fit = np.array(sorted(df['n'].unique()), dtype=float)
        ax.plot(ns_fit, np.exp(b) * ns_fit ** m, 'k--', alpha=0.5, linewidth=1.5,
                label=f'fitted O(n^{m:.2f})')

    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel('n', fontsize=12); ax.set_ylabel('Runtime (ms)', fontsize=12)
    ax.set_title('DP Algorithms — Empirical Growth', fontsize=13, fontweight='bold')
    ax.legend(fontsize=9); ax.grid(True, which='both', alpha=0.3)

    # Right — Greedy with O(n log n) overlay
    ax2 = axes[1]
    sub = df[df['algorithm'] == 'Greedy']
    if not sub.empty:
        g = sub.groupby('n')['runtime_ms'].median().reset_index()
        ax2.plot(g['n'], g['runtime_ms'], marker='s',
                 label='Greedy (empirical)', color=ALG_COLORS['Greedy'],
                 linewidth=2, markersize=5)

        ns_arr = g['n'].values.astype(float)
        if len(ns_arr) >= 2:
            mid     = len(ns_arr) // 2
            ref_n   = ns_arr[mid]
            ref_ms  = g['runtime_ms'].values[mid]
            theory  = ref_ms * (ns_arr * np.log2(ns_arr + 1)) / (ref_n * np.log2(ref_n + 1))
            ax2.plot(ns_arr, theory, 'k--', alpha=0.5, linewidth=1.5,
                     label='O(n log n) theoretical')

    ax2.set_xscale('log'); ax2.set_yscale('log')
    ax2.set_xlabel('n', fontsize=12); ax2.set_ylabel('Runtime (ms)', fontsize=12)
    ax2.set_title('Greedy — Empirical vs O(n log n)', fontsize=13, fontweight='bold')
    ax2.legend(fontsize=9); ax2.grid(True, which='both', alpha=0.3)

    fig.suptitle('Theoretical vs Empirical Runtime', fontsize=14, fontweight='bold')
    fig.tight_layout()
    _save(fig, 'fig6_theoretical_vs_empirical.png')


# ── Fig 7: Capacity ratio impact (R01000 vs R10000) ───────────────────────────

def plot_capacity_ratio_impact(df):
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)
    dp_algs   = ['Tabulation', 'SpaceOptimised']

    for ax, ratio_val in zip(axes, ['R01000', 'R10000']):
        sub = df[(df['ratio'] == ratio_val) & (df['algorithm'].isin(dp_algs))]
        for alg in dp_algs:
            s = sub[sub['algorithm'] == alg]
            if s.empty:
                continue
            g = s.groupby('n')['runtime_ms'].median().reset_index()
            ax.plot(g['n'], g['runtime_ms'], marker='o',
                    label=alg, color=ALG_COLORS[alg], linewidth=2, markersize=5)

        ax.set_xscale('log'); ax.set_yscale('log')
        ax.set_title(f'Capacity Ratio: {ratio_val}', fontsize=13, fontweight='bold')
        ax.set_xlabel('n', fontsize=11)
        ax.legend(fontsize=9); ax.grid(True, which='both', alpha=0.3)

    axes[0].set_ylabel('Runtime (ms, median)', fontsize=12)
    fig.suptitle('DP Runtime: Low Capacity (R01000) vs High Capacity (R10000)',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    _save(fig, 'fig7_capacity_ratio_impact.png')


# ── Entry point ───────────────────────────────────────────────────────────────

def generate_all_plots(csv_path=None):
    if csv_path is None:
        csv_path = os.path.join(RESULTS, 'benchmark_results.csv')

    try:
        import pandas as pd
        import matplotlib
        matplotlib.use('Agg')
    except ImportError:
        print("[ERROR] Required: pip install matplotlib pandas numpy")
        return

    if not os.path.exists(csv_path):
        print(f"[ERROR] No results at {csv_path} — run benchmark first.")
        return

    df = _load(csv_path)
    print(f"Loaded {len(df):,} result rows from {csv_path}\n")

    plot_runtime_vs_n(df)
    plot_dp_comparison(df)
    plot_brute_force_small(df)
    plot_greedy_ratio(df)
    plot_heatmap(df)
    plot_theoretical_vs_empirical(df)
    plot_capacity_ratio_impact(df)

    print(f"\nAll 7 plots saved to: {PLOTS}")
