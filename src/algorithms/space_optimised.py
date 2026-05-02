def knapsack_space_optimised(values, weights, n, W):
    dp = [0] * (W + 1)
    for i in range(n):
        for w in range(W, weights[i] - 1, -1):
            dp[w] = max(dp[w], values[i] + dp[w - weights[i]])
    return dp[W]


if __name__ == "__main__":
    values  = [60, 100, 120, 80]
    weights = [10,  20,  30, 25]
    n, W    = 4, 50
    result  = knapsack_space_optimised(values, weights, n, W)
    print(f"Space-Optimised Result: {result}")  # Expected: 220
