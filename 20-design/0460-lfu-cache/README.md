# 460. LFU Cache

**Pattern:** Hash maps + per-frequency ordered buckets (O(1) LFU with LRU tie-break)
**Difficulty:** Hard
**Link:** https://leetcode.com/problems/lfu-cache/

## The problem in plain words

A fixed-size key/value cache. `get` and `put` work as usual, but when the cache
is full and a new key arrives, evict the key that has been used the *fewest*
times — the "least frequently used." If several keys tie for fewest uses, evict
the one among them that was used longest ago (least recently used). Both
operations must run in O(1).

## Why this matters

LFU asks a subtler question than LRU: not "what's cold *right now*," but "what's
been cold *the whole time*." Tracking usage frequency and evicting the rarest
resists a one-off burst that would wrongly promote an item under pure recency.

This is a real caching policy. Database buffer pools and storage tiers use LFU
(and LFU/LRU hybrids like ARC and W-TinyLFU, which power Caffeine, the JVM cache
behind many services) to keep genuinely hot pages. CDNs weigh how *often* an
object is requested, not just how recently. Memory allocators and page-
replacement research lean on frequency counts.

The hard part — and what the good solution buys — is doing all this in **O(1)**.
The obvious frequency cache scans for the minimum count on every eviction, which
is O(n). Getting eviction, frequency bumps, and tie-breaking all to constant time
is what makes LFU usable in a hot path with a strict latency budget.

## Start from the obvious

Keep a `key -> value` map and a `key -> count` map. On eviction, scan the counts
for the smallest, breaking ties somehow, and drop that key.

```
def evict(self):
    victim = min(self.counts, key=self.counts.get)   # O(n) scan
    del self.values[victim]; del self.counts[victim]
```

`get`/`put` are O(1), but every eviction scans all keys for the minimum count —
O(n) — and the tie-break (which of the min-count keys is least recent?) needs
even more bookkeeping. Correct, but misses the required complexity.

## Find the waste

Two things are being recomputed. First, we rescan for the minimum count each
eviction, though it changes in small, predictable steps. Second, we have no
structure that remembers *recency within a count*, so ties force another scan.

Both point to the same fix: **group keys by their count**, and within each group
keep them in recency order.

## The insight

Maintain three maps plus one integer:

- `key_val`: `key -> value`.
- `key_freq`: `key -> use count`.
- `freq_keys`: `freq -> ordered collection of keys at that frequency`, oldest at
  the front, newest at the back.
- `min_freq`: the smallest frequency any live key currently has.

Use an `OrderedDict` for each bucket: it gives O(1) append-to-end (newest) and
O(1) pop-from-front (oldest) — a ready-made LRU list.

- **Touch a key** (`get`, or `put` on an existing key): remove it from its
  current freq bucket, increment its freq, append it to the next freq's bucket.
  If that emptied the `min_freq` bucket, `min_freq` rises by exactly one (the
  bucket the key just moved into).
- **Insert a new key**: it starts at frequency 1, so `min_freq` resets to 1.
- **Evict**: pop the *front* (oldest) key of the `min_freq` bucket. That key is
  the least frequent, and among those the least recent — both rules satisfied,
  no scan.

Because `min_freq` only ever moves in single steps we can track directly, and
every bucket operation is O(1), the whole cache is O(1).

## Complexity

- **Time:** `O(1)` for both `get` and `put`. Finding the eviction victim is O(1)
  (front of the `min_freq` bucket); frequency bumps are O(1) OrderedDict moves.
- **Space:** `O(capacity)` — three entries per key across the maps, plus the
  bucket structure.

## Pitfalls

- Getting `min_freq` maintenance wrong. It only needs updating in two places: set
  to 1 on any new insertion, and bumped by one when a touch empties the current
  min bucket. Rescanning for it defeats the purpose.
- Forgetting that **updating an existing key's value is a use** — it must bump
  frequency, just like a `get`.
- Not deleting a bucket when it empties, leaving stale empty structures that
  confuse `min_freq` logic.
- The `capacity == 0` case — the cache should store nothing and every `get`
  returns -1.
- Wrong tie-break: evicting the newest instead of the oldest within the min
  bucket. Pop the front, not the back.

## Transfer

LFU is [LRU Cache / 146](../0146-lru-cache/) with an extra frequency dimension —
the same "hash map for lookup + linked structure for ordered eviction" skeleton,
layered per count. The bucket-by-a-key idea also shows up in
[All O`one Data Structure / 432](https://leetcode.com/problems/all-oone-data-structure/),
where counts are bucketed to get O(1) min/max. When you need "constant-time
access to the extreme of a changing multiset," bucket by the key you rank on.
