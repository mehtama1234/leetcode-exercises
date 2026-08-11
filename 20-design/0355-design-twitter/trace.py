"""Rich full-arc trace for Design Twitter (tree renderer, heap view).
The interesting part is the feed: a k-way merge of each source's time-sorted
tweets, pulling the 10 newest. A max-heap holds one candidate per source; we pop
the global newest, then push that owner's next-older tweet. The arc: the rule
(one candidate per source, heap picks the max) -> run the merge pulling newest
-> edge (feed caps at 10; unfollow removes a source). Nodes are heap entries
placed by hand. Mirrors solution.py's getNewsFeed. Writes trace.json.
"""
import json
import os
import heapq

frames = []

CODE = [
    "sources = following[user] | {user}",
    "heap = []                       # max-heap by timestamp",
    "for uid in sources:             # seed newest of each",
    "    if tweets[uid]: push newest (-ts, tid, uid, idx)",
    "while heap and len(feed) < 10:",
    "    -ts, tid, uid, idx = heappop(heap)   # global newest",
    "    feed.append(tid)",
    "    if idx > 0: push tweets[uid][idx-1]  # next older",
]


def add(**f):
    frames.append(f)


# Scenario mirrors solution.py's k-way-merge test:
#   user 1 follows 2 and 3.
#   postTweet order (global time): 2->20@t0, 3->30@t1, 2->21@t2, 1->10@t3.
# Each user's tweets in post order (ts, tid):
tweets = {
    1: [(3, 10)],
    2: [(0, 20), (2, 21)],
    3: [(1, 30)],
}
sources = [1, 2, 3]

# ---- Node layout for the heap view ----
# We draw the heap as a small binary tree. We recompute node positions each frame
# from the current heap contents so the picture matches the real heap array.
XSTEP, YSTEP, X0, Y0 = 88, 84, 20, 20


def heap_nodes(heap):
    """heap is the real heapq list of (-ts, tid, uid, idx). Lay out array as a
    binary tree by array index (parent i -> children 2i+1, 2i+2)."""
    nodes = []
    edges = []
    n = len(heap)
    # depth-based x: assign columns by in-order-ish index; simple: level + slot.
    for i, entry in enumerate(heap):
        negts, tid, uid, idx = entry
        depth = i.bit_length() - 1 if i > 0 else 0
        # slot within level
        level_start = (1 << depth) - 1
        slot = i - level_start
        width = 1 << depth
        # center each level
        x = X0 + (slot - (width - 1) / 2) * XSTEP + 3 * XSTEP
        y = Y0 + depth * YSTEP
        nodes.append({"id": i, "val": f"t{tid}@{-negts}", "x": x, "y": y})
    for i in range(n):
        if 2 * i + 1 < n:
            edges.append([i, 2 * i + 1])
        if 2 * i + 2 < n:
            edges.append([i, 2 * i + 2])
    return nodes, edges


def feed_state(feed, heap):
    return [["feed", " ".join(str(t) for t in feed) or "(empty)"],
            ["heap size", len(heap)], ["pulled", len(feed)]]


# ---- Act 0: the rule ----
# Seed heap: newest of each source.
heap = []
for uid in sources:
    posts = tweets[uid]
    if posts:
        idx = len(posts) - 1
        ts, tid = posts[idx]
        heapq.heappush(heap, (-ts, tid, uid, idx))
nodes, edges = heap_nodes(heap)
add(act=0, nodes=nodes, edges=edges, code="feed", line=2,
    intro="one candidate per source enters the heap — its NEWEST tweet. The heap's top "
    "is the global newest across everyone.",
    invariant="the heap holds at most one tweet per source at any moment.",
    note="A news feed merges each source's time-sorted tweets. Seed a max-heap with the "
    "newest tweet of the user and each followee. User 1 follows 2 and 3.",
    active=[0], done={}, state=[["sources", "1, 2, 3"], ["heap size", len(heap)]])
add(act=0, nodes=nodes, edges=edges, code="feed", line=3,
    note="Seeded: 1's newest t10@3, 2's newest t21@2, 3's newest t30@1. The heap keeps "
    "the largest timestamp on top — here t10@3 (time 3).",
    active=[0], done={}, state=[["top", "t10 (time 3)"], ["heap size", len(heap)]])

# ---- Act 1: run the merge ----
add(act=1, nodes=nodes, edges=edges, code="feed", line=4,
    intro="each pop takes the global newest; then we push only THAT owner's next-older "
    "tweet — never everyone's whole history.",
    invariant="feed is built strictly newest-first; we stop at 10 pulls.",
    note="Pull the newest repeatedly. After popping a tweet, push that same user's "
    "next-older one, so the heap always has their best remaining candidate.",
    active=[0], done={}, state=[["feed", "(empty)"], ["heap size", len(heap)]])

