def optimal_matrix_mult(matrices):
    N = len(matrices)
    m = [[float('inf')] * N for _ in range(N)]
    s = [[0] * N for _ in range(N)]

    for i in range(N):
        m[i][i] = 0

    for L in range(2, N + 1):
        for i in range(N - L + 1):
            j = i + L - 1
            for k in range(i, j):
                cost = (m[i][k] + m[k + 1][j]
                        + matrices[i][0] * matrices[k][1] * matrices[j][1])
                if cost < m[i][j]:
                    m[i][j] = cost
                    s[i][j] = k

    def construct_parens(i, j):
        if i == j:
            return f"M{i + 1}"
        k = s[i][j]
        left = construct_parens(i, k)
        right = construct_parens(k + 1, j)
        return f"({left} {right})"

    return m[0][N - 1], construct_parens(0, N - 1), m, s

matrices = [(1, 5), (5, 2), (2, 3), (3, 9), (9, 4)]
cost, parens, _, _ = optimal_matrix_mult(matrices)
print(cost, parens)
