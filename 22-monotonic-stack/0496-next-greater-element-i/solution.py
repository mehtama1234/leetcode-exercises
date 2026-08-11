"""496. Next Greater Element I — https://leetcode.com/problems/next-greater-element-i/

For each value in `nums1` (a subset of `nums2`), find the first number to its
right in `nums2` that is strictly greater. If there is none, report -1.

The brute force and the monotonic-stack precompute are kept side by side so the
reason the fast one exists is visible.
"""
from typing import Dict, List


def next_greater_element_brute(nums1: List[int], nums2: List[int]) -> List[int]:
    """Locate each query in nums2, then scan right for a bigger value. O(n*m).

    Direct from the definition: find the element, walk rightward until something
    strictly larger appears. Correct, but every query re-walks nums2 from scratch,
    re-discovering "next greater" relationships that never change.
    """
    ans: List[int] = []
    for x in nums1:
        j = nums2.index(x)
        nxt = -1
        for k in range(j + 1, len(nums2)):
            if nums2[k] > x:
                nxt = nums2[k]
                break
        ans.append(nxt)
    return ans


def next_greater_element(nums1: List[int], nums2: List[int]) -> List[int]:
    """Monotonic decreasing stack over nums2, precompute all answers. O(n+m)/O(n).

    Sweep nums2 once, keeping a stack of values still *waiting* for their next
    greater element — a stack whose values strictly decrease bottom -> top. When
    the current value is bigger than the stack top, it *is* that top's next
    greater element: pop and record it. Every value that never gets popped has no
    greater element to its right and defaults to -1.

    Because nums2 has distinct values, a single dict value -> next-greater answers
    every nums1 query in O(1). Each value is pushed once and popped at most once,
    so building the map is O(m).
    """
    next_greater: Dict[int, int] = {}
    stack: List[int] = []  # values still awaiting a greater element on their right
    for x in nums2:
        while stack and stack[-1] < x:
            next_greater[stack.pop()] = x  # x resolves this waiting value
        stack.append(x)
    # anything left on the stack has no greater element to its right
    return [next_greater.get(x, -1) for x in nums1]


def _test() -> None:
    cases = [
        (([4, 1, 2], [1, 3, 4, 2]), [-1, 3, -1]),
        (([2, 4], [1, 2, 3, 4]), [3, -1]),
        (([1], [1]), [-1]),
        (([5, 3, 1], [1, 3, 5]), [-1, 5, 3]),  # decreasing queries
        (([1, 2, 3], [3, 2, 1]), [-1, -1, -1]),
    ]
    for (nums1, nums2), expected in cases:
        assert next_greater_element(nums1, nums2) == expected, (nums1, nums2)
        assert next_greater_element_brute(nums1, nums2) == expected, (nums1, nums2)
    print("next_greater_element: all cases passed")


if __name__ == "__main__":
    _test()
