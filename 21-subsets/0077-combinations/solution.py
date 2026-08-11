"""77. Combinations — https://leetcode.com/problems/combinations/

Return every way to choose k numbers from 1..n, ignoring order. For n=4, k=2 the
answer has C(4,2) = 6 combinations.

Order doesn't matter, so we only ever move forward through the numbers. The fixed
size k lets us prune branches that can't possibly be completed.
"""
from typing import List


def combine(n: int, k: int) -> List[List[int]]:
    """Backtracking over a forward-only index, pruned by remaining need. O(k*C(n,k)).

    Because combinations ignore order, we fix an order for ourselves — always pick
    the next number larger than the last — which visits each combination once. The
    prune: if the numbers left to consider (n - start + 1) are fewer than the slots
    still to fill (k - len(path)), this branch can never reach size k, so we stop
    early instead of recursing into a dead end.
    """
    result: List[List[int]] = []
    path: List[int] = []

    def backtrack(start: int) -> None:
        if len(path) == k:
            result.append(path[:])
            return
        need = k - len(path)            # numbers still to place
        # Only start values that leave enough room to finish are worth trying.
        last_ok = n - need + 1
        for i in range(start, last_ok + 1):
            path.append(i)              # choose
            backtrack(i + 1)            # explore: strictly larger numbers only
            path.pop()                  # un-choose

    backtrack(1)
    return result


def _key(lists: List[List[int]]) -> set:
    return {tuple(s) for s in lists}


def _test() -> None:
    import math
    cases = [
        ((4, 2),
         [[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]),
        ((1, 1), [[1]]),
        ((3, 3), [[1, 2, 3]]),          # edge: k == n -> exactly one combination
        ((5, 1), [[1], [2], [3], [4], [5]]),  # edge: k == 1
    ]
    for (n, k), expected in cases:
        got = combine(n, k)
        assert len(got) == math.comb(n, k), (n, k, len(got))
        assert _key(got) == _key(expected), (n, k, got)
        # every combination is strictly increasing (our canonical order)
        assert all(list(c) == sorted(c) for c in got), (n, k, "not increasing")
    print("combine: all cases passed")


if __name__ == "__main__":
    _test()
