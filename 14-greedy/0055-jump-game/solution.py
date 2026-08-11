"""55. Jump Game — https://leetcode.com/problems/jump-game/

Each entry in the array is the max number of steps you can jump forward from that
index. Starting at index 0, return whether you can reach the last index.
"""
from typing import List


def can_jump(nums: List[int]) -> bool:
    """Track the farthest index reachable so far. O(n) time, O(1) space.

    Greedy insight: we don't need to know *which* jumps to take, only how far we
    could possibly get. Sweep left to right holding `reach` = the farthest index
    reachable using everything seen so far. At index i, if i > reach we can never
    stand on i (nothing before it jumps far enough), so we're stuck — return
    False. Otherwise i is reachable, so from i we can extend our frontier to
    `i + nums[i]`; keep the best.

    Why the greedy choice is safe: reachability is "downward closed" — if you can
    reach index i, you can reach every index between the start and i (a jump of
    length L also permits any length < L). So the single number "farthest
    reachable" captures the whole reachable set exactly; there's no need to branch
    over individual jump choices. Maximizing the frontier at each step never rules
    out a position we could otherwise have reached.
    """
    reach = 0  # farthest index reachable so far
    for i, step in enumerate(nums):
        if i > reach:
            return False          # this index is beyond anything we can reach
        if i + step > reach:
            reach = i + step      # extend the frontier
        if reach >= len(nums) - 1:
            return True           # last index already within reach
    return True


def _test() -> None:
    cases = [
        ([2, 3, 1, 1, 4], True),
        ([3, 2, 1, 0, 4], False),   # the 0 at index 3 is an unavoidable trap
        ([0], True),                # already at the last index
        ([1, 0], True),
        ([0, 1], False),            # stuck at the start
        ([2, 0, 0], True),          # one jump clears both zeros
        ([1, 1, 1, 1], True),
    ]
    for nums, expected in cases:
        assert can_jump(nums) == expected, nums
    print("can_jump: all cases passed")


if __name__ == "__main__":
    _test()
