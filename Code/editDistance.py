class Solution:
    def edit_distance(self, s1, s2):
        """
        Compute the minimum edit distance (Levenshtein distance) between two strings.
        Operations allowed: insert, delete, substitute
        """
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]
        
        # Base cases
        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j
        
        # Fill table left to right, top to bottom
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = 1 + min(
                        dp[i - 1][j],      # delete from s1
                        dp[i][j - 1],      # insert into s1
                        dp[i - 1][j - 1]   # substitute
                    )
        
        return dp[m][n], dp


def main():
    solution = Solution()
    
    print("="*70)
    print("EDIT DISTANCE (LEVENSHTEIN DISTANCE) - DYNAMIC PROGRAMMING")
    print("="*70)
    print()
    
    # Test case 1: EXECUTION vs INTENTION
    s1 = "EXECUTION"
    s2 = "INTENTION"
    dist1, dp_table1 = solution.edit_distance(s1, s2)
    
    print(f"Test Case 1:")
    print(f"String 1 (rows): '{s1}'")
    print(f"String 2 (cols): '{s2}'")
    print(f"Minimum Edit Distance: {dist1}")
    print()
    
    print("DP Table (Edit Distance values):")
    print("-" * 70)
    # Print header (ε = empty string column)
    print(f"    {'ε':>5}", end="")
    for char in s2:
        print(f"{char:>5}", end="")
    print()
    
    # Print rows
    for i in range(len(s1) + 1):
        if i == 0:
            print(f"  ε ", end="")
        else:
            print(f"  {s1[i-1]} ", end="")
        for j in range(len(s2) + 1):
            print(f"{dp_table1[i][j]:>5}", end="")
        print()
    print()
    print("="*70)
    print()
    
    # Test case 2: Simple example
    s3 = "CAT"
    s4 = "DOG"
    dist2, dp_table2 = solution.edit_distance(s3, s4)
    
    print(f"Test Case 2:")
    print(f"String 1: '{s3}'")
    print(f"String 2: '{s4}'")
    print(f"Minimum Edit Distance: {dist2}")
    print()
    
    print("DP Table:")
    print("-" * 70)
    print(f"    {'ε':>5}", end="")
    for char in s4:
        print(f"{char:>5}", end="")
    print()
    
    for i in range(len(s3) + 1):
        if i == 0:
            print(f"  ε ", end="")
        else:
            print(f"  {s3[i-1]} ", end="")
        for j in range(len(s4) + 1):
            print(f"{dp_table2[i][j]:>5}", end="")
        print()
    print()
    print("="*70)
    print()
    
    # Test case 3: Identical strings
    s5 = "HELLO"
    s6 = "HELLO"
    dist3, _ = solution.edit_distance(s5, s6)
    
    print(f"Test Case 3:")
    print(f"String 1: '{s5}'")
    print(f"String 2: '{s6}'")
    print(f"Minimum Edit Distance: {dist3}")
    print()
    print("="*70)


if __name__ == "__main__":
    main()