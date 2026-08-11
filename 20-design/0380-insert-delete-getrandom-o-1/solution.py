"""380. Insert Delete GetRandom O(1) — https://leetcode.com/problems/insert-delete-getrandom-o-1/

A set supporting `insert`, `remove`, and `getRandom` — return a uniformly random
current element — all in average O(1).

A hash set gives O(1) insert/remove but can't pick a uniform random element in
O(1) (you'd have to walk it). An array gives O(1) random indexing but O(n)
removal. Pairing them — array for the values, dict for value->its index — gets
all three at O(1), with a swap-with-last trick to delete without shifting.
"""
import random
from typing import List


class RandomizedSet:
    """dict + array for O(1) insert, remove, and uniform getRandom.

    `vals` is a plain array holding the current elements in no particular order.
    `pos` maps each value to its index in `vals`. Random selection is just a
    random index into `vals` — trivially uniform and O(1).

    The one hard part is O(1) removal from an array without shifting. Trick: swap
    the element to delete with the *last* element, update the moved element's
    index in `pos`, then pop the last slot. Removing from the end of an array is
    O(1), so the whole delete is O(1).
    """

    def __init__(self) -> None:
        self.vals: List[int] = []
        self.pos: dict[int, int] = {}  # value -> index in vals

    def insert(self, val: int) -> bool:
        """Add val if absent. Return True if it was actually inserted."""
        if val in self.pos:
            return False
        self.pos[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        """Remove val if present. Return True if it was actually removed."""
        if val not in self.pos:
            return False
        idx = self.pos[val]
        last = self.vals[-1]
        # Move the last element into the hole left by val.
        self.vals[idx] = last
        self.pos[last] = idx
        # Drop the now-duplicated last slot and the removed value's entry.
        self.vals.pop()
        del self.pos[val]
        return True

    def getRandom(self) -> int:
        """Return a uniformly random current element."""
        return random.choice(self.vals)


def _test() -> None:
    # Official LeetCode example.
    s = RandomizedSet()
    assert s.insert(1) is True    # {1}
    assert s.remove(2) is False   # 2 not present
    assert s.insert(2) is True    # {1, 2}
    assert s.getRandom() in (1, 2)
    assert s.remove(1) is True    # {2}
    assert s.insert(2) is False   # already present
    assert s.getRandom() == 2     # only element left

    # Edge: remove the last-inserted element (val IS the last slot).
    t = RandomizedSet()
    t.insert(10)
    t.insert(20)
    assert t.remove(20) is True   # 20 was the last element; no swap needed
    assert t.getRandom() == 10
    assert t.remove(10) is True   # now empty
    assert t.insert(10) is True   # reusable after emptying

    # Edge: re-insert after remove keeps the set consistent.
    u = RandomizedSet()
    for v in (1, 2, 3):
        u.insert(v)
    u.remove(2)                    # swaps 3 into index 1
    assert set(u.vals) == {1, 3}
    assert u.insert(2) is True
    assert set(u.vals) == {1, 2, 3}

    # Sanity: getRandom is roughly uniform over the elements.
    r = RandomizedSet()
    for v in range(5):
        r.insert(v)
    counts = {v: 0 for v in range(5)}
    random.seed(0)
    for _ in range(50000):
        counts[r.getRandom()] += 1
    # Each of 5 elements should appear ~10000 times; allow generous slack.
    for v in range(5):
        assert 8500 < counts[v] < 11500, (v, counts[v])

    print("randomized_set: all cases passed")


if __name__ == "__main__":
    _test()
