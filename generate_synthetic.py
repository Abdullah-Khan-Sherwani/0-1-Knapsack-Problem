import os, random

KPLIB = os.path.join('testcases', 'kplib')
SIZES = [5, 8, 10, 12, 15, 18, 20, 22, 25]
SEEDS = [0, 1, 2]
CATEGORY = '13Synthetic'
RATIO    = 'R01000'

def make_instance(n, seed):
    rng = random.Random(seed)
    weights = [rng.randint(1, 100) for _ in range(n)]
    values  = [rng.randint(1, 1000) for _ in range(n)]
    capacity = max(1, sum(weights) // 2)   # ~50% of total weight
    return n, capacity, weights, values

def write_kp(path, n, capacity, weights, values):
    with open(path, 'w') as f:
        f.write(f'{n}\n{capacity}\n')
        for w, v in zip(weights, values):
            f.write(f'{w} {v}\n')

for n in SIZES:
    n_label = f'n{n:05d}'
    folder  = os.path.join(KPLIB, CATEGORY, n_label, RATIO)
    os.makedirs(folder, exist_ok=True)
    for seed in SEEDS:
        n_, cap, wts, vals = make_instance(n, seed)
        fp = os.path.join(folder, f's{seed:03d}.kp')
        write_kp(fp, n_, cap, wts, vals)
        print(f'  wrote {fp}  (n={n_}, cap={cap})')

print(f'\nDone — {len(SIZES) * len(SEEDS)} files created under {CATEGORY}/')
