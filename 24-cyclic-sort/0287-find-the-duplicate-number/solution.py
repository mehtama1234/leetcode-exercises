"""287. Find the Duplicate Number — https://leetcode.com/problems/find-the-duplicate-number/

Given `nums` of length n+1 where every value is in 1..n, exactly one value is
repeated (possibly many times). Find that repeated value WITHOUT modifying the
array and using only O(1) extra space.

The "don't modify the array" + "O(1) space" pair rules out the sign-flip trick.
Instead we read the array as a linked list: index i points to node nums[i].
Because two indices share the same value, two arrows point at the same node — the
list has a cycle, and its entrance is the duplicate. Floyd's tortoise-and-hare
finds that entrance in O(1) space.
"""
from typing import List


def find_duplicate_sign(nums: List[int]) -> int:
    """Sign-flip version — shown ONLY to contrast: it mutates the input.

    This is the #442/#448 idea: mark value `v` by flipping the number at index
    `v-1`; the first value whose home is already negative is the duplicate. It's
    O(n)/O(1), but it MODIFIES the array (we restore it here), which #287 forbids.
    Included so the linked-list solution's constraint is concrete, not abstract.
    """
    ans = -1
    for x in nums:
        home = abs(x) - 1
        if nums[home] < 0:
            ans = abs(x)
            break
        nums[home] = -nums[home]
    for i in range(len(nums)):
        nums[i] = abs(nums[i])  # restore, since we promised not to modify
    return ans


def find_duplicate(nums: List[int]) -> int:
    """Floyd's cycle detection. O(n) time, O(1) space, array untouched.

    Read the array as a function on positions: from position `i` you jump to
    position `nums[i]`. Start at position 0 and keep jumping. Values are in
    1..n and there are n+1 of them, so at least two positions hold the same
    value — meaning at least two positions jump to the SAME next position. That
    shared target is a node with two arrows into it: the sequence must eventually
    loop, and the entrance of that loop is exactly the duplicated value.

    Phase 1 — find a meeting point inside the cycle. A slow pointer steps once,
    a fast pointer steps twice; they are guaranteed to collide inside the loop.

    Phase 2 — find the loop's entrance. Reset one pointer to the start; advance
    both one step at a time. The distance math of Floyd's algorithm makes them
    meet precisely at the cycle's entrance, which is the repeated number.
    """
    slow = nums[0]
    fast = nums[0]
    # Phase 1: advance until slow and fast meet inside the cycle.
    while True:
        slow = nums[slow]
        fast = nums[nums[fast]]
        if slow == fast:
            break
    # Phase 2: find the entrance to the cycle (the duplicate value).
    slow = nums[0]
    while slow != fast:
        slow = nums[slow]
        fast = nums[fast]
    return slow


def _test() -> None:
    cases = [
        ([1, 3, 4, 2, 2], 2),
        ([3, 1, 3, 4, 2], 3),
        ([1, 1], 1),                 # smallest case, n = 1
        ([2, 2, 2, 2, 2], 2),        # duplicate repeated many times
        ([1, 4, 4, 2, 4, 3], 4),
    ]
    for nums, expected in cases:
        snapshot = list(nums)
        assert find_duplicate(nums) == expected, nums
        # Floyd must not have modified the array.
        assert nums == snapshot, ("array was modified", nums, snapshot)
        assert find_duplicate_sign(list(nums)) == expected, nums
    print("find_duplicate: all cases passed")


if __name__ == "__main__":
    _test()
