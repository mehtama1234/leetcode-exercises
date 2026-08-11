"""78. Subsets — https://leetcode.com/problems/subsets/

Given a list of *distinct* numbers, return every possible subset (the power set),
including the empty set and the full set, in any order.

This is the cleanest possible backtracking template: at each element you make one
binary decision — take it or leave it — and the tree of those decisions has one
leaf per subset.
"""
from typing import List


def subsets(nums: List[int]) -> List[List[int]]:
    """Backtracking. O(n * 2^n) time, O(n) extra space (recursion + path).

    The decision tree: at index `i` you branch two ways — include nums[i] in the
    current path, or don't — then recurse to i+1. When i reaches the end, the path
    is one complete subset, so we record a *copy* of it. The three-line template
    is visible here: choose (append), explore (recurse), un-choose (pop) so the
    path is clean for the sibling branch.
    """
    n = len(nums)
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(i: int) -> None:
        if i == n:
            result.append(path[:])  # copy — path keeps mutating after this
            return
        # Branch 1: leave nums[i] out.
        backtrack(i + 1)
        # Branch 2: take nums[i].
        path.append(nums[i])        # choose
        backtrack(i + 1)            # explore
        path.pop()                  # un-choose

    backtrack(0)
    return result


def subsets_grow(nums: List[int]) -> List[List[int]]:
    """Same power set via the "grow at each element" view. O(n * 2^n).

    An equivalent, often-seen formulation: start with just the empty subset, and
    for each new number, append it to a copy of *every* subset seen so far. This
    doubles the count each step — the same 2^n, arrived at without recursion. Kept
    to show the two views are the same object.
    """
    result: List[List[int]] = [[]]
    for x in nums:
        result += [subset + [x] for subset in result]
    return result


def _key(lists: List[List[int]]) -> set:
    """Order-independent comparison key: a set of tuples."""
    return {tuple(s) for s in lists}


def _test() -> None:
    cases = [
        ([1, 2, 3], [[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]),
        ([0], [[], [0]]),
        ([], [[]]),                      # edge: empty input -> just the empty set
        ([5, 6], [[], [5], [6], [5, 6]]),
    ]
    for nums, expected in cases:
        got = subsets(nums)
        assert len(got) == 2 ** len(nums), (nums, len(got))
        assert _key(got) == _key(expected), (nums, got)
        assert _key(subsets_grow(nums)) == _key(expected), (nums, "grow")
    print("subsets: all cases passed")


if __name__ == "__main__":
    _test()
