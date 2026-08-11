"""155. Min Stack — https://leetcode.com/problems/min-stack/

A normal stack (push/pop/top) that also answers `getMin()` — the smallest value
currently in the stack — in O(1) time.

The naive idea (scan the stack for the minimum) is O(n) per query. The insight is
to *remember* the running minimum alongside each element, so the current min is
always sitting on top with the top element.
"""


class MinStack:
    """Stack that tracks its minimum in O(1) for every operation.

    We keep two parallel stacks. `stack` holds the values as usual. `mins` holds,
    at each level, the minimum of everything at or below that level. When we push
    x, the new minimum is `min(x, current_min)`; we push that onto `mins`. When we
    pop, we pop both. So `mins[-1]` is always the current minimum — no scanning.
    """

    def __init__(self) -> None:
        self.stack: list[int] = []
        self.mins: list[int] = []  # mins[i] = min of stack[0..i]

    def push(self, val: int) -> None:
        self.stack.append(val)
        cur_min = val if not self.mins else min(val, self.mins[-1])
        self.mins.append(cur_min)

    def pop(self) -> None:
        self.stack.pop()
        self.mins.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.mins[-1]


def _test() -> None:
    # Official LeetCode example.
    s = MinStack()
    s.push(-2)
    s.push(0)
    s.push(-3)
    assert s.getMin() == -3       # minimum is -3
    s.pop()
    assert s.top() == 0
    assert s.getMin() == -2       # -3 gone, min back to -2

    # Edge: duplicates of the minimum. Popping one must not lose the min.
    d = MinStack()
    d.push(1)
    d.push(1)
    d.push(0)
    assert d.getMin() == 0
    d.pop()                        # remove the 0
    assert d.getMin() == 1        # two 1s remain
    d.pop()
    assert d.getMin() == 1        # still a 1 left

    # Edge: single element.
    o = MinStack()
    o.push(5)
    assert o.top() == 5
    assert o.getMin() == 5

    print("min_stack: all cases passed")


if __name__ == "__main__":
    _test()
