def knapsack_brute_force(capacity, n, values, weights):
    if n == 0 or capacity == 0:
        return 0
    elif weights[n - 1] > capacity:
        return knapsack_brute_force(capacity, n - 1, values, weights)
    else:
        include_item = values[n - 1] + knapsack_brute_force(capacity - weights[n - 1], n - 1, values, weights)
        exclude_item = knapsack_brute_force(capacity, n - 1, values, weights)
        return max(include_item, exclude_item)


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    n        = len(values)
    print("Maximum value in Knapsack =", knapsack_brute_force(capacity, n, values, weights))
