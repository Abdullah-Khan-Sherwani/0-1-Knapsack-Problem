def parse_kp(filepath):
    """Parse a .kp file. Returns (n, capacity, values, weights).
    
    File format (per kplib README):
        n
        c
        p_1 w_1  (p = price/value, w = weight)
        p_2 w_2
        ...
        p_n w_n
    """
    with open(filepath, 'r') as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    n        = int(lines[0])
    capacity = int(lines[1])
    weights, values = [], []
    for ln in lines[2 : n + 2]:
        parts = ln.split()
        values.append(int(parts[0]))   # p_i = price/value (first column)
        weights.append(int(parts[1]))  # w_i = weight (second column)
    return n, capacity, values, weights
