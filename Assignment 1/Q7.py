"""Q7: Find a local minimum in O(log n) time.

Assumptions are:
An element a[i] is a local minimum if:
  - if i == 0: a[0] < a[1]
  - if i == n-1: a[n-1] < a[n-2]
  - otherwise: a[i] < a[i-1] and a[i] < a[i+1]

Assumes all elements are distinct.
"""


def find_local_min(a) -> int:
    n = len(a)
    if n == 0:
        return -1
    if n == 1:
        return 0
    if a[0] < a[1]:
        return 0
    if a[-1] < a[-2]:
        return n - 1

    low, high = 1, n - 2  
    while low <= high:
        mid = (low + high) // 2
        if a[mid] < a[mid - 1] and a[mid] < a[mid + 1]:
            return mid
        if a[mid - 1] < a[mid]:
            high = mid - 1
        else:
            low = mid + 1

    return -1  


if __name__ == "__main__":
    tests = [[1], [2, 1], [1, 2], [9,6,3,14,5,7,4], [1,2,3,4], [4,3,2,1]]
    for t in tests:
        idx = find_local_min(t)
        print(t, "->", idx, t[idx] if idx != -1 else None)
