def knapsack_greedy(capacity, values, weights):
    n      = len(values)
    ratios = [(values[i] / weights[i], i) for i in range(n)]
    ratios.sort(reverse=True)

    s1_value     = 0
    s1_items     = []
    total_weight = 0
    s2_value     = 0   # value of first item that doesn't fit
    s2_item      = None

    for ratio, item in ratios:
        if total_weight + weights[item] <= capacity:
            s1_value     += values[item]
            s1_items.append(item)
            total_weight += weights[item]
        elif s2_value == 0 and weights[item] <= capacity:
            # first item that didn't fit (individually fits the sack)
            s2_value = values[item]
            s2_item  = item

    if s1_value >= s2_value:
        return s1_value, sorted(s1_items)
    return s2_value, [s2_item] if s2_item is not None else []


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    max_val, items = knapsack_greedy(capacity, values, weights)
    print("Greedy Approximation Result:", max_val)
    print("Items included (0-indexed) :", items)
    print("Total Weight               :", sum(weights[i] for i in items))
