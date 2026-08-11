# 202. Happy Number

**Pattern:** Cycle detection (a set, or two pointers at different speeds)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/happy-number/

## The problem in plain words

Take a number. Replace it with the sum of the squares of its digits. Repeat. If
you ever land on `1`, the number is "happy." If you loop forever without hitting
`1`, it isn't. Return whether the number is happy.

```diagram
   19  ->  1^2 + 9^2 = 1 + 81 = 82
   82  ->  8^2 + 2^2 = 64 + 4 = 68
   68  ->  6^2 + 8^2 = 36 + 64 = 100
   100 ->  1^2 + 0^2 + 0^2 = 1        reached 1  ->  happy!
```

## Why this matters

The number-crunching part is a warm-up. The real question is hidden: this process
either reaches `1` or *runs forever*. But "forever" can't mean forever producing
new numbers — the digit-square-sum of anything quickly falls below about 810 and
stays there. So a value must eventually repeat. The problem is really: **does this
sequence enter a loop, and can you tell before you've gone around it?**

Detecting whether a walk revisits a state is a core problem. A garbage collector
must notice cycles of references. A build system must catch circular dependencies.
A network router must spot routing loops. The two techniques here — remember every
state, or race two pointers — are the two standard answers, and they trade memory
against cleverness.

## Start from the obvious

Keep a set of every number you've seen. Each step, if the new number is `1` you're
happy; if it's already in the set, you've looped and you're not.

```diagram
   n = 2      seen = { }

   2   not 1, not seen  -> add 2       seen = {2}
   4   not 1, not seen  -> add 4       seen = {2,4}
   16  not 1, not seen  -> add 16      seen = {2,4,16}
   37  ...              -> add 37
   58 -> 89 -> 145 -> 42 -> 20 -> 4    4 is already in seen!
                                       ^ loop found  ->  NOT happy
```

This is correct and clear. The one cost: the set can grow to hold every distinct
number in the chain. That's fine here (the range is bounded), but it raises the
natural question — can we detect the loop *without* remembering everything?

## The insight

Yes — race two pointers through the sequence at different speeds. A slow pointer
takes one step at a time; a fast pointer takes two. If the sequence funnels into a
loop, the fast one is going around it faster and will eventually catch the slow one
from behind — they'll land on the same value. If instead the sequence reaches `1`,
the fast pointer gets there first.

```diagram
   step the sequence f(n) = square-digit-sum

   slow: one step      fast: two steps

           slow          fast
   start:   n            f(n)
   step1:   f(n)         f(f(f(n)))
   step2:   f(f(n))      ...

   if they ever meet  ->  there's a cycle  ->  not happy
   if fast reaches 1  ->  happy
```

The reason this works: think of the sequence as a shape like the letter rho — a
tail that leads into a circle. Once both pointers are on the circle, the fast one
closes the gap by one position each step, so it's guaranteed to overtake the slow
one. No set needed; just two running values.

```diagram
   the sequence has a "rho" shape:

        start -> o -> o -> o
                          |
                          v
                    o <---+  <- loop
                    |     ^
                    v     |
                    o --> o

   fast laps slow inside the loop; they collide
```

## Complexity

- **Time: about constant** in practice — the sequence provably drops into a small
  bounded range fast, so the number of steps to reach `1` or to loop is small.
- **Extra memory:** the set version holds up to `k` seen values; the two-pointer
  version uses **constant** memory — just `slow` and `fast`.

## Pitfalls

- Assuming an unhappy number runs off to infinity. It can't — the values stay
  bounded, so a repeat is guaranteed, which is what makes cycle detection valid.
- With two pointers, advancing them by the wrong amounts. Slow moves one hop, fast
  moves two hops per iteration.
- Forgetting that `1` maps to `1` (a fixed point) — reaching it is the happy exit,
  not a loop to reject.

## Transfer

The reusable move is **model a repeating process as a walk, then detect a cycle —
either by remembering states in a set or by racing two pointers.** The two-pointer
version is Floyd's cycle detection, the exact trick used in
[Linked List Cycle / 141](https://leetcode.com/problems/linked-list-cycle/) and
[Find the Duplicate Number / 287](https://leetcode.com/problems/find-the-duplicate-number/),
where the "next step" is a pointer instead of the digit-square-sum here.
