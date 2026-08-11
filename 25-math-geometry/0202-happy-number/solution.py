"""202. Happy Number — https://leetcode.com/problems/happy-number/

Replace a number by the sum of the squares of its digits, repeat. If you reach
1 the number is "happy"; if you loop forever without reaching 1 it is not.
Return whether n is happy.

Two implementations are kept side by side so the reason the fast one exists is
visible: the seen-set records every number to detect a repeat, and Floyd's
cycle detection is what you get by asking "can I detect the loop with O(1)
memory?".
"""


def _square_digit_sum(n: int) -> int:
    """Sum of the squares of the digits of n. E.g. 19 -> 1 + 81 = 82."""
    total = 0
    while n > 0:
        n, digit = divmod(n, 10)  # peel off the last digit
        total += digit * digit
    return total


def is_happy_set(n: int) -> bool:
    """Remember every number seen; if one repeats, we're in a loop. O(1)-ish
    time (the sequence provably enters a small range), O(k) space for the set.

    The key realization: the process either reaches 1 or repeats a value it has
    seen before — it cannot run forever producing all-new numbers, because the
    square-digit-sum of any number quickly falls below ~810 and stays bounded.
    So "does it repeat?" is the same question as "is there a cycle?", and a set
    answers "have I seen this?" directly.
    """
    seen: set[int] = set()
    while n != 1 and n not in seen:
        seen.add(n)
        n = _square_digit_sum(n)
    return n == 1


def is_happy(n: int) -> bool:
    """Floyd's tortoise and hare — detect the cycle with O(1) space.

    Key insight: the sequence n, f(n), f(f(n)), ... eventually either hits 1 or
    enters a cycle. Instead of storing every value, run two pointers: `slow`
    advances one step, `fast` advances two. If there is a cycle, the fast
    pointer laps the slow one and they meet inside it. If the sequence reaches 1
    instead, fast hits 1 first and we return True. This is the same technique
    used to find a loop in a linked list — here the "next pointer" is the
    square-digit-sum function.
    """
    slow = n
    fast = _square_digit_sum(n)
    while fast != 1 and slow != fast:
        slow = _square_digit_sum(slow)                    # one step
        fast = _square_digit_sum(_square_digit_sum(fast)) # two steps
    return fast == 1


def _test() -> None:
    cases = [
        (19, True),    # 19 -> 82 -> 68 -> 100 -> 1
        (7, True),     # 7 -> 49 -> 97 -> ... -> 1
        (2, False),    # falls into the 4->16->37->58->89->145->42->20->4 loop
        (1, True),     # already happy
        (0, False),    # 0 -> 0 forever, never 1
    ]
    for n, expected in cases:
        assert is_happy(n) == expected, (n, expected)
        assert is_happy_set(n) == expected, (n, expected)  # both must agree
    print("is_happy: all cases passed")


if __name__ == "__main__":
    _test()
