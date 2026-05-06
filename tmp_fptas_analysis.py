import csv
from collections import defaultdict
from statistics import mean, median

data = []
with open("results/benchmark_n100.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        if row["skipped"] == "False":
            data.append({
                "n": int(row["n"]),
                "algo": row["algorithm"],
                "rt": float(row["runtime_ms"]),
                "capacity": int(row["capacity"]),
            })

algo_n = defaultdict(list)
for r in data:
    algo_n[(r["algo"], r["n"])].append(r["rt"])

algos = ["BruteForce","Memoization","Tabulation","SpaceOptimised","Greedy","FPTAS"]
ns = sorted(set(r["n"] for r in data))

print(f"{'Algo':<20} {'n':<6} {'mean_ms':>10} {'median_ms':>10} {'count':>6}")
print("-"*56)
for algo in algos:
    for n in ns:
        vals = algo_n.get((algo, n), [])
        if vals:
            print(f"{algo:<20} {n:<6} {mean(vals):>10.3f} {median(vals):>10.3f} {len(vals):>6}")

print("\n=== FPTAS vs DP at each n (mean ms) ===")
print(f"{'n':<6} {'FPTAS':>10} {'Tabulation':>12} {'SpaceOpt':>12} {'Memo':>10} | FPTAS/Tab  FPTAS/SO")
print("-"*75)
for n in ns:
    fptas = mean(algo_n.get(("FPTAS", n), [0]))
    tab = mean(algo_n.get(("Tabulation", n), [0]))
    so = mean(algo_n.get(("SpaceOptimised", n), [0]))
    memo = mean(algo_n.get(("Memoization", n), [0]))
    ratio_tab = fptas/tab if tab else float("inf")
    ratio_so = fptas/so if so else float("inf")
    print(f"{n:<6} {fptas:>10.3f} {tab:>12.3f} {so:>12.3f} {memo:>10.3f} | {ratio_tab:>8.3f}x  {ratio_so:>8.3f}x")

print("\n=== Capacity stats ===")
cap_by_n = defaultdict(list)
for r in data:
    cap_by_n[r["n"]].append(r["capacity"])
print(f"{'n':<6} {'mean_W':>10} {'max_W':>10}")
for n in ns:
    caps = cap_by_n[n]
    if caps:
        print(f"{n:<6} {mean(caps):>10.0f} {max(caps):>10.0f}")

print("\n=== FPTAS vs Greedy ===")
print(f"{'n':<6} {'FPTAS':>10} {'Greedy':>10} | ratio")
for n in ns:
    fptas = mean(algo_n.get(("FPTAS", n), [0]))
    greedy = mean(algo_n.get(("Greedy", n), [0]))
    ratio = fptas/greedy if greedy else float("inf")
    print(f"{n:<6} {fptas:>10.3f} {greedy:>10.3f} | {ratio:>6.1f}x")
