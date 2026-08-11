"""46. Permutations — https://leetcode.com/problems/permutations/

Given a list of *distinct* numbers, return every ordering of all of them. For n
numbers there are n! permutations.

Unlike subsets, order matters and every element must be used. The decision at
each step is "which unused number goes next?", so we track what's still available.
"""
from typing import List


def permute(nums: List[int]) -> List[List[int]]:
    """Backtracking with a used[] mask. O(n * n!) time, O(n) extra space.

    The decision tree has depth n. At each depth we try every number that hasn't
    been placed yet (that's what `used` records). When the path reaches length n,
    every number is placed, so it's one complete permutation. The template is the
    same choose / explore / un-choose — the only twist versus subsets is that we
    must remember which items are still available.
    """
    n = len(nums)
    result: List[List[int]] = []
    path: List[int] = []
    used = [False] * n

    def backtrack() -> None:
        if len(path) == n:
            result.append(path[:])      # copy — path keeps mutating
            return
        for i in range(n):
            if used[i]:
                continue                # already placed this number
            used[i] = True              # choose
            path.append(nums[i])
            backtrack()                 # explore
            path.pop()                  # un-choose
            used[i] = False

    backtrack()
    return result


def _key(lists: List[List[int]]) -> set:
    """Order-independent key. Permutations keep their internal order (it's the
    whole point), so we tuple each one but treat the outer list as a set."""
    return {tuple(s) for s in lists}


def _test() -> None:
    import math
    cases = [
        ([1, 2, 3],
         [[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]),
        ([0, 1], [[0, 1], [1, 0]]),
        ([7], [[7]]),                   # edge: single element
        ([], [[]]),                     # edge: empty -> one permutation (empty)
    ]
    for nums, expected in cases:
        got = permute(nums)
        assert len(got) == math.factorial(len(nums)), (nums, len(got))
        assert _key(got) == _key(expected), (nums, got)
    print("permute: all cases passed")


if __name__ == "__main__":
    _test()
