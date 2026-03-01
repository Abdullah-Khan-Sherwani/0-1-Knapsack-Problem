class Solution:
    def optimalMatMult(self, matrices: list[tuple[int, int]]) -> tuple[int, str, list, list]:
        N = len(matrices)
        m = [[float('inf')] * N for _ in range(N)]
        s = [[0] * N for _ in range(N)]

        for i in range(N):
            m[i][i] = 0

        for L in range(2, N + 1):
            for i in range(N - L + 1):
                j = i + L - 1
                
                for k in range(i, j):
                    cost = m[i][k] + m[k + 1][j] + (matrices[i][0] * matrices[k][1] * matrices[j][1])          
                    if cost < m[i][j]:
                        m[i][j] = cost
                        s[i][j] = k  

        def construct_parens(i, j):
            if i == j:
                return f"M{i + 1}"
            else:
                k = s[i][j]
                left = construct_parens(i, k)
                right = construct_parens(k + 1, j)
                return f"({left} {right})"

        min_cost = int(m[0][N - 1])
        optimal_string = construct_parens(0, N - 1)
        
        return min_cost, optimal_string, m, s

def main():
    solution = Solution()
    
    # M1: 1×5, M2: 5×2, M3: 2×3, M4: 3×9, M5: 9×4
    matrices4 = [(1, 5), (5, 2), (2, 3), (3, 9), (9, 4)]
    cost4, parens4, m_matrix, s_matrix = solution.optimalMatMult(matrices4)
    
    print("="*70)
    print("PROBLEM FROM QUESTION: Five Matrices")
    print("="*70)
    print(f"M1: 1×5, M2: 5×2, M3: 2×3, M4: 3×9, M5: 9×4")
    print()
    
    print("Matrix m (Minimum costs for multiplying chains):")
    print("-" * 70)
    for i, row in enumerate(m_matrix):
        print(f"m[{i}]: ", end="")
        for j, val in enumerate(row):
            if val == float('inf'):
                print(f"{str('∞'):>8}", end=" ")
            else:
                print(f"{int(val):>8}", end=" ")
        print()
    print()
    
    print("Matrix s (Optimal split points):")
    print("-" * 70)
    for i, row in enumerate(s_matrix):
        print(f"s[{i}]: ", end="")
        for j, val in enumerate(row):
            print(f"{val:>8}", end=" ")
        print()
    print()
    
    print("="*70)
    print(f"Minimum scalar multiplications required: {cost4}")
    print(f"Optimal Parenthesization: {parens4}")
    print("="*70)

if __name__ == "__main__":
    main()