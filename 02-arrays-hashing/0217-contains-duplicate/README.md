# 217. Contains Duplicate

**Pattern:** Hashing (remember what you've seen, then ask a yes/no question)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/contains-duplicate/

## The problem in plain words

You have a list of numbers. Answer one yes/no question: does any number show up
more than once?

```diagram
        index:   0    1    2    3
        nums:  [ 1 ,  2 ,  3 ,  1 ]
                 ^              ^
                 the two 1s are a duplicate  ->  answer: true
```

## Why this matters

Strip the story away and the real question is small: *as numbers go by one at a
time, can I tell whether the one in front of me has already gone by?* You are not
hunting through the list. You are keeping a memory of what you've passed and
asking your memory a single yes/no question.

That move runs real systems. A database with a UNIQUE column is asking "have I
already stored this value?" on every insert. Throwing out repeated log lines,
emails, or crawled web addresses before you process them is the same check.
Catching a form that got submitted twice, or a request that got replayed, is a
seen-before test. When memory is tight and an occasional wrong "yes" is
acceptable, systems swap the exact set for a Bloom filter — a tiny table that
still answers "probably seen / definitely not."

What you buy is a single walk with an early exit: the moment the first repeat
turns up you can stop, instead of scanning the rest of the list over and over.

## Start from the obvious

A duplicate means two different positions holding the same value. So compare
every position against every position after it.

```diagram
   nums = [1, 2, 3, 1]

   i=0 (1): 1==2? 1==3? 1==1?  YES at index 3  -> true
   i=1 (2): 2==3? 2==1?
   i=2 (3): 3==1?
            ^ for each i, we re-walk the whole rest of the list
```

This is correct and it's the honest first thought. But look at the shape of the
work: for every number you sweep the rest again. On a list of length n that is
about n × n steps — double the list and the work roughly quadruples. The waste
is the repeated sweeping.

## Find the waste

The inner loop keeps asking "is this same value sitting somewhere *later*?" But
you don't need to look ahead at all. You only need to remember what you've
*already passed*. The cheap question is:

```diagram
   standing on the second 1:
      slow way:  "does a 1 appear anywhere else?"  (search the list)
      fast way:  "have I already walked past a 1?"  (check my memory)
```

Answering "have I seen this value?" in one step is exactly what a hash set is
for. (A set is a bag that only knows whether a value is inside it.)

## The insight

Walk the list once, carrying a set of everything seen so far. At each number,
first ask the set if it's already there; only then add it.

```diagram
   nums = [1, 2, 3, 1]      seen = {}

   x=1   in seen? no    ->  add 1     seen = {1}
   x=2   in seen? no    ->  add 2     seen = {1,2}
   x=3   in seen? no    ->  add 3     seen = {1,2,3}
   x=1   in seen? YES!  ->  return true
                  ^
          the earlier 1 was remembered three steps ago
```

Checking *before* you add is what lets you stop the instant the first repeat
appears, instead of building the whole set first.

## Complexity

- **Time: about n steps.** One pass, and each set lookup or insert is a single
  step on average.
- **Extra memory: about n.** In the worst case (all values distinct) the set
  ends up holding the whole list.

A one-liner captures the same idea: `len(set(nums)) != len(nums)` — if squashing
duplicates shrinks the list, there were duplicates. It reads cleanly, but it
always builds the whole set even when the answer was decided on the second
element; the explicit loop can bail early.

## Pitfalls

- Sorting first (about n log n — roughly n steps times a small growing factor) is
  a valid way to save memory, but don't reach for it when you're allowed the set;
  it's slower here for no reason.
- Empty list and single element must return false — there's nothing to pair.
- Inserting before checking still works for *this* problem, but the "check first"
  habit matters in siblings where a number must not match itself.

## Transfer

The reusable move: **replace an inner search with a one-step "have I seen it?"
check backed by a set.** This is the base case the whole family builds on —
[Two Sum / 1](../0001-two-sum/) looks up the needed partner, and
[Longest Consecutive Sequence / 128](../0128-longest-consecutive-sequence/) asks
"is `x-1` present?". Any time a slow solution keeps re-scanning to ask "is this
value here?", reach for a set first.
