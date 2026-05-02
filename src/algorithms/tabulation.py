def knapsack_tabulation(capacity, values, weights):
    n   = len(values)
    tab = [[0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        for w in range(1, capacity + 1):
            if weights[i - 1] <= w:
                include_item = values[i - 1] + tab[i - 1][w - weights[i - 1]]
                exclude_item = tab[i - 1][w]
                tab[i][w] = max(include_item, exclude_item)
            else:
                tab[i][w] = tab[i - 1][w]

    items_included = []
    w = capacity
    for i in range(n, 0, -1):
        if tab[i][w] != tab[i - 1][w]:
            items_included.append(i - 1)
            w -= weights[i - 1]

    return tab[n][capacity], items_included


if __name__ == "__main__":
    values   = [60, 100, 120, 80]
    weights  = [10,  20,  30, 25]
    capacity = 50
    max_val, items = knapsack_tabulation(capacity, values, weights)
    print("Maximum value in Knapsack =", max_val)
    print("Items included (0-indexed):", items)
    print("Total Weight              :", sum(weights[i] for i in items))
