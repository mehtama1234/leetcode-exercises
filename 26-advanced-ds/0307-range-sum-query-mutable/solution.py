"""307. Range Sum Query - Mutable — https://leetcode.com/problems/range-sum-query-mutable/

Support two operations on an array, mixed in any order and any number of times:
`update(i, val)` sets one element, and `sumRange(l, r)` returns the sum of the
slice `nums[l..r]` inclusive. Both must stay fast even as the array keeps changing.

The whole point of this problem is the tension between the two operations. A plain
array makes `update` O(1) but `sumRange` O(n). A prefix-sum array makes `sumRange`
O(1) but `update` O(n) (every later prefix shifts). A Fenwick tree (Binary Indexed
Tree) balances them: both become O(log n). We implement the Fenwick tree here, and
keep a segment-tree version alongside so the two classic answers sit side by side.
"""
from typing import List


class NumArrayPrefix:
    """Prefix-sum baseline. sumRange O(1), but update is O(n).

    Kept to show *why* we need something cleverer. `prefix[k]` holds the sum of the
    first k elements, so a range sum is one subtraction. But changing element i by
    delta means every prefix from i+1 onward is now wrong, so update rewrites the
    tail. Great for a read-only array, wrong tool once updates are frequent.
    """

    def __init__(self, nums: List[int]) -> None:
        self.nums = nums[:]
        self.prefix = [0] * (len(nums) + 1)
        for i, x in enumerate(nums):
            self.prefix[i + 1] = self.prefix[i] + x

    def update(self, index: int, val: int) -> None:
        self.nums[index] = val
        # rebuild every prefix at or after index+1 — this is the O(n) cost
        for i in range(index, len(self.nums)):
            self.prefix[i + 1] = self.prefix[i] + self.nums[i]

    def sumRange(self, left: int, right: int) -> int:
        return self.prefix[right + 1] - self.prefix[left]


class NumArray:
    """Fenwick tree / Binary Indexed Tree. Both operations O(log n).

    The trick is to store *partial* sums, not the raw array and not full prefixes.
    The tree is 1-indexed. Node `i` is responsible for the sum of a block of
    elements ending at i, whose length is `i & (-i)` — the value of i's lowest set
    bit. So node 6 (110) covers 2 elements (6,5), node 8 (1000) covers 8 elements,
    node 5 (101) covers just itself. Every position is covered by a chain of such
    blocks whose lengths are distinct powers of two — exactly the bits of the index.

    Prefix-sum up to i: repeatedly add tree[i], then strip the lowest set bit
    (i -= i & -i) to jump to the block before this one. At most one step per bit,
    so O(log n) additions.

    Point update at i: add delta to tree[i], then move to the next node that also
    covers i by *adding* the lowest set bit (i += i & -i). Again O(log n) nodes.
    A range sum is prefix(right) - prefix(left-1).
    """

    def __init__(self, nums: List[int]) -> None:
        self.n = len(nums)
        self.nums = [0] * self.n            # our own copy of current values
        self.tree = [0] * (self.n + 1)      # 1-indexed Fenwick array
        for i, x in enumerate(nums):
            self.update(i, x)               # build by n point-updates: O(n log n)

    def _add(self, i: int, delta: int) -> None:
        """Add `delta` to logical index i (0-based). Walk up the covering blocks."""
        i += 1  # switch to 1-indexed tree space
        while i <= self.n:
            self.tree[i] += delta
            i += i & (-i)  # jump to the next node whose block also covers i

    def _prefix(self, i: int) -> int:
        """Sum of nums[0..i] inclusive (i is 0-based). Walk down the blocks."""
        i += 1  # 1-indexed
        s = 0
        while i > 0:
            s += self.tree[i]
            i -= i & (-i)  # drop the lowest set bit -> previous disjoint block
        return s

    def update(self, index: int, val: int) -> None:
        # Fenwick stores sums, so we apply the *difference* from the old value.
        delta = val - self.nums[index]
        self.nums[index] = val
        self._add(index, delta)

    def sumRange(self, left: int, right: int) -> int:
        if left == 0:
            return self._prefix(right)
        return self._prefix(right) - self._prefix(left - 1)


class NumArraySegTree:
    """Iterative segment tree — the other standard answer, also O(log n) both ways.

    A segment tree stores sums over ranges in a binary tree flattened into an array
    of size 2n. Leaves n..2n-1 hold the elements; each internal node holds the sum
    of its two children. Update fixes one leaf and walks to the root (log n parents).
    A range query walks the two boundaries inward, grabbing whole subtree sums that
    fall completely inside [l, r]. More general than Fenwick (any associative op:
    min, max, gcd), at the cost of ~2x memory and more code.
    """

    def __init__(self, nums: List[int]) -> None:
        self.n = len(nums)
        self.tree = [0] * (2 * self.n)
        for i, x in enumerate(nums):
            self.tree[self.n + i] = x
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index: int, val: int) -> None:
        i = index + self.n
        self.tree[i] = val
        i //= 2
        while i >= 1:
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]
            i //= 2

    def sumRange(self, left: int, right: int) -> int:
        lo, hi = left + self.n, right + self.n + 1  # [lo, hi)
        s = 0
        while lo < hi:
            if lo & 1:          # lo is a right child -> it's fully inside, take it
                s += self.tree[lo]
                lo += 1
            if hi & 1:          # hi-1 is a left child -> fully inside, take it
                hi -= 1
                s += self.tree[hi]
            lo //= 2
            hi //= 2
        return s


def _test() -> None:
    # Official LeetCode example.
    for Cls in (NumArray, NumArrayPrefix, NumArraySegTree):
        na = Cls([1, 3, 5])
        assert na.sumRange(0, 2) == 9, Cls.__name__
        na.update(1, 2)                 # nums -> [1, 2, 5]
        assert na.sumRange(0, 2) == 8, Cls.__name__

        # Edge: single element.
        one = Cls([7])
        assert one.sumRange(0, 0) == 7, Cls.__name__
        one.update(0, -3)
        assert one.sumRange(0, 0) == -3, Cls.__name__

        # Edge: negatives, repeated updates, sub-ranges.
        arr = Cls([-2, 0, 3, -5, 2, -1])
        assert arr.sumRange(0, 5) == -3, Cls.__name__
        assert arr.sumRange(2, 4) == 0, Cls.__name__
        arr.update(3, 5)                # -> [-2, 0, 3, 5, 2, -1]
        assert arr.sumRange(0, 5) == 7, Cls.__name__
        assert arr.sumRange(3, 3) == 5, Cls.__name__

    print("range_sum_query_mutable: all cases passed")


if __name__ == "__main__":
    _test()
