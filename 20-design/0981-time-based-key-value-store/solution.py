"""981. Time Based Key-Value Store — https://leetcode.com/problems/time-based-key-value-store/

Store multiple timestamped values per key. `get(key, t)` returns the value that
was set at the largest timestamp <= t (the value "in effect" at time t), or "" if
none exists.

Because `set` is always called with increasing timestamps, each key's history is
already sorted by time. Finding "largest timestamp <= t" in a sorted list is a
binary search — no scanning.
"""
from bisect import bisect_right
from collections import defaultdict


class TimeMap:
    """Versioned key-value store. set O(1), get O(log n) via binary search.

    For each key we keep two parallel, append-only lists: `times[key]` (the
    timestamps) and `values[key]` (the values). Timestamps arrive strictly
    increasing, so `times[key]` stays sorted for free — we never sort.

    `get(key, t)` is the classic "floor" query: find the rightmost timestamp that
    is <= t. `bisect_right` locates the first timestamp strictly greater than t;
    the entry just before it is our answer. That's O(log n) instead of an O(n)
    scan back through history.
    """

    def __init__(self) -> None:
        self.times: dict[str, list[int]] = defaultdict(list)
        self.values: dict[str, list[str]] = defaultdict(list)

    def set(self, key: str, value: str, timestamp: int) -> None:
        self.times[key].append(timestamp)
        self.values[key].append(value)

    def get(self, key: str, timestamp: int) -> str:
        """Value set at the largest timestamp <= `timestamp`, else ""."""
        if key not in self.times:
            return ""
        ts = self.times[key]
        # First index whose timestamp is strictly greater than `timestamp`.
        i = bisect_right(ts, timestamp)
        if i == 0:
            return ""            # every stored time is later than t
        return self.values[key][i - 1]


def _test() -> None:
    # Official LeetCode example.
    m = TimeMap()
    m.set("foo", "bar", 1)
    assert m.get("foo", 1) == "bar"
    assert m.get("foo", 3) == "bar"   # nothing newer than t=1, so still "bar"
    m.set("foo", "bar2", 4)
    assert m.get("foo", 4) == "bar2"
    assert m.get("foo", 5) == "bar2"

    # Edge: query before any value exists for the key.
    assert m.get("foo", 0) == ""      # first set was at t=1
    assert m.get("missing", 10) == "" # unknown key

    # Edge: exact-timestamp hits across several versions.
    s = TimeMap()
    s.set("k", "v1", 10)
    s.set("k", "v2", 20)
    s.set("k", "v3", 30)
    assert s.get("k", 9) == ""
    assert s.get("k", 10) == "v1"
    assert s.get("k", 19) == "v1"     # between v1 and v2 -> v1 still in effect
    assert s.get("k", 20) == "v2"
    assert s.get("k", 100) == "v3"    # far future -> latest value

    print("time_map: all cases passed")


if __name__ == "__main__":
    _test()
