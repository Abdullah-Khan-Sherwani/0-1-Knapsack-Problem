/*
 * Problem (Q6):
 *
 * Given a sequence A of n integers and an integer x, design a divide-and-conquer
 * algorithm to find the frequency of x in A (i.e., the number of times x appears in A).
 * What is the time complexity of your algorithm?
 */

function countFrequency(A: number[], x: number) : number {
    if (A.length === 0) return 0;
    return countInRange(A, 0, A.length - 1, x);
}

function countInRange(A: number[], low: number, high: number, x: number): number {
    if (low >= high) return A[low] === x ? 1:0;

    const mid = Math.floor((low + high) / 2);
    return countInRange(A, low, mid, x) + countInRange(A, mid + 1, high, x);
}

function main() {
  const A = [1, 2, 3, 2, 2, 4];
  const x = 2;
  console.log(`freq of ${x} in [${A}] =`, countFrequency(A, x));
}

main();