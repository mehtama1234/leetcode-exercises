# 881. Boats to Save People

**Pattern:** Greedy (sort, then pair the ends — with a swap argument)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/boats-to-save-people/

## The problem in plain words

You have a crowd of people, each with a weight. Every boat holds **at most two
people** and at most `limit` total weight. Use as few boats as possible to carry
everyone across. Return the boat count.

```diagram
   people = [3, 2, 2, 1]   limit = 3

   sorted:  1   2   2   3
   boats:  (1)      (2+? no) each heavy person needs their own boat here
           3 -> alone,  2 -> alone,  2+1 -> together
           answer: 3 boats
```

## Why this matters

Stripped down, this is **packing items into the fewest containers** without going
over a weight cap. The two-per-boat case has a clean greedy answer, but the move is
general: sort by size, and pair the heaviest thing with the heaviest thing that
still fits beside it.

This is real infrastructure work. Cloud schedulers pack VMs onto the fewest hosts
under CPU and RAM caps. Shipping loads pallets into the fewest trucks. Memory
allocators pack allocations into fixed blocks. Ad servers bundle payloads under a
byte budget. Packing tighter means fewer machines and lower cost.

What you buy is a fast, provably-best answer: a sort plus one sweep, about
n·log n work, instead of searching through exponentially many pairings.

## Start from the obvious

The honest first thought: pair people up. Each boat holds two, so if everyone paired
you would need n/2 boats. Two people share a boat when their weights sum to at most
`limit`. So brute force is "find the best set of pairs":

```
best = infinity
for each valid way to pair people (weight <= limit each pair):
    boats = (#pairs) + (#people left alone)
    best = min(best, boats)
```

That is a matching problem over all subsets — exponential, hopeless for real input.
It is correct, but it makes you ask: does the pairing really need a search, or is
there one obviously-right way to pair?

## Find the waste

The brute force sweats over *which* light person to seat with *which* heavy person,
as if the choice matters. It (almost) does not. Fix your eyes on the single
**heaviest** person, `H`. `H` is going on a boat no matter what — nothing lets you
skip them. The only question is who, if anyone, rides along.

The best candidate to seat next to `H` is the **lightest** person, `L`:

- If `L` does not even fit with `H` (`L + H > limit`), then nobody fits with `H`
  (everyone else is heavier), so `H` sails alone. No choice.
- If `L` does fit, pairing `H` with `L` is never worse than pairing `H` with some
  heavier `M`. Whoever `M` is, `M >= L`, so `M` still fits somewhere else that `L`
  could have filled. You can always swap `L` in beside `H` without breaking a boat.

```diagram
   suppose an "optimal" plan seats H with a middle person M, and L elsewhere:

        boat:  H + M          boat:  L + (someone)
                  ^                   ^
   swap L and M:  H + L (fits, L<=M)  M + (someone)  (M<=whoever held M before? fits)
   ----------------------------------------------------------------
   same number of boats, but now H is paired with L.  So grabbing H+L costs nothing.
```

That is a **swap argument** (any best plan can be rewritten to pair `H` with `L`).
So never search — sort everyone and repeatedly settle the current heaviest against
the current lightest.

## The insight

Sort the weights. One pointer at the light end, one at the heavy end.

```
left, right = 0, n-1
while left <= right:
    if people[left] + people[right] <= limit:
        left += 1        # lightest rides with the heaviest
    right -= 1           # the heaviest boards either way
    boats += 1
```

A worked trace:

```diagram
   people sorted = [1, 2, 2, 3]   limit = 3
   L=0                   R=3

   step1  1 + 3 = 4 > 3   -> 3 sails alone   R=2  boats=1
   step2  1 + 2 = 3 <=3   -> pair 1 and 2    L=1 R=1  boats=2
   step3  L==R (the lone 2)  -> 2 sails alone  R=0  boats=3
                                              answer: 3
```

Each loop commits exactly one boat. The heaviest remaining person always boards it;
the lightest joins only if there is room.

**Why not the opposite greedy?** If you paired the two heaviest each time, they would
usually overflow the limit, wasting the second seat — and then every light person
you skipped still needs their own boat, so you end with more boats. Pairing
heavy-with-light is what fills second seats.

## Complexity

- **Time: about n·log n.** The sort dominates. The two-pointer sweep after it is one
  pass — each pointer moves inward and they meet once.
- **Extra memory: a fixed amount** beyond the sort (Python's `list.sort()` is in
  place — sorts the list itself without a copy).

## Pitfalls

- **Forgetting boats hold at most two.** The heavy pointer moves one step per boat
  precisely because no third person can board.
- **Using `<` instead of `<=`** on the loop bound. With `left <= right`, when both
  pointers land on the *same* person that lone person still gets a boat; `<` would
  drop them.
- **Trying to pack more than one light person with a heavy one.** The two-seat cap
  forbids it — the check is only ever `people[left] + people[right]`.
- **Not sorting first.** The whole argument rests on "heaviest" and "lightest" being
  at the ends.

## Transfer

The reusable move is **sort, then greedily settle the most-constrained item against
its best partner, justified by a swap argument.** Once you see that the extreme
element's fate is forced and its best partner is the opposite extreme, a two-pointer
sweep replaces a search. Siblings:
[Two Sum II / 167](../../03-two-pointers/0167-two-sum-ii-input-array-is-sorted/)
(sorted two-pointer convergence),
[Assign Cookies / 455](https://leetcode.com/problems/assign-cookies/) (sort both
sides, match smallest-fits-smallest).
