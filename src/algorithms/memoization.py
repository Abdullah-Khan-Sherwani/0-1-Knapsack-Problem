def knapsack_memoization(capacity, n, values, weights, memo):
    if memo[n][capacity] is not None:
        return memo[n][capacity]

    if n == 0 or capacity == 0:
        result = 0
    elif weights[n - 1] > capacity:
        result = knapsack_memoization(capacity, n - 1, values, weights, memo)
    else:
        include_item = values[n - 1] + knapsack_memoization(capacity - weights[n - 1], n - 1, values, weights, memo)
        exclude_item = knapsack_memoization(capacity, n - 1, values, weights, memo)
        result = max(include_item, exclude_item)

    memo[n][capacity] = result
    return result


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    n        = len(values)
    memo     = [[None] * (capacity + 1) for _ in range(n + 1)]
    print("Maximum value in Knapsack =", knapsack_memoization(capacity, n, values, weights, memo))
