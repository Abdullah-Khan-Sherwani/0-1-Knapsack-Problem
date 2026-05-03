import math


def knapsack_fptas(capacity, values, weights, epsilon=0.25):
    n = len(values)
    if n == 0:
        return 0

    P = max(values)
    K = (epsilon * P) / n

    scaled = [math.floor(v / K) for v in values]
    max_profit = sum(scaled)

    INF = float('inf')

    # 1-D profit-indexed DP: dp[p] = min weight to achieve scaled profit p.
    # Space O(n^2/eps) -- no 2-D table, no reconstruction.
    dp = [INF] * (max_profit + 1)
    dp[0] = 0

    for i in range(n):
        vi = scaled[i]
        wi = weights[i]
        if vi == 0:
            continue
        for p in range(max_profit, vi - 1, -1):
            if dp[p - vi] + wi < dp[p]:
                dp[p] = dp[p - vi] + wi

    best_p = 0
    for p in range(max_profit, -1, -1):
        if dp[p] <= capacity:
            best_p = p
            break

    return int(best_p * K)


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    result = knapsack_fptas(capacity, values, weights, epsilon=0.25)
    print("FPTAS Result (eps=0.25):", result)
    print("Optimal (DP):            220")
    print("Approximation ratio:    ", round(result / 220, 3), " (guarantee >= 0.75)")
