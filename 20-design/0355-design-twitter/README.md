# 355. Design Twitter

**Pattern:** Composed data model + k-way merge with a heap
**Difficulty:** Medium
**Link:** https://leetcode.com/problems/design-twitter/

## The problem in plain words

Model a tiny social network. Users post tweets, follow and unfollow each other, and
ask for their news feed: the 10 most recent tweets from themselves and everyone
they follow, newest first.

```diagram
   user 1 follows user 2

   user 1 tweets:  [ 5 ]                         (time 0)
   user 2 tweets:  [ 6 ]                         (time 1)

   feed(1) merges both, newest first  ->  [ 6, 5 ]
```

## Why this matters

Two real ideas hide in here. First, **picking a data model** so each operation is
cheap: users hold their own tweet lists, follows are a set per user. Second, the
feed is a **k-way merge of sorted streams** — you have several lists already in
time order and want the newest few across all of them. A heap does that without
sorting everything.

This is the actual shape of a timeline service. A "fan-out on read" feed — pull
each followee's recent posts and merge them at request time — is exactly this heap
merge. Twitter, Instagram, and Reddit-style feeds all wrestle with the
read-versus-write-fanout tradeoff. The same k-way merge powers external sorting,
merging sorted log files, and combining results from database shards.

What the good solution buys is **not doing more work than the answer needs**. You
want only 10 tweets, so the heap lets you pull the newest, then step just that one
user's pointer back — touching a handful of tweets instead of sorting every
followee's whole history on every feed request.

## Start from the obvious

To build a feed, gather every tweet from the user and all followees into one big
pile, sort by timestamp newest-first, and take the first 10.

```diagram
   pile = user1's tweets + user2's + user3's + ...     (everything)
   sort the whole pile by time
   take the first 10
        ^ sorting N tweets to keep 10 -- most of that work is thrown away
```

Correct and plain. But it collects and sorts *everything* even though you only ever
want 10. That is the waste.

## Find the waste

Each user's own tweet list is *already* sorted by time — they were appended in
order. The naive version throws that ordering away and re-sorts from scratch.
Merging already-sorted lists shouldn't need a full sort, and since you only want
the top 10, you shouldn't even fully merge.

## The insight

Stamp every tweet with a strictly increasing global counter, so "newest" means
"largest timestamp." Store each user's tweets in post order. To build a feed,
keep a **max-heap** — a bucket that always hands you its largest item — holding the
current newest tweet from each source.

```diagram
   user1: [ (0,A) ]                 <- newest for user1
   user2: [ (1,B), (3,D) ]          <- newest is (3,D)
   user3: [ (2,C) ]                 <- newest for user3

   heap seeded with each list's newest:  { (3,D), (2,C), (0,A) }

   pop (3,D) -> feed=[D];  user2 has (1,B) left -> push it
       heap: { (2,C), (1,B), (0,A) }
   pop (2,C) -> feed=[D,C]; user3 has none left
       heap: { (1,B), (0,A) }
   pop (1,B) -> feed=[D,C,B]
   pop (0,A) -> feed=[D,C,B,A]      done (or stop at 10)
```

Each list is sorted, so the heap always holds the current front of every stream.
Pop ten times and you have the ten newest overall — and you only ever push a
followee's *next* tweet after popping their current one.

## Complexity

Let `k` = number of followees, `f` = feed size (10 here).

- **Feed:** seed the heap with up to `k` entries, then do `f` pop/push pairs, each
  costing about `log k`. So roughly `k + f log k` — independent of how many tweets
  exist in total.
- **post / follow / unfollow:** a single step each.
- **Space:** proportional to total tweets plus total follows for storage; the heap
  holds at most `k` entries at once.

## Pitfalls

- Using wall-clock time for ordering. Two tweets can share a millisecond; a
  monotonic counter gives a strict, tie-free order.
- Letting a user follow themselves and then double-counting their tweets. Guard the
  self-follow, and always include the user as a source explicitly.
- Sorting all tweets on every feed call — fine for tests, wrong at scale. The heap
  merge is the point.
- Forgetting to push only the popped user's *next* tweet, from the same list.

## Transfer

The k-way heap merge is the reusable core. See
[Merge k Sorted Lists / 23](https://leetcode.com/problems/merge-k-sorted-lists/)
and [Find K Pairs with Smallest Sums / 373](https://leetcode.com/problems/find-k-pairs-with-smallest-sums/).
The "pick the right containers per operation" modeling skill carries to
[LRU Cache / 146](../0146-lru-cache/) and
[Time Based Key-Value Store / 981](../0981-time-based-key-value-store/).
