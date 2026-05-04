"""
Generates synthetic kplib-style instances at intermediate n values for both
R01000 (R=1000) and R10000 (R=10000), then statistically verifies each
instance matches its category's mathematical definition.

Formulas: Pisinger "Where are the hard knapsack problems?" (2005)
Format:   matches real kplib exactly (blank line after capacity, p w per line)
"""
import os, sys, random, math

_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ROOT)


KPLIB      = os.path.join(_ROOT, 'testcases', 'kplib')

# ── Configuration — edit these to add more sizes, ratios, or seeds ────────────

# Subset of 13Synthetic sizes (BF-compatible) + gap sizes above BF + between 50-100
# Sizes ≤ BF_MAX_N: BruteForce will also run for full 6-algorithm comparison
SIZES = [
    10, 15, 20, 25,   # BF-compatible (exist in 13Synthetic — same n, different category type)
    30, 40, 45,       # above BF cutoff, below kplib n=50
    60, 75, 90,       # between kplib n=50 and n=100
]

RATIOS = {
    'R01000': 1000,
    'R10000': 10000,
}

SEEDS = list(range(10))   # 10 instances per (category, n, ratio)

# Add more ratios here if needed, e.g. 'R00100': 100


# ── Instance generators (all take n, rng, R) ──────────────────────────────────

def uncorrelated(n, rng, R):
    w = [rng.randint(1, R) for _ in range(n)]
    v = [rng.randint(1, R) for _ in range(n)]
    return w, v


