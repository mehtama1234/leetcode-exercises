# 355. Design Twitter

**Pattern:** Composed data model + k-way merge with a heap
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/design-twitter/

## The problem in plain words

Model a tiny social network. Users can post tweets, follow and unfollow each
other, and ask for their news feed: the 10 most recent tweets from themselves
and everyone they follow, newest first.

## Why this matters

Two real ideas hide in here. First, **choosing a data model** so each operation
is cheap: users hold their own tweet lists, follows are a set per user. Second,
the feed is a **k-way merge of sorted streams** — you have several lists already
in time order and want the globally newest few, merged. A heap does that without
sorting everything.

This is the actual shape of a timeline/feed service. A "fan-out on read" feed
(pull each followee's recent posts and merge them at request time) is exactly
this heap merge — Twitter, Instagram, and Reddit-style feeds all wrestle with
the read-vs-write-fanout tradeoff. The same k-way merge powers external sorting,
merging sorted log files, and combining results from database shards.

What the good solution buys is **not doing more work than the answer needs**. We
want only 10 tweets, so the heap lets us pull the newest, then advance just that
one user's pointer — touching a handful of tweets instead of sorting every
followee's entire history on every feed request.

## Start from the obvious

To build a feed, gather every tweet from the user and all followees into one big
list, sort by timestamp descending, and take the first 10.

```
all_tweets = []
for u in followees + [me]:
    all_tweets += tweets[u]
all_tweets.sort(key=lambda t: -t.time)
return [t.id for t in all_tweets[:10]]
```

Correct and simple. But it collects and sorts *everything* — O(N log N) over the
total tweet count — even though we only ever want 10. That's the waste.

## Find the waste

Each user's own tweet list is *already* sorted by time (they were appended in
order). We're throwing that ordering away and re-sorting from scratch. Merging
already-sorted lists shouldn't need a full sort — and we only want the top 10, so
we shouldn't even fully merge.

## The insight

Stamp every tweet with a strictly increasing global counter, so "newest" means
"largest timestamp." Store each user's tweets in post order. To build a feed:

1. Seed a **max-heap** with the *newest* tweet from the user and each followee —
   at most one entry per source.
2. Pop the heap: that's the globally newest unseen tweet. Add it to the feed.
3. Push that same user's *next* tweet (one step older) back onto the heap.
4. Repeat until you have 10 tweets or the heap empties.

Because each list is sorted, the heap always holds the current front of every
stream, and popping ten times gives the ten newest overall.

## Complexity

Let `k` = number of followees, `f` = feed size (10 here).

- **Feed:** `O(k + f log k)` — seed the heap with up to `k` entries, then do `f`
  pop/push operations each `O(log k)`. Independent of total tweets posted.
- **post / follow / unfollow:** `O(1)`.
- **Space:** `O(total tweets + total follows)` for storage; the heap holds at
  most `k` entries at a time.

## Pitfalls

- Using wall-clock time for ordering. Two tweets can share a millisecond; a
  monotonic counter gives a strict, tie-free order.
- Letting a user follow themselves and then double-counting their tweets. Guard
  the self-follow, and always include the user as a source explicitly.
- Sorting all tweets on every feed call — fine for tests, wrong at scale. The
  heap merge is the point.
- Forgetting to advance only the popped user's pointer (pushing the *next* tweet
  from the same list).

## Transfer

The k-way heap merge is the reusable core. See
[Merge k Sorted Lists / 23](https://leetcode.com/problems/merge-k-sorted-lists/)
and [Find K Pairs with Smallest Sums / 373](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/).
The "pick the right containers per operation" modeling skill carries to
[LRU Cache / 146](../0146-lru-cache/) and
[Time Based Key-Value Store / 981](../0981-time-based-key-value-store/).
