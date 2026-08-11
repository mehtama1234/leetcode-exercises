"""355. Design Twitter — https://leetcode.com/problems/design-twitter/

Support posting tweets, following/unfollowing users, and fetching a user's news
feed: the 10 most recent tweets from the user and everyone they follow, newest
first.

The interesting part is the feed. Merging each followee's recent tweets by time
is a k-way merge of sorted lists — the same job a heap is built for. We only need
the top 10, so we never merge more than we must.
"""
import heapq
from collections import defaultdict
from typing import List


class Twitter:
    """A tiny Twitter core: post, follow/unfollow, and a merged news feed.

    Each user keeps their own tweet list in post order. A single global counter
    stamps every tweet with a strictly increasing time, so "newest" is just
    "largest timestamp" — no wall clock needed and no ties.

    The feed is a k-way merge over the current user's own tweets plus each
    followee's tweets, all already sorted by time within each list. A max-heap
    seeded with the newest tweet from each relevant user lets us pull the global
    newest, then advance only that user's pointer — so we touch at most 10 pulls
    worth of tweets, not everyone's whole history.
    """

    def __init__(self) -> None:
        self.time = 0
        # userId -> list of (timestamp, tweetId), appended in post order.
        self.tweets: dict[int, list[tuple[int, int]]] = defaultdict(list)
        # userId -> set of userIds they follow.
        self.following: dict[int, set[int]] = defaultdict(set)

    def postTweet(self, userId: int, tweetId: int) -> None:
        self.tweets[userId].append((self.time, tweetId))
        self.time += 1

    def getNewsFeed(self, userId: int) -> List[int]:
        """Return up to 10 tweet ids, newest first, from self + followees."""
        # Everyone whose tweets can appear: the user and all they follow.
        sources = self.following[userId] | {userId}

        # Max-heap seeded with the newest (last) tweet of each source.
        # Entry: (-timestamp, tweetId, ownerId, index_in_owner's_list).
        heap: list[tuple[int, int, int, int]] = []
        for uid in sources:
            posts = self.tweets[uid]
            if posts:
                idx = len(posts) - 1
                ts, tid = posts[idx]
                heapq.heappush(heap, (-ts, tid, uid, idx))

        feed: List[int] = []
        while heap and len(feed) < 10:
            neg_ts, tid, uid, idx = heapq.heappop(heap)
            feed.append(tid)
            # Push this owner's next-newest tweet (one step older).
            if idx > 0:
                nidx = idx - 1
                nts, ntid = self.tweets[uid][nidx]
                heapq.heappush(heap, (-nts, ntid, uid, nidx))
        return feed

    def follow(self, followerId: int, followeeId: int) -> None:
        if followerId != followeeId:
            self.following[followerId].add(followeeId)

    def unfollow(self, followerId: int, followeeId: int) -> None:
        self.following[followerId].discard(followeeId)


def _test() -> None:
    # Official LeetCode example.
    t = Twitter()
    t.postTweet(1, 5)
    assert t.getNewsFeed(1) == [5]        # user 1's own tweet
    t.follow(1, 2)
    t.postTweet(2, 6)
    assert t.getNewsFeed(1) == [6, 5]     # 6 is newer than 5
    t.unfollow(1, 2)
    assert t.getNewsFeed(1) == [5]        # no longer sees user 2

    # Edge: feed caps at 10 and stays newest-first.
    f = Twitter()
    for i in range(1, 13):                 # post 12 tweets by user 9
        f.postTweet(9, i)
    feed = f.getNewsFeed(9)
    assert len(feed) == 10
    assert feed == [12, 11, 10, 9, 8, 7, 6, 5, 4, 3]

    # Edge: cannot follow yourself; empty feed for a silent user.
    g = Twitter()
    g.follow(1, 1)                         # no-op
    assert g.getNewsFeed(1) == []

    # Edge: merge across several followees, interleaved in time.
    m = Twitter()
    m.follow(1, 2)
    m.follow(1, 3)
    m.postTweet(2, 20)
    m.postTweet(3, 30)
    m.postTweet(2, 21)
    m.postTweet(1, 10)
    assert m.getNewsFeed(1) == [10, 21, 30, 20]

    print("twitter: all cases passed")


if __name__ == "__main__":
    _test()
