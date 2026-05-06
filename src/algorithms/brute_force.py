def knapsack_brute_force(capacity, n, values, weights):
    if n == 0 or capacity == 0:
        return 0, []
    if weights[n - 1] > capacity:
        return knapsack_brute_force(capacity, n - 1, values, weights)
    inc_val, inc_items = knapsack_brute_force(capacity - weights[n - 1], n - 1, values, weights)
    inc_val += values[n - 1]
    exc_val, exc_items = knapsack_brute_force(capacity, n - 1, values, weights)
    if inc_val >= exc_val:
        return inc_val, inc_items + [n - 1]
    return exc_val, exc_items


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    n        = len(values)
    max_val, items = knapsack_brute_force(capacity, n, values, weights)
    print("Maximum value in Knapsack =", max_val)
    print("Items included (0-indexed):", sorted(items))
    print("Total Weight              :", sum(weights[i] for i in items))
