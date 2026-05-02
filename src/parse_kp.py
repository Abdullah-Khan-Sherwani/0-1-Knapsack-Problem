def parse_kp(filepath):
    """Parse a .kp file. Returns (n, capacity, values, weights)."""
    with open(filepath, 'r') as f:
        lines = [ln.strip() for ln in f if ln.strip()]
    n        = int(lines[0])
    capacity = int(lines[1])
    weights, values = [], []
    for ln in lines[2 : n + 2]:
        parts = ln.split()
        weights.append(int(parts[0]))
        values.append(int(parts[1]))
    return n, capacity, values, weights
