# Speaker Script — 0/1 Knapsack Empirical Comparison

**Total target time: 8–10 minutes (≈ 9 min comfortable).**
**Group:** Anas Tabba · Abdullah Khan Sherwani · Zuhair Merchant · Raahin Raajiudin
**Deck:** `knapsack_presentation.pptx` — 15 slides.

---

## Speaker assignments at a glance

| Slides | Speaker     | Approx Time |
|--------|-------------|-------------|
| 1–4    | **Anas**    | 2:15 |
| 5–6    | **Abdullah**| 1:30 |
| 7–8    | **Zuhair**  | 1:30 |
| 9–10   | **Raahin**  | 1:30 |
| 11     | **Anas**    | 0:30 |
| 12     | **Abdullah**| 0:30 |
| 13     | **Zuhair**  | 0:45 |
| 14     | **Raahin**  | 0:45 |
| 15     | **Anas (close)** | 0:30 |

Each speaker handles **one algorithm pair + one results slide**, except Anas who opens, summarises complexity, and closes.

---

## SLIDE 1 — Title (Anas, 0:15)

> "Good [morning/afternoon] everyone. Our group — Anas, Abdullah, Zuhair, and Raahin — has been working on an empirical comparison of six algorithms for the **0/1 Knapsack Problem**. Today we'll walk you through the problem, the algorithms, our benchmark methodology, and what the data actually tells us about which algorithm to pick when."

**Cue:** click → slide 2.

---

## SLIDE 2 — Problem Statement (Anas, 0:30)

> "Formally, you're given **n items**, each with a value and a weight, and a knapsack of capacity W. The goal is to pick a 0/1 indicator x for each item so that the total weight stays under W and the total value is maximised.
>
> The 0/1 part is what makes it hard — you can't take a fraction of an item, only the whole thing or nothing. The problem has been studied since 1957 and is **NP-hard**, though it admits a pseudo-polynomial dynamic programming solution that we'll see shortly."

**Cue:** click → slide 3.

---

## SLIDE 3 — Real-World Use Cases (Anas, 0:35)

> "This isn't a textbook curiosity — the same abstract problem shows up everywhere.
>
> Think **cargo loading** for trucks and aircraft, **capital budgeting** in finance where each project has a fixed cost and an expected return, and **cloud resource allocation** where you decide which jobs to pack onto a server. **Cutting stock** problems in manufacturing reduce to it. Even **cryptography** — the Merkle–Hellman cryptosystem encodes messages as 0/1 selections — and **video games** with limited inventory slots.
>
> Whenever you have a fixed budget and items that are either taken whole or skipped, you have a knapsack."

**Cue:** click → slide 4.

---

## SLIDE 4 — Why These Six Algorithms (Anas, 0:45)

> "We chose these six because together they span the full design space.
>
> On the left, **four exact algorithms** that always return the true optimum but differ in *how* they search and how much memory they need: brute force, top-down memoization, bottom-up tabulation, and a space-optimised version that drops a row.
>
> On the right, **two approximation algorithms** — greedy and FPTAS — that trade a known amount of accuracy for huge speed or memory wins.
>
> The big idea is that there's no single best algorithm. You're trading off three axes — **time, memory, and accuracy** — and the right choice depends entirely on which axis is binding for your input. I'll hand it over to Abdullah to walk through the first two."

**Cue:** click → slide 5. Hand-off to **Abdullah**.

---

## SLIDE 5 — Brute Force (Abdullah, 0:45)

> "Brute force is the naive recursion. For each item you either take it or skip it, recurse on the remaining n − 1 items, and return the maximum of the two branches. No caching at all.
>
> That gives you **O(2ⁿ) time** — every subset is explored. Space is just O(n) for the recursion stack. The advantage is it's trivially correct, which makes it useful as an *oracle* for testing the other algorithms — and that's how we used it.
>
> The disadvantage is obvious: at n = 25 you already have 33 million function calls. Beyond that, infeasible.
>
> On our baseline instance with four items, you can see it correctly returns value 220 by picking items 1 and 2 — the 100 and 120 — for an exact fit."

**Cue:** click → slide 6.

---

## SLIDE 6 — Memoization (Abdullah, 0:45)

