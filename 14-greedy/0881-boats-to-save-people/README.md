# 881. Boats to Save People

**Pattern:** Greedy (sort + two pointers, exchange argument)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/boats-to-save-people/

## The problem in plain words

You have a crowd of people, each with a weight. Every boat holds **at most two
people** and can carry at most `limit` total weight. Use as few boats as
possible to get everyone across. Return that boat count.

## Why this matters

Stripped down, this is **bin packing with a capacity limit** — fit items into the
fewest containers without exceeding a weight or size cap. The special case here
(two items per boat) has a clean greedy answer, but the underlying operation is
universal: sort by size and pair the largest with the largest thing that still
fits, proven optimal by an exchange argument.

This is real infrastructure work. Cloud schedulers pack VMs or containers onto
the fewest physical hosts under CPU/RAM limits. Shipping and logistics load
pallets into trucks or trailers to minimize trips. Memory allocators and disk
tools pack allocations into fixed blocks. Ad servers and CDNs bundle payloads
under a byte budget. Even cutting-stock problems (slicing pipe or fabric with
minimal waste) are the same shape.

What we buy is a fast, near-optimal answer: a sort plus a single two-pointer
sweep — `O(n log n)` — instead of searching exponentially many pairings. In the
scheduling world, packing tighter directly means fewer machines and lower cost.

## Start from the obvious

The honest first thought is: try to pair people up. Each boat holds two, so if
we could pair everyone we'd need `n/2` boats. When can two people share a boat?
When their weights sum to `<= limit`. So brute force is "find the best set of
pairs":

```
# try every way to match people into pairs of weight <= limit,
# keep the matching that leaves the fewest people unpaired
best = infinity
for each valid pairing of people:
    boats = (#pairs) + (#people left alone)
    best = min(best, boats)
```

That's a matching problem over all subsets — exponential. It's correct but
hopeless for real input. The question is whether the pairing really needs a
search, or whether there's one obviously-right way to pair.

## Find the waste

The brute force explores *which* light person to pair with *which* heavy person,
as if that choice mattered. It (almost) doesn't. Fix your attention on the single
**heaviest** person, `H`. `H` is going on a boat no matter what — nothing lets us
skip them. The only decision is who, if anyone, rides with `H`.

Here's the key: the best candidate to seat next to `H` is the **lightest** person
`L`. Reason it through:

- If `L` doesn't even fit with `H` (`L + H > limit`), then nobody fits with `H`
  (everyone is heavier than `L`), so `H` sails alone. No choice to make.
- If `L` does fit, pairing `H` with `L` is never worse than pairing `H` with some
  heavier person `M`. Whoever `M` is, `M >= L`, so `M` fits beside the now-freed
  spot that `L` would have taken. You can always swap `L` in for `M` next to `H`
  without breaking any boat. This is an **exchange argument**: any optimal
  solution can be rewritten to pair `H` with `L`, so grabbing that pairing costs
  nothing.

So we never need to search. Sort everyone, and repeatedly resolve the current
heaviest person against the current lightest.

## The insight

Sort the weights. Put one pointer at the light end, one at the heavy end.

```
left, right = 0, n-1
while left <= right:
    if people[left] + people[right] <= limit:
        left += 1      # lightest rides along with the heaviest
    right -= 1         # the heaviest is seated either way
    boats += 1
```

Each loop iteration commits exactly one boat. The heaviest remaining person
always boards it; the lightest remaining person joins only if there's room.

**Why not the opposite greedy?** If you instead paired the two heaviest people
each time, you'd usually fail to seat two (heavy + heavy overflows the limit),
burning the second seat — and then every light person you skipped still needs
their own boat. You'd end up with more boats. Pairing heavy-with-light is what
fills second seats.

## Complexity

- **Time:** `O(n log n)` — dominated by the sort. The two-pointer sweep after it
  is a single `O(n)` pass (each pointer moves inward, they meet once).
- **Space:** `O(1)` extra beyond the sort (`O(n)` if the sort isn't in place; in
  Python `list.sort()` is in place).

## Pitfalls

- **Forgetting boats hold at most two.** The heavy pointer always moves one step
  per boat precisely because a boat can't hold a third person.
- **Using `<` instead of `<=`** on the loop bound: with `left <= right`, when the
  two pointers land on the *same* person that lone person still gets a boat. Using
  `<` would drop them.
- **Trying to pack more than one light person with a heavy one.** The two-seat cap
  forbids it; the check is only ever `people[left] + people[right]`.
- **Not sorting first.** The whole argument rests on "heaviest" and "lightest"
  being at the ends.

## Transfer

The reusable move is: **sort, then greedily resolve the most-constrained item
against its cheapest partner, justified by an exchange argument.** Once you see
that the extreme element's fate is forced and its best partner is the opposite
extreme, a two-pointer sweep replaces a search. Siblings:
[Two Sum II / 167](../../03-two-pointers/0167-two-sum-ii-input-array-is-sorted/)
(sorted two-pointer convergence),
[Assign Cookies / 455](https://leetcode.com/problems/assign-cookies/) (sort both
sides, greedily match smallest-fits-smallest), and container/interval problems
where sorting exposes a forced choice at an extreme.
