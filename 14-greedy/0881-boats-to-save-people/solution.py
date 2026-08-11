"""881. Boats to Save People — https://leetcode.com/problems/boats-to-save-people/

Each boat carries at most two people and has a weight limit. Given each person's
weight and the limit, return the fewest boats needed to carry everyone.
"""
from typing import List


def num_rescue_boats(people: List[int], limit: int) -> int:
    """Sort, then pair the heaviest with the lightest. O(n log n) time, O(1) extra.

    Greedy choice: sort people, put a pointer at each end. The heaviest person
    (right) must go on a boat no matter what. Ask the cheapest possible question:
    can the *lightest* remaining person (left) ride along? If yes, seat both and
    move both pointers in; if no, the heavy one goes alone and we move only the
    right pointer. Either way one boat is committed per step.

    Why this is safe — the exchange argument: the heaviest person H sails in some
    boat. If any partner fits with H at all, the lightest person L fits (L is the
    lightest of everyone). Pairing H with L can never be worse than pairing H with
    someone heavier: whoever we'd otherwise have paired with H still fits beside L
    too (they're >= L in weight but the boat held them next to the heavier H, so
    it holds them next to the lighter L). So there's always an optimal solution
    that pairs H with L — taking that pairing greedily loses nothing.

    If we were greedy the other way (pair two heavy people), we'd routinely waste
    a boat's second seat: two heavy people rarely fit together, and the light
    people then also each need their own boats.
    """
    people.sort()
    left, right = 0, len(people) - 1
    boats = 0
    while left <= right:
        # The heaviest (right) always boards this boat.
        # If the lightest (left) also fits, take them along.
        if people[left] + people[right] <= limit:
            left += 1
        right -= 1
        boats += 1
    return boats


def _test() -> None:
    cases = [
        (([1, 2], 3), 1),
        (([3, 2, 2, 1], 3), 3),
        (([3, 5, 3, 4], 5), 4),
        # everyone must go solo: no two fit together
        (([5, 5, 5, 5], 6), 4),
        # everyone pairs up perfectly
        (([1, 1, 2, 2], 3), 2),
        # single person
        (([4], 5), 1),
    ]
    for (people, limit), expected in cases:
        assert num_rescue_boats(people, limit) == expected, (people, limit)
    print("num_rescue_boats: all cases passed")


if __name__ == "__main__":
    _test()
