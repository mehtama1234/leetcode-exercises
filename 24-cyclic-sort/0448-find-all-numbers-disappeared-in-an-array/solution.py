"""448. Find All Numbers Disappeared in an Array — https://leetcode.com/problems/find-all-numbers-disappeared-in-an-array/

Given `nums` of length n where every value is in 1..n, return every value in
1..n that does NOT appear. Aim for O(n) time and O(1) extra space.

Same skeleton as #442: value `v` lives at index `v-1`, and we mark "value v was
seen" by flipping the sign of the number at that home index. Whatever slot stays
positive at the end was never marked, so its index+1 is a missing number.
"""
from typing import List


def find_disappeared_set(nums: List[int]) -> List[int]:
    """Honest baseline: build the set of what's present, report the gaps.

    Correct, but the set is O(n) EXTRA memory. It's the version to beat.
    """
    present = set(nums)
    return [v for v in range(1, len(nums) + 1) if v not in present]


def find_disappeared(nums: List[int]) -> List[int]:
    """Sign-flip trick (index-as-hash). O(n) time, O(1) extra space.

    Key insight: values are 1..n, so value `v` maps to home index `v - 1`. In one
    pass, for each value `v` we flip the number at `nums[v-1]` negative — a mark
    that says "value v showed up". We use `abs()` when reading because a slot may
    already have been flipped by a previous mark; the magnitude still names the
    value.

    After marking, any index `i` whose value is still POSITIVE was never marked,
    which means the value `i + 1` never appeared. Those are the disappeared
    numbers. The output list itself doesn't count as extra bookkeeping — it's the
    required answer, not a helper structure.
    """
    n = len(nums)
    for x in nums:
        home = abs(x) - 1
        if nums[home] > 0:
            nums[home] = -nums[home]
    return [i + 1 for i in range(n) if nums[i] > 0]


def _test() -> None:
    cases = [
        ([4, 3, 2, 7, 8, 2, 3, 1], [5, 6]),
        ([1, 1], [2]),
        ([1], []),                    # nothing missing
        ([2, 2], [1]),                # 1 disappeared
        ([1, 2, 3, 4], []),           # complete
    ]
    for nums, expected in cases:
        assert find_disappeared_set(list(nums)) == expected, nums
        assert find_disappeared(list(nums)) == expected, nums
    print("find_disappeared: all cases passed")


if __name__ == "__main__":
    _test()
