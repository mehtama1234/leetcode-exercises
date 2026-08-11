# 1. Two Sum

**Pattern:** Hashing (remember what you've seen so you never look twice)
**Difficulty:** Easy
**Link:** https://leetcode.com/problems/two-sum/

## The problem in plain words

You get a list of numbers and a target. Two of the numbers add up to the target.
Give back *where* those two sit — their positions, not the numbers.

```diagram
        index:   0    1    2    3
        nums:  [ 2 ,  7 , 11 , 15 ]     target = 9
                 └────┘
                 2 + 7 = 9   ->  answer: [0, 1]
```

## Why this matters

Strip the story away and one question is left: *as things go by one at a time,
can I instantly tell whether the piece that completes the current one has already
gone by?* You are not really searching. You are **remembering**, then asking a
yes/no question about your memory.

That single move runs real systems. When a database joins two tables on a shared
key, it puts one side into a lookup table and checks each row of the other side
against it — the same "have I seen the match?" question. Removing duplicate
events in a data pipeline, or pairing a payment to the invoice it settles, is the
same lookup wearing different clothes.

What the good version buys you is one walk through data you often cannot rewind,
and it swaps a slow "re-scan everything each time" for an instant check. As the
list grows, that is the line between a program that answers and one that hangs.

## Start from the obvious

The problem describes pairs, so try every pair. For each number, look at every
number after it and see if they add up.

```diagram
   i=0 (2): 2+7=9  found!            <- got lucky early here
   i=1 (7): 7+11, 7+15
   i=2 (11): 11+15
            ^ for each i, we re-walk the whole rest of the list
```

This works. But look at the shape of the work: for every number you sweep the
rest of the list again. On a list of length n that is about n × n steps. Double
the input and the work roughly quadruples. The waste is the repeated sweeping.

## Find the waste

Here is the thing the slow version keeps ignoring. When you stand on a number `x`,
its partner is not a mystery you have to hunt for. It is forced: the partner must
be `target - x`. There is exactly one value that works.

```diagram
   standing on x = 7,  target = 9
   partner MUST be  9 - 7 = 2      (nothing to search — it's decided)
   real question:  "have I already walked past a 2?"
```

So the job is not "find a matching number." It is "check whether one exact number
showed up earlier." Checking *did I already see this value?* in one step is the
whole reason hash maps exist.

## The insight

Walk the list once. Keep a map of every number you've passed and where it sat. At
each new number, first ask the map for its partner; only then file the number away.

```diagram
   target = 9        map = {}           (value -> index seen)

   i=0  x=2   need 9-2=7   7 in map? no    ->  file 2:  {2:0}
   i=1  x=7   need 9-7=2   2 in map? YES!   ->  answer [ map[2], 1 ] = [0, 1]
                                  ▲
                        the partner was remembered two steps ago
```

Checking *before* filing is what stops a number from pairing with itself, and it
handles a repeat like `[3, 3], target 6` correctly — the first `3` gets filed, the
second `3` finds it.

The big-picture idea: you spent a little memory to buy a lot of speed. Instead of
looking again and again, you wrote down what you saw so the answer is one glance
away. That trade — remember now, skip the re-search later — is everywhere in
computing.

## Complexity

- **Time: about n steps.** You touch each number once, and each map check is a
  single step on average.
- **Extra memory: about n.** In the worst case the map holds nearly the whole list
  before the answer appears.

## Pitfalls

- Returning the two **numbers** instead of their **positions**.
- Filing a number into the map *before* checking — then it can match itself.
- Assuming the list is sorted. It isn't. (Sorted is a different, pointer-based
  problem — see [Two Sum II / 167](../../03-two-pointers/0167-two-sum-ii-input-array-is-sorted/).)

## Transfer

The reusable move is: **replace an inner search with a one-step "have I seen it?"
check backed by a set or map.** The same move powers
[Contains Duplicate / 217](../0217-contains-duplicate/),
[Valid Anagram / 242](../0242-valid-anagram/), and
[Longest Consecutive Sequence / 128](../0128-longest-consecutive-sequence/).
Any time a slow solution keeps re-scanning to ask "is this value here?", reach for
a hash set or map first.
