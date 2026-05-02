def knapsack_greedy(capacity, values, weights):
    n      = len(values)
    ratios = [(values[i] / weights[i], i) for i in range(n)]
    ratios.sort(reverse=True)

    total_value  = 0
    total_weight = 0

    for ratio, item in ratios:
        if total_weight + weights[item] <= capacity:
            total_value  += values[item]
            total_weight += weights[item]

    return total_value


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    print("Greedy Approximation Result:", knapsack_greedy(capacity, values, weights))
