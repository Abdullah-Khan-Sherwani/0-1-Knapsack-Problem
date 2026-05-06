import math


def knapsack_fptas(capacity, values, weights, epsilon=0.25):
    n = len(values)
    if n == 0:
        return 0, []

    P = max(values)
    K = (epsilon * P) / n

    scaled = [math.floor(v / K) for v in values]
    max_profit = sum(scaled)

    INF = float('inf')

    # 2D profit-indexed DP: dp[i][p] = min weight to achieve scaled profit p using first i items.
    dp = [[INF] * (max_profit + 1) for _ in range(n + 1)]
    dp[0][0] = 0

    for i in range(1, n + 1):
        vi = scaled[i - 1]
        wi = weights[i - 1]
        for p in range(max_profit + 1):
            dp[i][p] = dp[i - 1][p]  # exclude item i
            if vi > 0 and p >= vi and dp[i - 1][p - vi] + wi < dp[i][p]:
                dp[i][p] = dp[i - 1][p - vi] + wi  # include item i

    best_p = 0
    for p in range(max_profit, -1, -1):
        if dp[n][p] <= capacity:
            best_p = p
            break

    # Backtrack to recover which items were included
    items = []
    p = best_p
    for i in range(n, 0, -1):
        vi = scaled[i - 1]
        wi = weights[i - 1]
        if vi > 0 and p >= vi and dp[i - 1][p - vi] + wi == dp[i][p]:
            items.append(i - 1)
            p -= vi

    return int(best_p * K), items


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    result, items = knapsack_fptas(capacity, values, weights, epsilon=0.25)
    print("FPTAS Result (eps=0.25):", result)
    print("Items included (0-indexed):", sorted(items))
    print("Total Weight              :", sum(weights[i] for i in items))
    print("Optimal (DP):              220")
    print("Approximation ratio:      ", round(result / 220, 3), " (guarantee >= 0.75)")
