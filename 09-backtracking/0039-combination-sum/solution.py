"""39. Combination Sum — https://leetcode.com/problems/combination-sum/

Given distinct positive numbers `candidates` and a `target`, return every unique
combination whose numbers sum to `target`. Each candidate may be reused any
number of times. Two combinations are the same if they use the same multiset of
numbers, so order inside a combination does not matter.
"""
from typing import List


def combination_sum(candidates: List[int], target: int) -> List[List[int]]:
    """Backtracking over a non-decreasing "start index" so combinations are unique.

    The whole problem is: build a running list, and at every step decide "which
    number do I add next?". If we let ourselves pick freely from all candidates
    at every step, we'd generate the same multiset in many orders — [2,3] and
    [3,2] — and count them as different.

    The fix is an ordering rule: once we commit to starting our next pick at
    index `start`, we never look back before `start`. That forces every
    combination we emit to be non-decreasing by index, which makes each multiset
    appear exactly once. Because reuse is allowed, the recursive call keeps the
    SAME `start` (we may pick the current number again), not `start + 1`.

    We also carry `remaining = target - chosen so far`. When it hits 0 we found a
    combination; if it drops below the current candidate we can stop early once
    candidates are sorted, because everything further is only larger.
    """
    candidates.sort()  # lets us prune: once a candidate exceeds `remaining`, stop
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int, remaining: int) -> None:
        if remaining == 0:
            result.append(path.copy())  # copy: path is mutated after this returns
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break  # sorted, so every later candidate is too big as well
            path.append(c)
            backtrack(i, remaining - c)  # i, not i+1 → candidate i may repeat
            path.pop()  # undo the choice before trying the next candidate

    backtrack(0, target)
    return result


def _normalize(combos: List[List[int]]) -> set:
    """Order-independent view of the answer for stable comparison in tests."""
    return {tuple(sorted(c)) for c in combos}


def _test() -> None:
    cases = [
        (([2, 3, 6, 7], 7), [[2, 2, 3], [7]]),
        (([2, 3, 5], 8), [[2, 2, 2, 2], [2, 3, 3], [3, 5]]),
        (([2], 1), []),          # nothing sums to 1
        (([2], 4), [[2, 2]]),    # single candidate reused
        (([7, 3, 2], 18), None), # unsorted input must still work; check count below
    ]
    for (candidates, target), expected in cases:
        got = combination_sum(candidates, target)
        # every combination must actually sum to target
        for combo in got:
            assert sum(combo) == target, (candidates, target, combo)
        # no duplicate multisets
        assert len(_normalize(got)) == len(got), (candidates, target, got)
        if expected is not None:
            assert _normalize(got) == _normalize(expected), (candidates, target, got)
    print("combination_sum: all cases passed")


if __name__ == "__main__":
    _test()
