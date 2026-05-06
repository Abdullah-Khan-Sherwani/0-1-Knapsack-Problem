def knapsack_memoization(capacity, n, values, weights, memo):
    if memo[n][capacity] is not None:
        return memo[n][capacity]

    if n == 0 or capacity == 0:
        result = (0, [])
    elif weights[n - 1] > capacity:
        result = knapsack_memoization(capacity, n - 1, values, weights, memo)
    else:
        inc_val, inc_items = knapsack_memoization(capacity - weights[n - 1], n - 1, values, weights, memo)
        inc_val += values[n - 1]
        exc_val, exc_items = knapsack_memoization(capacity, n - 1, values, weights, memo)
        if inc_val >= exc_val:
            result = (inc_val, inc_items + [n - 1])
        else:
            result = (exc_val, exc_items)

    memo[n][capacity] = result
    return result


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    n        = len(values)
    memo     = [[None] * (capacity + 1) for _ in range(n + 1)]
    max_val, items = knapsack_memoization(capacity, n, values, weights, memo)
    print("Maximum value in Knapsack =", max_val)
    print("Items included (0-indexed):", sorted(items))
    print("Total Weight              :", sum(weights[i] for i in items))