> "Memoization is the same recursion as brute force, **plus a 2-D cache** indexed by (items remaining, capacity remaining). Once you've solved a subproblem, you store the answer; the next time you hit it you just look it up.
>
> This collapses the work from O(2ⁿ) down to **O(n × W)** — one unit of work per cell of the table. The price is O(n × W) memory.
>
> A subtle point: this is **pseudo-polynomial**. If you double W, the table doubles, even though the binary input only grew by one bit.
>
> On the baseline it gives the same answer as brute force — value 220, items 1 and 2 — but in a fraction of the time. I'll pass it to Zuhair for the bottom-up versions."

**Cue:** click → slide 7. Hand-off to **Zuhair**.

---

## SLIDE 7 — Tabulation (Zuhair, 0:45)

> "Tabulation is the bottom-up cousin of memoization. Instead of recursing and caching, you fill a 2-D table iteratively from row 0 up to row n. Each cell is computed exactly once.
>
> Same complexity — O(n × W) time and space — but in practice tabulation is **the fastest of the exact algorithms** because there's no recursion overhead and it has better cache locality.
>
> The other big advantage: because you have the full table, you can **walk back through it and recover which items were chosen**. You start at the bottom-right corner and check, at each row, whether the value changed when item i was added. If it did, item i was taken. We use this whenever we need to know what's actually in the knapsack — not just its value."

**Cue:** click → slide 8.

---

## SLIDE 8 — Space-Optimised DP (Zuhair, 0:45)

> "Notice that when filling row i, we only ever read from row i − 1. So we don't actually need the whole table — **just one row, reused**.
>
> The trick is the iteration order: when updating dp[w], you have to walk **w from W downward to weights[i]** so you don't overwrite values you still need.
>
> Same O(n × W) time but only **O(W) memory** — a huge win when W is large.
>
> The trade-off is that **you can't recover the item set** from a single row — that history is exactly what we threw away. So this is value-only, by design. If you needed both, you'd add a parent table, which defeats the optimisation. Over to Raahin for the approximations."

**Cue:** click → slide 9. Hand-off to **Raahin**.

---

## SLIDE 9 — Greedy Approximation (Raahin, 0:45)

> "Greedy is dramatically simpler. Compute each item's **value-to-weight ratio**, sort descending, and pack until the next one doesn't fit.
>
> By itself this can be arbitrarily bad. So the standard fix — sometimes called **strategy S2** — is to also remember the single best item that didn't fit, and return the maximum of the greedy pack and that single item. This guarantees you get **at least half of the true optimum**.
>
> Time complexity is O(n log n) — basically just the sort — and space is O(n). Crucially, **runtime is independent of W**, so when capacity is huge greedy doesn't care.
>
> On our baseline, greedy returns 160 versus the optimal 220 — about 73% — well above the 50% floor but visibly worse than the exact algorithms. This single example is exactly why we benchmark across many input categories."

**Cue:** click → slide 10.

---

## SLIDE 10 — FPTAS (Raahin, 0:45)

> "FPTAS — Fully Polynomial-Time Approximation Scheme — is the more sophisticated approximation. You pick a parameter epsilon between 0 and 1; the algorithm guarantees a result within (1 − ε) of the optimum.
>
> The trick is value scaling. Divide every value by K = εP/n, round down, then run a **profit-indexed DP**: dp at index p stores the *minimum weight* needed to achieve scaled profit p. Take the largest p whose minimum weight fits the capacity, multiply back by K.
>
> Time is O(n³/ε), space O(n²/ε) — polynomial in both n and 1/ε, hence "fully polynomial". You pay more than greedy but get a tighter, **tunable** guarantee.
>
> At ε = 0.25 the formal floor is 75 percent; in practice we typically see 95-percent-plus. I'll hand it back to Anas for the complexity summary."

**Cue:** click → slide 11. Hand-off to **Anas**.

---

## SLIDE 11 — Theoretical Complexity Summary (Anas, 0:30)

