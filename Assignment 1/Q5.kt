/*
 * Problem (Q5):
 *
 * Let A = ⟨a1, . . . , an⟩ be an array of n distinct positive integers.
 * An element ai (1 ≤ i ≤ n) is called a peak element if none of its neighbors are larger than it.
 * Two elements ai and aj are neighbors if |i − j| = 1.
 *
 * Design a divide-and-conquer O(log n) algorithm to find one peak element.
 */

fun findPeak(A: IntArray): Int {
    if (A.isEmpty()) return -1

    var low = 0
    var high = A.lastIndex

    while(low <= high) {
        val mid = (low + high) / 2
        val leftGreater = mid > 0 && A[mid] < A[mid - 1]
        val rightGreater = mid < A.lastIndex && A[mid] < A[mid + 1]

        if(!leftGreater && !rightGreater) {
            return mid
        } else if (leftGreater) {
            high = mid - 1
        } else {
            low = mid + 1
        }
    }

    return -1
}

fun main() {
    val A = intArrayOf(1, 3, 2, 5, 4)

    val idx = findPeak(A)
    if(idx >= 0) println("Peak index: $idx, value: ${A[idx]}") else println("No Peak found")
}