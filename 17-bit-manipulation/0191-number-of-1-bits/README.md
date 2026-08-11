# 191. Number of 1 Bits

**Pattern:** Bit manipulation (clear-the-lowest-bit trick)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/number-of-1-bits/

## The problem in plain words

Take a number, write it in binary, and count how many of its bits are `1`. That
count has a name: the *Hamming weight*.

Example: `11` in binary is `1011`, which has three `1`s, so the answer is `3`.

## Start from the obvious

Look at the bottom bit, count it, then slide everything down one position so the
next bit becomes the bottom bit. Repeat until nothing is left.

```
count = 0
while n:
    count += n & 1   # is the lowest bit a 1?
    n >>= 1          # shift the next bit into position
```

Walking `n = 1011`:

```
1011  & 1 = 1   count 1,  shift ->  101
 101  & 1 = 1   count 2,  shift ->   10
  10  & 1 = 0   count 2,  shift ->    1
   1  & 1 = 1   count 3,  shift ->    0   done
```

Correct. But notice: it takes one step per *bit position*. A 32-bit number
always costs 32 iterations, even if only one bit is set.

## Find the waste

Most of those 32 steps hit a `0` bit and do nothing but shift. If a number is
`1000...0001` (two set bits at the ends), we still grind through all 32 positions
to find the two ones. We're paying for the width of the number, not for the work
that matters — the number of `1`s.

## The insight

There's a single operation that deletes exactly the lowest set bit:

```
n & (n - 1)
```

Why it works: subtracting `1` flips the lowest `1` to `0` and turns every `0`
below it into `1`. AND-ing that back with the original keeps every higher bit
unchanged and clears that whole bottom run — net effect, the lowest `1`
disappears:

```
n     = 1100
n - 1 = 1011
n&n-1 = 1000   (lowest set bit gone)
```

So loop `n &= n - 1` and count how many times you can do it before `n` hits `0`.
Each step removes one `1`, so the loop runs exactly as many times as there are
set bits:

```
n = 1100  -> 1000  (count 1)
          -> 0000  (count 2)   answer 2
```

For a sparse number that's a handful of steps instead of a full 32.

## Complexity

- **Scan version:** `O(w)` where `w` is the bit width (32 here) — fixed cost.
- **Kernighan version:** `O(k)` where `k` is the number of set bits — never more
  than `w`, often far fewer.
- **Space:** `O(1)` for both.

## Pitfalls

- Using an *arithmetic* right shift on a negative number in languages where the
  sign bit gets copied in — you'd loop forever. Use unsigned/logical shift, or
  the `n & (n - 1)` form which avoids shifting entirely.
- In Python, integers are unbounded, so treat the input as the 32-bit unsigned
  value it represents; the tests use exact 32-bit patterns like `0xFFFFFFFF`.

## Transfer

`n & (n - 1)` is a workhorse: it powers the O(n) DP in
[Counting Bits / 338](../0338-counting-bits/) and the classic power-of-two check
`n > 0 and (n & (n - 1)) == 0`. Whenever you want to touch set bits one at a time
rather than scan every position, reach for it.
