# 11. Container With Most Water

**Pattern:** Two pointers (greedy shrink from both ends)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/container-with-most-water/

## The problem in plain words

Each number is the height of a vertical wall standing at that position. Pick two
walls; they form a container, and the water it holds is its **width** (distance
between the walls) times the **height of the shorter wall** (water spills over the
lower one). Find the largest amount of water any pair can hold.

For two walls `i` and `j`, area is `(j - i) * min(height[i], height[j])`.

## Start from the obvious

Try every pair and keep the best:

```
best = 0
for i:
  for j after i:
    best = max(best, (j - i) * min(height[i], height[j]))
```

`O(n^2)`, correct, done. But it dutifully checks pairs that obviously can't win.
Understanding *which* pairs are hopeless is what collapses this to linear time.

## Find the waste

Two things fight to make the area big: **width** and **the shorter wall's height**.
Start with the maximum possible width — the leftmost and rightmost walls. From
here, any other pair is narrower, because the only way to move is inward.

So width can only shrink. The single question that matters at each step is: which
pointer do we move to have a shot at a *taller* short wall?

Look at the current pair and consider the **shorter** wall. It is the one capping
the area. If we keep it and move the taller wall inward instead:

- width goes down (we moved inward), and
- the height is *still* limited by that same short wall.

That's strictly worse — smaller width, same height. So there is no point pairing
the shorter wall with anything closer; every such container is beaten by the one
we already measured. We can safely discard the shorter wall and move its pointer
inward, hoping the next wall is taller.

## The insight

Two pointers at the ends. Measure the area, then **move whichever wall is shorter**
one step inward. Repeat until they meet, tracking the best area seen.

```
left, right = 0, len(height) - 1
best = 0
while left < right:
    best = max(best, (right - left) * min(height[left], height[right]))
    if height[left] < height[right]: left += 1
    else: right -= 1
```

Because each move provably eliminates only containers that can't beat the current
best, one inward sweep is enough. No pair worth checking is skipped.

## Complexity

- **Time:** `O(n)` — the two pointers only move inward and meet after `n` steps.
- **Space:** `O(1)` — two indices and a running max.

## Pitfalls

- **Moving the taller wall** (or always moving one fixed side): that can step past
  the real answer. You must move the *shorter* one.
- Height is `min(left, right)`, not the sum or the max — water pours over the
  lower wall.
- Ties (`height[left] == height[right]`): moving either side is fine; the pair
  you'd get by keeping one and moving the other is no taller and strictly
  narrower.
- Off-by-one on width — it's `right - left` (indices), not `right - left + 1`.

## Transfer

This is the "start at the widest/extreme configuration and greedily shrink the
provably-worse side" flavor of two pointers — different from the
[Two Sum II / 167](../0167-two-sum-ii-input-array-is-sorted/) sum-target sweep, but
the same converging-pointer skeleton. The key transferable habit is proving *why*
an end can be discarded, which also underlies harder greedy-pointer problems like
*Trapping Rain Water / 42*.
