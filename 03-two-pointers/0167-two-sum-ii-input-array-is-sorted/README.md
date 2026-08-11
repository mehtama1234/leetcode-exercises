# 167. Two Sum II - Input Array Is Sorted

**Pattern:** Two pointers (let sorted order point the way)
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/

## The problem in plain words

Same goal as the classic Two Sum — find the two numbers that add up to `target`
and return where they are — with two twists: the array is **already sorted**, and
the answer is **1-indexed** (the first element is position 1, not 0).

```diagram
   position:  1    2    3    4
   numbers: [ 2 ,  7 , 11 , 15 ]     target = 9
              └────┘
              2 + 7 = 9   ->  answer: [1, 2]
```

## Why this matters

The real problem is: *use the fact that the data is sorted to find a pair hitting
a target — without spending extra memory.* The one reusable move is reading the
sum of the two current ends as a signal that tells you, with no guessing, which
end to throw away next. Every comparison kills a whole candidate, so you finish in
one pass.

That "the data is already ordered, so let direction guide the search" idea is how
real systems dodge brute force. Databases merge-join two sorted streams by
advancing whichever side is behind — the same converge-by-comparison move. Range
queries over sorted price ladders or time-series use the two-pointer shrink.

What you're solving for is space. A hash-map Two Sum is fast but spends memory to
rebuild an ordering the input already gave you. Two pointers stay fast at constant
memory. When sortedness is handed to you, refusing to use it is the real waste.

## Start from the obvious

Ignore the sorting and test every pair, exactly like brute-force Two Sum.

```diagram
   for each i:
     for each j after i:
       if numbers[i] + numbers[j] == target: return [i+1, j+1]
```

Correct, and it works. But notice what it throws away: the problem went out of its
way to say the array is sorted, and this never touches that fact. About n × n
steps for something a single pass can do.

## Find the waste

You could pull in a hash map like the original Two Sum and drop to one pass — but
that spends memory to rediscover partners the *sorting already orders for you*.
Sorted order gives something a hash map can't: **direction**. Put `left` on the
smallest number and `right` on the largest, and their sum tells you which way to
step.

```diagram
   numbers: [ 2 , 3 , 4 ]   target = 6
              L       R      sum = 2+4 = 6  == target  -> found [1, 3]

   why direction works:
     sum too BIG  -> right is too large for ANY partner (left is already smallest)
                     so drop right:  R--
     sum too SMALL-> left is too small to reach target with ANY partner
                     so drop left:   L++
```

## The insight

Each comparison lets you throw away one whole end as impossible, so the pointers
march toward each other and meet after at most n steps — one pass, no extra memory.

```diagram
   numbers: [ 2 , 3 , 4 ]   target = 6
   L         R    sum=6  ==  ->  return [L+1, R+1] = [1, 3]

   numbers: [ 5 , 25 , 75 ]  target = 100
   L              R    sum=5+75=80  < 100  too small -> L++
        L         R    sum=25+75=100 ==    -> return [2, 3]
```

The reasoning ("this end can't be in any answer, drop it") only holds *because* the
array is sorted. That's the whole point of the problem.

## Complexity

- **Time: about n steps.** The two pointers only move inward, so combined they take
  at most n steps.
- **Extra memory: constant.** Two indices. This beats the hash-map Two Sum, which
  needs memory proportional to the list.

## Pitfalls

- **Off-by-one on indexing:** the answer is 1-based. Return `[left+1, right+1]`,
  not `[left, right]`.
- Reusing the hash-map Two Sum code — it works but misses the point and wastes
  memory the sorted order makes unnecessary.
- Moving the wrong pointer (swapping the branches): too big shrink from the right,
  too small grow from the left.
- Duplicates and negatives are fine; the direction argument doesn't care.

## Transfer

The "converge from both ends of a sorted array, using the sum to pick which side
to shrink" move is the backbone of [3Sum / 15](../0015-3sum/) (fix one number,
two-pointer the rest) and
[Container With Most Water / 11](../0011-container-with-most-water/). Any time the
input is sorted and you're hunting for a pair (or a bounded sum), reach for two
converging pointers before a hash map.
