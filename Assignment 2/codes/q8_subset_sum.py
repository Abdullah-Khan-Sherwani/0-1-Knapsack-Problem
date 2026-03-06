def subset_sum(S, t):
    n = len(S)
    dp = [[False] * (t + 1) for _ in range(n + 1)]

    for i in range(n + 1):
        dp[i][0] = True

    for i in range(1, n + 1):
        for j in range(1, t + 1):
            dp[i][j] = dp[i - 1][j]
            if S[i - 1] <= j:
                dp[i][j] = dp[i][j] or dp[i - 1][j - S[i - 1]]

    if not dp[n][t]:
        return None

    subset = []
    j = t
    for i in range(n, 0, -1):
        if dp[i][j] and not dp[i - 1][j]:
            subset.append(S[i - 1])
            j -= S[i - 1]

    return subset

print(subset_sum([3, 34, 4, 12, 5, 2], 9))
