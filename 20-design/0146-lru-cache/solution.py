"""146. LRU Cache — https://leetcode.com/problems/lru-cache/

Build a fixed-size key->value cache. `get` and `put` must both run in O(1). When
the cache is full and a new key arrives, evict the *least recently used* one.

The whole trick is picking data structures that let you do three things in O(1):
look a key up, mark it as "just used" (move it to the front), and drop the item
at the back. A hash map gives fast lookup; a doubly linked list gives O(1) move
and remove. Kept together, they are an LRU cache.
"""
from typing import Optional


class _Node:
    """One entry in the recency-ordered doubly linked list."""

    def __init__(self, key: int = 0, val: int = 0) -> None:
        self.key = key
        self.val = val
        self.prev: Optional["_Node"] = None
        self.next: Optional["_Node"] = None


class LRUCache:
    """dict + doubly linked list. All operations O(1).

    The list runs from most-recently-used (right behind `head`) to
    least-recently-used (right before `tail`). Two sentinel nodes, `head` and
    `tail`, remove every edge case about inserting/removing at the ends — there
    is always a real node on each side of any position we touch.

    The dict maps key -> its node, so we can jump straight to a node without
    walking the list. That is what keeps `get`/`put` at O(1): the dict finds the
    node, the linked list re-orders it, and neither operation scans anything.
    """

    def __init__(self, capacity: int) -> None:
        self.cap = capacity
        self.map: dict[int, _Node] = {}
        # Sentinels: head <-> ... <-> tail. Never removed.
        self.head = _Node()
        self.tail = _Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: _Node) -> None:
        """Unlink a node from wherever it currently sits."""
        node.prev.next = node.next  # type: ignore[union-attr]
        node.next.prev = node.prev  # type: ignore[union-attr]

    def _add_front(self, node: _Node) -> None:
        """Insert a node just after head (mark it most-recently-used)."""
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node  # type: ignore[union-attr]
        self.head.next = node

    def get(self, key: int) -> int:
        """Return the value and mark the key as most-recently-used, else -1."""
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_front(node)
        return node.val

    def put(self, key: int, value: int) -> None:
        """Insert or update. Evict the LRU entry if we overflow capacity."""
        if key in self.map:
            node = self.map[key]
            node.val = value
            self._remove(node)
            self._add_front(node)
            return
        if len(self.map) >= self.cap:
            lru = self.tail.prev  # node just before tail = least recent
            self._remove(lru)      # type: ignore[arg-type]
            del self.map[lru.key]  # type: ignore[union-attr]
        node = _Node(key, value)
        self.map[key] = node
        self._add_front(node)


def _test() -> None:
    # Official LeetCode example.
    c = LRUCache(2)
    c.put(1, 1)
    c.put(2, 2)
    assert c.get(1) == 1          # returns 1, key 1 now most-recent
    c.put(3, 3)                    # evicts key 2 (least recent)
    assert c.get(2) == -1         # 2 was evicted
    c.put(4, 4)                    # evicts key 1
    assert c.get(1) == -1
    assert c.get(3) == 3
    assert c.get(4) == 4

    # Edge: capacity 1 — every new key evicts the previous one.
    d = LRUCache(1)
    d.put(1, 10)
    assert d.get(1) == 10
    d.put(2, 20)
    assert d.get(1) == -1
    assert d.get(2) == 20

    # Edge: updating an existing key both refreshes value and recency.
    e = LRUCache(2)
    e.put(1, 1)
    e.put(2, 2)
    e.put(1, 100)                  # update value AND make 1 most-recent
    e.put(3, 3)                    # evicts 2, not 1
    assert e.get(2) == -1
    assert e.get(1) == 100
    assert e.get(3) == 3

    print("lru_cache: all cases passed")


if __name__ == "__main__":
    _test()
