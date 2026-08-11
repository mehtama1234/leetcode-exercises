"""560. Subarray Sum Equals K — https://leetcode.com/problems/subarray-sum-equals-k/

Count how many contiguous subarrays of `nums` add up to exactly `k`. Numbers can
be negative, so you can't use a sliding window — but prefix sums + a hash map do
it in one pass.
"""
from typing import List


def subarray_sum_brute(nums: List[int], k: int) -> int:
    """Try every subarray, add it up. O(n^2) time, O(1) space.

    For each start, extend the end one step at a time and keep a running sum. It's
    the definition made literal, but every start re-walks the tail — that repeated
    walking is the waste we remove.
    """
    n = len(nums)
    count = 0
    for start in range(n):
        running = 0
        for end in range(start, n):
            running += nums[end]
            if running == k:
                count += 1
    return count


def subarray_sum(nums: List[int], k: int) -> int:
    """Prefix sum + hash map, single pass. O(n) time, O(n) space.

    Key insight: a subarray (i..j) sums to k exactly when
        prefix[j+1] - prefix[i] == k,  i.e.  prefix[i] == prefix[j+1] - k.
    So as we sweep and maintain the running prefix sum, the question becomes:
    "how many earlier prefix sums equal (current - k)?" A dict counting how often
    each prefix sum has occurred answers that in O(1). The seed {0: 1} accounts
    for subarrays that start at index 0 (prefix 0 seen once, before anything).
    """
    count = 0
    running = 0
    seen: dict[int, int] = {0: 1}  # prefix sum -> how many times we've seen it
    for x in nums:
        running += x
        # A subarray ending here sums to k for each earlier prefix == running - k.
        count += seen.get(running - k, 0)
        seen[running] = seen.get(running, 0) + 1
    return count


def _test() -> None:
    # Official LeetCode examples.
    assert subarray_sum([1, 1, 1], 2) == 2
    assert subarray_sum([1, 2, 3], 3) == 2  # [1,2] and [3]

    # Negatives (why sliding window fails) and a zero-sum case.
    assert subarray_sum([1, -1, 0], 0) == 3  # [1,-1], [0], [1,-1,0]
    assert subarray_sum([-1, -1, 1], 0) == 1  # [-1,1]
    assert subarray_sum([3, 4, 7, 2, -3, 1, 4, 2], 7) == 4

    # Edge: single element, and brute force must agree everywhere.
    assert subarray_sum([5], 5) == 1
    assert subarray_sum([5], 3) == 0

    for nums, k in [([1, 1, 1], 2), ([1, -1, 0], 0), ([3, 4, 7, 2, -3, 1, 4, 2], 7)]:
        assert subarray_sum(nums, k) == subarray_sum_brute(nums, k), (nums, k)

    print("subarray_sum_equals_k: all cases passed")


if __name__ == "__main__":
    _test()
