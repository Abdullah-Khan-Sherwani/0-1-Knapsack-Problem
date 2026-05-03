def knapsack_greedy(capacity, values, weights):
    n      = len(values)
    ratios = [(values[i] / weights[i], i) for i in range(n)]
    ratios.sort(reverse=True)

    s1_value = 0
    total_weight = 0
    s2_value = 0  # value of first item that doesn't fit

    for ratio, item in ratios:
        if total_weight + weights[item] <= capacity:
            s1_value     += values[item]
            total_weight += weights[item]
        elif s2_value == 0 and weights[item] <= capacity:
            # first item that didn't fit (individually fits the sack)
            s2_value = values[item]

    return max(s1_value, s2_value)


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    print("Greedy Approximation Result:", knapsack_greedy(capacity, values, weights))
