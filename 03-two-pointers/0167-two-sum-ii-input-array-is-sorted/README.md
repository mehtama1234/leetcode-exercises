# 167. Two Sum II - Input Array Is Sorted

**Pattern:** Two pointers (converging on a sorted array)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

## The problem in plain words

Same goal as classic Two Sum — find the two numbers that add up to `target` and
return where they are — but with two twists: the array is **already sorted**, and
the answer must be **1-indexed** (the first element is position 1, not 0).

## Start from the obvious

Ignore the sorting and just test every pair, exactly like brute-force Two Sum:

```
for each i:
    for each j after i:
        if numbers[i] + numbers[j] == target: return [i+1, j+1]
```

`O(n^2)`, correct, and it works. But notice what it wastes: the problem went out
of its way to tell us the array is sorted, and this solution never uses that fact
at all. When a problem hands you a special structure, refusing to use it is the
waste.

## Find the waste

You could bring in a hash map like the original Two Sum and get `O(n)` time — but
that spends `O(n)` memory to rediscover partners the *sorting already orders for
us*. Sorted order gives something a hash map can't: **direction**. If you look at
the smallest and largest values together, their sum tells you which way to go.

Put `left` on the smallest number and `right` on the largest:

- Sum **too big**? Every pairing that uses the current `right` is at least this
  big (since `left` is already the smallest partner available), so `right` can't
  be in any answer. Move `right` left.
- Sum **too small**? By the mirror argument, the current `left` is too small to
  reach the target with any partner. Move `left` right.
- Sum **equal**? Found it.

## The insight

Each comparison lets us throw away one whole end value as impossible, so the two
pointers march toward each other and meet after at most `n` steps — one linear
pass, no extra memory.

```
left, right = 0, len(numbers) - 1
while left < right:
    s = numbers[left] + numbers[right]
    if s == target: return [left+1, right+1]
    elif s < target: left += 1
    else: right -= 1
```

The reasoning ("this end can't possibly be part of the answer, discard it") only
holds *because* the array is sorted. That's the whole point of the problem.

## Complexity

- **Time:** `O(n)` — the two pointers only ever move inward, so combined they take
  at most `n` steps.
- **Space:** `O(1)` — two indices, nothing allocated. This beats the hash-map Two
  Sum, which needs `O(n)` space.

## Pitfalls

- **Off-by-one on indexing:** the answer is 1-based. Return `[left+1, right+1]`,
  not `[left, right]`.
- Trying to reuse the exact hash-map Two Sum code — it works but misses the point
  and wastes memory the sorted structure makes unnecessary.
- Moving the wrong pointer (swapping the `<` and `>` branches) — remember: too
  big shrink from the right, too small grow from the left.
- Duplicates and negatives are fine here; the direction argument doesn't care.

## Transfer

The "converge two pointers from both ends of a sorted array, using the sum to
decide which side to shrink" move is the backbone of
[3Sum / 15](../0015-3sum/) (fix one number, two-pointer the rest) and
[Container With Most Water / 11](../0011-container-with-most-water/). Any time the
input is sorted and you're hunting for a pair (or a bounded sum), reach for two
converging pointers before a hash map.