feed = []
step = 0
while heap and len(feed) < 10:
    negts, tid, uid, idx = heap[0]
    nodes, edges = heap_nodes(heap)
    add(act=1, nodes=nodes, edges=edges, code="feed", line=5,
        note=f"Top of heap is t{tid}@{-negts} (user {uid}, time {-negts}) — the global "
        f"newest. Pop it.",
        active=[0], done={i: heap[i][1] for i in range(len(heap))},
        state=feed_state(feed, heap) + [["popping", f"t{tid}"]])
    heapq.heappop(heap)
    feed.append(tid)
    if idx > 0:
        nidx = idx - 1
        nts, ntid = tweets[uid][nidx]
        heapq.heappush(heap, (-nts, ntid, uid, nidx))
        nodes, edges = heap_nodes(heap)
        add(act=1, nodes=nodes, edges=edges, code="feed", line=7,
            note=f"Added t{tid} to the feed. User {uid} has an older tweet t{ntid}@{nts} — "
            f"push it as their new candidate.",
            active=[0] if heap else [], done={i: heap[i][1] for i in range(len(heap))},
            state=feed_state(feed, heap) + [["pushed", f"t{ntid} (user {uid})"]])
    else:
        nodes, edges = heap_nodes(heap)
        add(act=1, nodes=nodes, edges=edges, code="feed", line=6,
            note=f"Added t{tid} to the feed. User {uid} has no older tweet, so nothing "
            "replaces it — that source is exhausted.",
            active=[0] if heap else [], done={i: heap[i][1] for i in range(len(heap))},
            state=feed_state(feed, heap) + [["exhausted", f"user {uid}"]])
    step += 1

add(act=1, nodes=[], edges=[], code="feed", line=4,
    note=f"Heap empty — every tweet merged. Feed newest-first: {feed}. Only the newest "
    "candidate per source was ever compared.",
    active=[], done={}, state=[["feed", " ".join(map(str, feed))], ["pulls", len(feed)]],
    banner=f"getNewsFeed(1) = {feed}  (newest first)")

# ---- Act 2: edge — cap at 10 / unfollow drops a source ----
# Edge A: a single user with 12 tweets -> feed caps at 10.
big = [(t, t + 1) for t in range(12)]  # (ts, tid): tid 1..12 at times 0..11
h2 = []
idx = len(big) - 1
ts, tid = big[idx]
heapq.heappush(h2, (-ts, tid, 9, idx))
n2, e2 = heap_nodes(h2)
add(act=2, nodes=n2, edges=e2, code="feed", line=4,
    intro="the while-loop guard len(feed) < 10 stops us early — we never touch tweet 11.",
    invariant="at most 10 pops happen no matter how long a history is.",
    note="Edge: user 9 posted 12 tweets (ids 1..12). Seed the newest, t12. We pull "
    "newest-first but stop after 10.",
    active=[0], done={0: 12}, state=[["tweets", 12], ["cap", 10]])
feed2 = []
while h2 and len(feed2) < 10:
    negts, tid, uid, i = heapq.heappop(h2)
    feed2.append(tid)
    if i > 0:
        nts, ntid = big[i - 1]
        heapq.heappush(h2, (-nts, ntid, uid, i - 1))
add(act=2, nodes=[{"id": 0, "val": "t2", "x": 300, "y": 20}], edges=[], code="feed", line=4,
    note=f"Stopped at 10: feed = {feed2}. Tweets 2 and 1 (the oldest two) are never "
    "pulled — the guard len(feed) < 10 saved that work.",
    active=[], done={}, state=[["feed len", len(feed2)], ["skipped", "t2, t1"]],
    banner=f"Feed caps at 10: {feed2}")

# Edge B: unfollow removes a source before the merge.
add(act=2, nodes=[{"id": 0, "val": "t5", "x": 300, "y": 20}], edges=[], code="feed", line=0,
    note="Unfollow just drops a followee from `sources`, so their tweets never enter the "
    "heap. Following yourself is a no-op, so a silent user gets an empty feed.",
    active=[0], done={0: 5}, state=[["sources", "self only"], ["unfollowed", "user 2"]],
    banner="unfollow -> that user's tweets never seed the heap")

trace = {
    "player": "tree",
    "title": "Design Twitter - a heap k-way merges each source's newest tweets",
    "acts": ["The rule: one candidate per source", "Run the merge (newest first)",
             "Edge: cap at 10 / unfollow"],
    "code": {"feed": CODE},
    "legend": [["active", "heap top (global newest)"], ["good", "in the heap"]],
    "nodes": nodes if nodes else [{"id": 0, "val": "seed", "x": 300, "y": 20}],
    "edges": [], "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