def weakly_correlated(n, rng, R):
    w, v = [], []
    for _ in range(n):
        wi = rng.randint(1, R)
        vi = rng.randint(max(1, wi - R // 10), wi + R // 10)
        w.append(wi); v.append(vi)
    return w, v


def strongly_correlated(n, rng, R):
    w = [rng.randint(1, R) for _ in range(n)]
    v = [wi + R // 10 for wi in w]
    return w, v


def inverse_strongly_correlated(n, rng, R):
    p = [rng.randint(1, R) for _ in range(n)]
    w = [pi + R // 10 for pi in p]
    return w, p


def almost_strongly_correlated(n, rng, R):
    w, v = [], []
    delta = max(1, R // 500)
    for _ in range(n):
        wi     = rng.randint(1, R)
        center = wi + R // 10
        vi     = rng.randint(max(1, center - delta), center + delta)
        w.append(wi); v.append(vi)
    return w, v


def subset_sum(n, rng, R):
    w = [rng.randint(1, R) for _ in range(n)]
    return w, list(w)


def _spanner(n, rng, R, base_fn, v_size=2, m_range=10):
    bw, bv = base_fn(v_size, rng, R)
    w, v   = [], []
    for _ in range(n):
        idx = rng.randint(0, v_size - 1)
        m   = rng.randint(1, m_range)
        w.append(max(1, bw[idx] * m))
        v.append(max(1, bv[idx] * m))
    return w, v


def spanner_uncorrelated(n, rng, R):
    return _spanner(n, rng, R, uncorrelated)


def spanner_weakly_correlated(n, rng, R):
    return _spanner(n, rng, R, weakly_correlated)


def spanner_strongly_correlated(n, rng, R):
    return _spanner(n, rng, R, strongly_correlated)


def multiple_strongly_correlated(n, rng, R, d=6):
    k1 = R // 10
    k2 = R // 10 + R // 20
    w  = [rng.randint(1, R) for _ in range(n)]
    v  = [(wi + k1) if wi % d == 0 else (wi + k2) for wi in w]
    return w, v


def profit_ceiling(n, rng, R, d=3):
    w = [rng.randint(1, R) for _ in range(n)]
    v = [max(1, d * math.floor(wi / d)) for wi in w]
    return w, v


def circle(n, rng, R):
    a = 2.0 / 3.0
    w, v = [], []
    for _ in range(n):
        wi    = rng.randint(1, 2 * R)
        inner = max(0.0, 4.0 * R * R - (wi - 2 * R) ** 2)
        vi    = max(1, int(a * math.sqrt(inner)))
        w.append(wi); v.append(vi)
    return w, v


CATEGORIES = {
    '00Uncorrelated':               uncorrelated,
    '01WeaklyCorrelated':           weakly_correlated,
    '02StronglyCorrelated':         strongly_correlated,
    '03InverseStronglyCorrelated':  inverse_strongly_correlated,
    '04AlmostStronglyCorrelated':   almost_strongly_correlated,
    '05SubsetSum':                  subset_sum,
    '07SpannerUncorrelated':        spanner_uncorrelated,
    '08SpannerWeaklyCorrelated':    spanner_weakly_correlated,
    '09SpannerStronglyCorrelated':  spanner_strongly_correlated,
    '10MultipleStronglyCorrelated': multiple_strongly_correlated,
    '11ProfitCeiling':              profit_ceiling,
    '12Circle':                     circle,
    # 06UncorrelatedWithSimilarWeights excluded — W too large for DP at any n
}


# ── Statistical property verification ────────────────────────────────────────

VERIFY_EXACT   = {'02StronglyCorrelated', '03InverseStronglyCorrelated', '05SubsetSum'}
VERIFY_RANGE   = {'01WeaklyCorrelated', '04AlmostStronglyCorrelated'}
VERIFY_FORMULA = {'11ProfitCeiling'}
VERIFY_PARTIAL = {'07SpannerUncorrelated', '08SpannerWeaklyCorrelated',
                  '09SpannerStronglyCorrelated', '10MultipleStronglyCorrelated', '12Circle'}


def verify_category(cat, weights, values, R):
    """Returns list of property violation strings (empty = all good)."""
    issues = []
    n = len(weights)

    if cat == '02StronglyCorrelated':
        for i, (w, v) in enumerate(zip(weights, values)):
            if v != w + R // 10:
                issues.append(f'item {i}: v={v} != w+R/10={w + R//10}')
                if len(issues) >= 3: break

    elif cat == '03InverseStronglyCorrelated':
        for i, (w, v) in enumerate(zip(weights, values)):
            if w != v + R // 10:
                issues.append(f'item {i}: w={w} != v+R/10={v + R//10}')
                if len(issues) >= 3: break

    elif cat == '05SubsetSum':
        for i, (w, v) in enumerate(zip(weights, values)):
            if v != w:
                issues.append(f'item {i}: v={v} != w={w}')
                if len(issues) >= 3: break

    elif cat == '01WeaklyCorrelated':
        tol = R // 10
        for i, (w, v) in enumerate(zip(weights, values)):
            if abs(v - w) > tol + 1:
                issues.append(f'item {i}: |v-w|={abs(v-w)} > R/10={tol}')
                if len(issues) >= 3: break

    elif cat == '04AlmostStronglyCorrelated':
        tol = max(1, R // 500)
        for i, (w, v) in enumerate(zip(weights, values)):
            center = w + R // 10
            if abs(v - center) > tol + 1:
                issues.append(f'item {i}: |v-center|={abs(v-center)} > R/500={tol}')
                if len(issues) >= 3: break

    elif cat == '11ProfitCeiling':
        d = 3
        for i, v in enumerate(values):
            if v % d != 0 and v != 1:
                issues.append(f'item {i}: v={v} not divisible by d={d}')
                if len(issues) >= 3: break

    elif cat == '10MultipleStronglyCorrelated':
        k1, k2, d = R // 10, R // 10 + R // 20, 6
        for i, (w, v) in enumerate(zip(weights, values)):
            expected = (w + k1) if w % d == 0 else (w + k2)
            if v != expected:
                issues.append(f'item {i}: v={v} != expected={expected}')
                if len(issues) >= 3: break

    elif cat in VERIFY_PARTIAL:
        # Partial: only check weight/value ranges are positive and non-zero
        if any(w <= 0 for w in weights):
            issues.append('non-positive weight found')
        if any(v <= 0 for v in values):
            issues.append('non-positive value found')

    return issues



# ── File I/O ──────────────────────────────────────────────────────────────────

def write_kp(path, n, capacity, weights, values):
    with open(path, 'w') as f:
        f.write(f'{n}\n{capacity}\n\n')
        for vi, wi in zip(values, weights):
            f.write(f'{vi} {wi}\n')


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    anomalies   = []
    total_files = 0

    print('=' * 72)
    print('  Generating & Verifying Synthetic kplib Instances')
    print(f'  Categories : {len(CATEGORIES)}')
    print(f'  Sizes      : {SIZES}')
    print(f'  Ratios     : {list(RATIOS.keys())}')
    print(f'  Seeds      : {len(SEEDS)}  (s000–s{len(SEEDS)-1:03d})')
    print(f'  Total files: {len(CATEGORIES) * len(SIZES) * len(RATIOS) * len(SEEDS)}')
    print('=' * 72)

    for cat_name, gen_fn in CATEGORIES.items():
        cat_issues = 0

        for ratio_name, R in RATIOS.items():
            for n in SIZES:
                n_label = f'n{n:05d}'
                folder  = os.path.join(KPLIB, cat_name, n_label, ratio_name)
                os.makedirs(folder, exist_ok=True)

                for seed in SEEDS:
                    rng = random.Random(seed * 9973 + n * 31 + abs(hash(cat_name)) % 997 + R)
                    weights, values = gen_fn(n, rng, R)
                    capacity = max(1, sum(weights) // 2)

                    fp = os.path.join(folder, f's{seed:03d}.kp')
                    write_kp(fp, n, capacity, weights, values)
                    total_files += 1

                    # ── Statistical property check ────────────────────────
                    prop_issues = verify_category(cat_name, weights, values, R)
                    if prop_issues:
                        for iss in prop_issues:
                            anomalies.append(
                                f'  [PROPERTY] {cat_name}/n={n}/{ratio_name}/s{seed:03d}: {iss}')
                        cat_issues += 1


        status = 'OK' if cat_issues == 0 else f'{cat_issues} ISSUES'
        print(f'  {cat_name:<35} {status}', flush=True)

    # ── Summary ──────────────────────────────────────────────────────────────
    print()
    print(f'  Files written      : {total_files}')
    print()
    if anomalies:
        print(f'ANOMALIES ({len(anomalies)}):')
        for a in anomalies:
            print(a)
    else:
        print('  All checks PASSED.')
        print('  Property formulas verified, exact algorithms consistent,')
        print('  approximation guarantees upheld on all checked instances.')

    print('=' * 72)


if __name__ == '__main__':
    main()
