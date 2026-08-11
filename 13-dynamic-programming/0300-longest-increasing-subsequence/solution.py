"""300. Longest Increasing Subsequence — https://leetcode.com/problems/longest-increasing-subsequence/

Given an array of integers, return the length of the longest strictly
increasing subsequence (pick elements in order, not necessarily contiguous).

Two implementations are kept side by side: an O(n^2) DP that builds the answer
one position at a time, and an O(n log n) "patience sorting" version that trades
the inner scan for a binary search.
"""
from typing import List
from bisect import bisect_left


def length_of_lis_dp(nums: List[int]) -> int:
    """O(n^2) time, O(n) space.

    Define dp[i] = length of the longest increasing subsequence that *ends* at
    index i. That "ends at i" anchor is the whole trick: it pins down the last
    element, so any earlier element nums[j] < nums[i] could be the one right
    before it. The best subsequence ending at i is therefore 1 plus the best
    among all valid predecessors:

        dp[i] = 1 + max(dp[j] for j < i if nums[j] < nums[i])   (or 1 if none)

    We compute dp left to right so every dp[j] we read is already final. The
    answer is the largest dp value, since the longest subsequence can end
    anywhere.
    """
    if not nums:
        return 0
    n = len(nums)
    dp = [1] * n  # each element alone is a length-1 subsequence
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                dp[i] = max(dp[i], dp[j] + 1)
    return max(dp)


def length_of_lis(nums: List[int]) -> int:
    """Patience sorting + binary search. O(n log n) time, O(n) space.

    The O(n^2) version wastes time re-scanning all predecessors for each i. The
    key observation: to extend increasing subsequences we only ever care about
    their *smallest possible tail* for each length. Keep an array `tails` where
    tails[k] is the smallest value that can end an increasing subsequence of
    length k+1.

    For each x:
      - find the leftmost tail >= x (binary search),
      - if none exists, x extends the longest run so far -> append it,
      - otherwise x is a better (smaller) tail for that length -> overwrite it.

    `tails` stays sorted throughout, which is what makes the binary search valid.
    Its length equals the LIS length. tails itself is NOT a real subsequence —
    only its length is meaningful — but that length is provably correct.
    """
    tails: List[int] = []
    for x in nums:
        pos = bisect_left(tails, x)  # leftmost index with tails[pos] >= x
        if pos == len(tails):
            tails.append(x)
        else:
            tails[pos] = x
    return len(tails)


def _test() -> None:
    cases = [
        ([10, 9, 2, 5, 3, 7, 101, 18], 4),   # [2,3,7,101]
        ([0, 1, 0, 3, 2, 3], 4),             # [0,1,2,3]
        ([7, 7, 7, 7, 7, 7, 7], 1),          # strictly increasing -> length 1
        ([], 0),                             # empty
        ([5], 1),                            # single element
        ([1, 2, 3, 4, 5], 5),                # already sorted
    ]
    for nums, expected in cases:
        assert length_of_lis(nums) == expected, nums
        assert length_of_lis_dp(nums) == expected, nums
    print("length_of_lis: all cases passed")


if __name__ == "__main__":
    _test()
