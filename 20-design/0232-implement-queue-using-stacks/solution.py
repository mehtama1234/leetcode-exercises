"""232. Implement Queue using Stacks — https://leetcode.com/problems/implement-queue-using-stacks/

Build a FIFO queue (push/pop/peek/empty) using only stacks (LIFO structures).
Every operation must be O(1) *amortized*.

A stack reverses order; two stacks reverse it twice, which restores original
order — that is the whole idea. Elements come in on an "in" stack and are moved
to an "out" stack only when needed, so each element is moved at most once.
"""


class MyQueue:
    """FIFO queue from two LIFO stacks. O(1) amortized per operation.

    `s_in` receives new elements. `s_out` serves them. When we need the front and
    `s_out` is empty, we pour all of `s_in` into `s_out`; reversing a reversed
    order gives back arrival order, so the true front ends up on top of `s_out`.

    The key to O(1) amortized cost: each element is pushed to `s_in` once, moved
    to `s_out` once, and popped once — three constant steps over its whole life,
    even though a single `pop` that triggers a transfer looks O(n).
    """

    def __init__(self) -> None:
        self.s_in: list[int] = []   # newest on top
        self.s_out: list[int] = []  # oldest on top (queue front)

    def _shift(self) -> None:
        """Move everything from s_in to s_out, but only when s_out is empty."""
        if not self.s_out:
            while self.s_in:
                self.s_out.append(self.s_in.pop())

    def push(self, x: int) -> None:
        self.s_in.append(x)

    def pop(self) -> int:
        """Remove and return the front (oldest) element."""
        self._shift()
        return self.s_out.pop()

    def peek(self) -> int:
        """Return the front element without removing it."""
        self._shift()
        return self.s_out[-1]

    def empty(self) -> bool:
        return not self.s_in and not self.s_out


def _test() -> None:
    # Official LeetCode example.
    q = MyQueue()
    q.push(1)
    q.push(2)
    assert q.peek() == 1          # front is the oldest, 1
    assert q.pop() == 1
    assert q.empty() is False

    # Edge: interleave pushes and pops so a transfer happens mid-stream.
    r = MyQueue()
    r.push(1)
    assert r.pop() == 1
    r.push(2)
    r.push(3)
    assert r.peek() == 2          # 2 arrived before 3
    r.push(4)
    assert r.pop() == 2
    assert r.pop() == 3
    assert r.pop() == 4           # 4 pushed after transfer still comes last
    assert r.empty() is True

    print("my_queue: all cases passed")


if __name__ == "__main__":
    _test()