> "Putting all six side by side: brute force O(2ⁿ); the three DP variants O(nW), differing only in space; greedy O(n log n); FPTAS O(n³/ε).
>
> The single most important observation is the line at the bottom of the slide: **O(nW) is pseudo-polynomial**. If you double W, you double the work even though the input only grew by one bit. That's why our benchmarks split by capacity range — to make this effect visible in the data."

**Cue:** click → slide 12. Hand-off to **Abdullah**.

---

## SLIDE 12 — Benchmark Methodology (Abdullah, 0:30)

> "Our test bed is the **Pisinger kplib** — the standard benchmark suite used in knapsack research. Fourteen instance categories, ranging from uncorrelated, where values and weights are independent, to strongly correlated, which is the hard case where every item has nearly the same ratio. We run on n from 5 up to 500, with two value ranges, R01000 and R10000.
>
> Everything's pure Python, timed with `time.perf_counter`. We added skip thresholds to avoid out-of-memory — for example, brute force is only run for n ≤ 25. And we **cross-check**: every exact algorithm must produce the same value on every instance, automatically flagged if not."

**Cue:** click → slide 13. Hand-off to **Zuhair**.

---

## SLIDE 13 — Results: Runtime vs n (Zuhair, 0:45)

> "This is the runtime versus problem size, log-log scale.
>
> The red line — **brute force** — climbs almost vertically and disappears off the chart at n = 25. That's the 2ⁿ wall.
>
> The three middle lines — memoization, tabulation, space-optimised — track each other closely; they're all O(nW) and grow linearly in n at fixed W. **Tabulation consistently sits a bit below the others**, even though they share the same complexity. That's a discrepancy worth pointing out: in practice it wins because it has no recursion overhead and better cache locality.
>
> Greedy is essentially flat — O(n log n), barely visible at the bottom — and FPTAS sits between greedy and DP."

**Cue:** click → slide 14. Hand-off to **Raahin**.

---

## SLIDE 14 — Results: Approximation Quality (Raahin, 0:45)

> "Now the approximation side. Each box plot is the ratio of the approximation result to the optimal value, by instance category.
>
> Greedy is excellent — typically 95-percent-plus — on uncorrelated and subset-sum instances. But notice the drop on the **strongly correlated** categories. The reason is structural: when values track weights, every item has a similar value-to-weight ratio, so the greedy ordering becomes meaningless and the heuristic loses traction.
>
> FPTAS at ε = 0.25 **never violates its 75% floor** on any instance — and is usually well above 95%. The take-away: both algorithms stay within their theoretical guarantees, but their *empirical* quality depends heavily on the input structure."

**Cue:** click → slide 15. Hand-off to **Anas**.

---

## SLIDE 15 — Conclusion (Anas, 0:30)

> "So our conclusion is: there is no universally best algorithm — only a *recipe* for matching algorithm to constraint.
>
> For tiny n, brute force as an oracle. Need the item set? Tabulation. Memory-bound with huge W? Space-optimised. Need raw speed? Greedy, since it's W-independent. Need a provable bound with a knob? FPTAS.
>
> The real lesson of this project is that empirical structure — correlation, the magnitude of W, the size of n — determines the winning algorithm. The art of algorithm selection is matching well-understood trade-offs to the constraints that actually matter for your problem.
>
> Thank you — we'd be happy to take any questions."

**Cue:** thank-you screen, take Q&A.

---

## Tips for delivery

- **Total target: 9 minutes**. Aim to land between 8:30 and 9:30 in rehearsal.
- Each speaker should rehearse their slides aloud at least twice. Time yourself — most overruns happen when describing complexity (slide 11) and reading the conclusion (slide 15).
- Hand-offs: pause briefly when transitioning between speakers and make eye contact. Don't say "now Zuhair will continue" — just stop, the next person starts.
- If running long, the first thing to trim is examples on slides 5, 6, 7, 8 — the right-hand "output" boxes. The slide stays informative without you reading the numbers aloud.
- If asked about something not on a slide:
  - **Why didn't you include category 06?** — its W is too large; the DP table would exceed memory.
  - **Why is FPTAS slower than DP for small W?** — the scaled DP has overhead from the division/floor and a profit-indexed table, which is bigger than n × W for small W.
  - **Why does greedy do badly on strongly correlated?** — value/weight ratios are almost identical, so the sort order is essentially random.
