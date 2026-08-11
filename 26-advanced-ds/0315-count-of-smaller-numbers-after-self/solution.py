"""315. Count of Smaller Numbers After Self — https://leetcode.com/problems/count-of-smaller-numbers-after-self/

For each element, count how many elements to its right are strictly smaller than
it. Return that list of counts (same length as the input).

This is "count inversions, per element." Three implementations sit side by side:
  * O(n^2) brute force — the honest definition, to anchor what we're speeding up.
  * A Binary Indexed Tree (Fenwick) over value-ranks — walk right-to-left and ask
    "how many smaller values have I already inserted?" in O(log n).
  * A merge sort that counts, during the merge, how many right-half elements slip
    in front of each left-half element.
"""
from typing import List


def countSmaller_brute(nums: List[int]) -> List[int]:
    """The definition, directly. O(n^2) time, O(n) space.

    For each i, scan everything to its right and tally the strictly smaller ones.
    Correct and obvious — and it re-scans the whole suffix for every element, which
    is exactly the repeated work the smarter methods remove.
    """
    n = len(nums)
    result = [0] * n
    for i in range(n):
        for j in range(i + 1, n):
            if nums[j] < nums[i]:
                result[i] += 1
    return result


class _BIT:
    """A Fenwick tree used as a frequency counter over value-ranks.

    Position `r` (1-indexed) counts how many times the value with rank r has been
    inserted. `add(r)` bumps that count; `prefix(r)` returns how many inserted
    values have rank <= r. Both are O(log n) via the lowest-set-bit walk:
      add:    i += i & -i   (climb to every block that covers i)
      prefix: i -= i & -i   (peel off blocks to sum ranks 1..i)
    We use it as a running "how many of value <= v have I seen so far?" oracle.
    """

    def __init__(self, size: int) -> None:
        self.tree = [0] * (size + 1)

    def add(self, i: int, delta: int = 1) -> None:
        while i < len(self.tree):
            self.tree[i] += delta
            i += i & (-i)

    def prefix(self, i: int) -> int:
        """Count of inserted values with rank in [1, i]."""
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)
        return s


def countSmaller(nums: List[int]) -> List[int]:
    """Fenwick / BIT over value-ranks. O(n log n) time, O(n) space.

    The core idea: process the array from RIGHT to LEFT. When we reach nums[i],
    every element already inserted into the BIT is one that lies to i's right. So
    "how many smaller values are to my right?" becomes "how many already-inserted
    values are strictly less than nums[i]?" — a prefix-count query.

    Values can be huge/negative, so we first *coordinate-compress*: map each distinct
    value to a small rank 1..m (sorted order). Then a query for "strictly less than
    nums[i]" is prefix(rank(nums[i]) - 1), and inserting nums[i] is add(rank).
    """
    n = len(nums)
    # Coordinate compression: sorted distinct values -> rank via binary search.
    sorted_vals = sorted(set(nums))
    rank = {v: i + 1 for i, v in enumerate(sorted_vals)}  # 1-indexed ranks

    bit = _BIT(len(sorted_vals))
    result = [0] * n
    for i in range(n - 1, -1, -1):
        r = rank[nums[i]]
        result[i] = bit.prefix(r - 1)   # how many seen-so-far values are strictly smaller
        bit.add(r)                      # now record nums[i] as "seen to the right"
    return result


def countSmaller_mergesort(nums: List[int]) -> List[int]:
    """Merge sort that counts inversions per element. O(n log n) time, O(n) space.

    We sort *indices* by their value and, during each merge, count how many
    right-half elements are smaller than a given left-half element — those are
    elements that were originally to its right yet are smaller, i.e. exactly what we
    want. `counts[idx]` accumulates across all the merges that idx participates in.
    """
    n = len(nums)
    counts = [0] * n
    indices = list(range(n))  # we sort these by nums[index], stably

    def sort(lo: int, hi: int) -> List[int]:
        if hi - lo <= 1:
            return indices[lo:hi]
        mid = (lo + hi) // 2
        left = sort(lo, mid)
        right = sort(mid, hi)
        merged: List[int] = []
        i = j = 0
        while i < len(left) or j < len(right):
            # Take from the left half when it's <= the right head. Everything already
            # pulled from the right (j of them) was smaller AND originally to the
            # right of left[i], so it contributes j to left[i]'s count.
            if j >= len(right) or (i < len(left) and nums[left[i]] <= nums[right[j]]):
                counts[left[i]] += j
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                j += 1
        indices[lo:hi] = merged
        return merged

    sort(0, n)
    return counts


def _test() -> None:
    cases = [
        ([5, 2, 6, 1], [2, 1, 1, 0]),
        ([-1], [0]),
        ([-1, -1], [0, 0]),
        ([], []),
        ([2, 0, 1], [2, 0, 0]),
        ([1, 2, 3, 4], [0, 0, 0, 0]),       # already sorted -> all zeros
        ([4, 3, 2, 1], [3, 2, 1, 0]),       # reverse sorted -> descending counts
        ([10, -5, 10, -5, 3], [3, 0, 2, 0, 0]),
    ]
    for nums, expected in cases:
        assert countSmaller(nums) == expected, ("bit", nums)
        assert countSmaller_brute(nums) == expected, ("brute", nums)
        assert countSmaller_mergesort(nums) == expected, ("mergesort", nums)
    print("count_of_smaller_numbers_after_self: all cases passed")


if __name__ == "__main__":
    _test()
