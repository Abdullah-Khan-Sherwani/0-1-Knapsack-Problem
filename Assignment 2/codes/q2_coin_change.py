def min_coins(C, V):
    dp = [float('inf')] * (V + 1)
    dp[0] = 0
    for v in range(1, V + 1):
        for coin in C:
            if coin <= v and dp[v - coin] != float('inf'):
                dp[v] = min(dp[v], 1 + dp[v - coin])
    return dp[V] if dp[V] != float('inf') else -1

print(min_coins([1, 3, 4], 6))
