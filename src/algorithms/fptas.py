import math


def knapsack_fptas(capacity, values, weights, epsilon=0.5):
    n = len(values)
    if n == 0:
        return 0

    P = max(values)
    K = (epsilon * P) / n

    # Scale profits down -- caps max_profit at n^2/epsilon
    scaled = [math.floor(v / K) for v in values]
    max_profit = sum(scaled)

    INF = float('inf')

    # Profit-indexed DP: dp[i][p] = min weight to achieve scaled profit p
    # using items 0..i-1.  Size: O(n * n^2/eps) -- fully polynomial.
    dp = [[INF] * (max_profit + 1) for _ in range(n + 1)]
    dp[0][0] = 0

    for i in range(1, n + 1):
        vi = scaled[i - 1]
        wi = weights[i - 1]
        for p in range(max_profit + 1):
            dp[i][p] = dp[i - 1][p]                          # skip item i
            if p >= vi and dp[i - 1][p - vi] + wi < dp[i][p]:
                dp[i][p] = dp[i - 1][p - vi] + wi            # take item i

    # Best scaled profit whose min weight fits in capacity
    best_p = 0
    for p in range(max_profit, -1, -1):
        if dp[n][p] <= capacity:
            best_p = p
            break

    # Backtrack to recover actual (unscaled) value of selected items
    actual_value = 0
    p = best_p
    for i in range(n, 0, -1):
        vi = scaled[i - 1]
        if p >= vi and dp[i - 1][p - vi] + weights[i - 1] == dp[i][p]:
            actual_value += values[i - 1]
            p -= vi

    return actual_value


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    result = knapsack_fptas(capacity, values, weights, epsilon=0.25)
    print("FPTAS Result (eps=0.25):", result)
    print("Optimal (DP):            220")
    print("Approximation ratio:    ", round(result / 220, 3), " (guarantee >= 0.75)")
