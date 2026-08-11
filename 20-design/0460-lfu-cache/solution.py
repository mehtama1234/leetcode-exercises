"""460. LFU Cache — https://leetcode.com/problems/lfu-cache/

Fixed-size key->value cache. When full, evict the *least frequently used* key.
Break ties by evicting the least recently used among the least frequent. Both
`get` and `put` must run in O(1).

The trick that keeps everything O(1): bucket keys by their use-count. Each bucket
is a recency-ordered list (newest at the front). Track the smallest count in use,
so eviction is "drop the back of the min-count bucket" — no scanning for the
minimum, no sorting.
"""
from collections import OrderedDict


class LFUCache:
    """dict + per-frequency ordered buckets. All operations O(1).

    Three pieces stay in sync:
      * `key_val`   : key -> value.
      * `key_freq`  : key -> how many times it's been used.
      * `freq_keys` : freq -> OrderedDict of keys at that frequency, in
                      recency order (oldest first, newest last).
    Plus `min_freq`, the smallest frequency any live key currently has.

    An OrderedDict gives O(1) move-to-end and O(1) pop-from-front, which is what
    makes each bucket a fast LRU list. When we touch a key, we lift it from its
    freq bucket, bump its freq, and drop it into the next bucket's end. Eviction
    removes the *front* (oldest) key of the `min_freq` bucket — the least
    frequent, and among those the least recent. Nothing is ever scanned.
    """

    def __init__(self, capacity: int) -> None:
        self.cap = capacity
        self.key_val: dict[int, int] = {}
        self.key_freq: dict[int, int] = {}
        self.freq_keys: dict[int, "OrderedDict[int, None]"] = {}
        self.min_freq = 0

    def _touch(self, key: int) -> None:
        """Advance a key's frequency by one, moving it between buckets."""
        f = self.key_freq[key]
        bucket = self.freq_keys[f]
        del bucket[key]
        if not bucket:
            del self.freq_keys[f]
            # If we just emptied the current minimum bucket, the new minimum
            # is exactly one higher (the bucket this key is about to enter).
            if self.min_freq == f:
                self.min_freq = f + 1
        nf = f + 1
        self.key_freq[key] = nf
        self.freq_keys.setdefault(nf, OrderedDict())[key] = None

    def get(self, key: int) -> int:
        if key not in self.key_val:
            return -1
        self._touch(key)
        return self.key_val[key]

    def put(self, key: int, value: int) -> None:
        if self.cap <= 0:
            return
        if key in self.key_val:
            self.key_val[key] = value
            self._touch(key)
            return
        if len(self.key_val) >= self.cap:
            # Evict least-frequent, least-recent: front of the min_freq bucket.
            bucket = self.freq_keys[self.min_freq]
            evict_key, _ = bucket.popitem(last=False)  # pop oldest (front)
            if not bucket:
                del self.freq_keys[self.min_freq]
            del self.key_val[evict_key]
            del self.key_freq[evict_key]
        # New keys start at frequency 1, which becomes the new minimum.
        self.key_val[key] = value
        self.key_freq[key] = 1
        self.freq_keys.setdefault(1, OrderedDict())[key] = None
        self.min_freq = 1


def _test() -> None:
    # Official LeetCode example.
    c = LFUCache(2)
    c.put(1, 1)                    # {1:f1}
    c.put(2, 2)                    # {1:f1, 2:f1}
    assert c.get(1) == 1          # use 1 -> {1:f2, 2:f1}
    c.put(3, 3)                    # full; evict min-freq key 2 -> {1:f2, 3:f1}
    assert c.get(2) == -1         # 2 was evicted
    assert c.get(3) == 3          # use 3 -> {1:f2, 3:f2}
    c.put(4, 4)                    # full; both at f2, evict older -> key 1
    assert c.get(1) == -1         # 1 was evicted -> {3:f2, 4:f1}
    assert c.get(3) == 3
    assert c.get(4) == 4

    # Edge: capacity 0 stores nothing.
    z = LFUCache(0)
    z.put(1, 1)
    assert z.get(1) == -1

    # Edge: tie broken by recency (LRU among least frequent).
    t = LFUCache(2)
    t.put(1, 1)                    # freq(1)=1
    t.put(2, 2)                    # freq(2)=1
    # both at freq 1; 1 is older than 2.
    t.put(3, 3)                    # evict the least recent at freq 1 -> key 1
    assert t.get(1) == -1
    assert t.get(2) == 2
    assert t.get(3) == 3

    # Edge: updating a key's value counts as a use (bumps frequency).
    u = LFUCache(2)
    u.put(1, 10)                   # freq(1)=1
    u.put(2, 20)                   # freq(2)=1
    u.put(1, 100)                  # update value AND bump freq(1)=2
    u.put(3, 30)                   # evict key 2 (freq 1), keep key 1 (freq 2)
    assert u.get(2) == -1
    assert u.get(1) == 100
    assert u.get(3) == 30

    print("lfu_cache: all cases passed")


if __name__ == "__main__":
    _test()
