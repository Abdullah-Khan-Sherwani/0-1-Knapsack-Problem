def triangle_max_path_sum(T, n):
    dp = [[0] * (i + 1) for i in range(n)]
    dp[0][0] = T[0][0]
    for i in range(1, n):
        for j in range(i + 1):
            if j == 0:
                dp[i][j] = T[i][j] + dp[i - 1][0]
            elif j == i:
                dp[i][j] = T[i][j] + dp[i - 1][j - 1]
            else:
                dp[i][j] = T[i][j] + max(dp[i - 1][j - 1], dp[i - 1][j])
    return max(dp[n - 1])

T = [[3], [7, 4], [2, 4, 6], [8, 5, 9, 3]]
print(triangle_max_path_sum(T, len(T)))
