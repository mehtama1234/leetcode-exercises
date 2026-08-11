"""853. Car Fleet — https://leetcode.com/problems/car-fleet/

Cars head to a target at their own speeds; a faster car catching a slower one
ahead just bunches up behind it (same speed thereafter). Count how many distinct
fleets reach the target.

One clean solution: sort cars by start position (closest to target first) and use
a stack of arrival times. A car merges into the fleet ahead unless it would reach
the target strictly later than the fleet's leader.
"""
from typing import List


def car_fleet(target: int, position: List[int], speed: List[int]) -> int:
    """Sort by position (nearest target first), stack of arrival times. O(n log n).

    Key insight: a car can never pass the car ahead of it — it can only catch up
    and join. So process cars from the one closest to the target backward. For each
    car compute its *free-running* time to the target, `(target - pos) / spd`.

    Walk the cars in order of decreasing start position. Keep a stack of the
    arrival times of the fleet *leaders* seen so far. A new car:

      - if its arrival time is > the current leader's, it is slower and can never
        catch up: it starts a NEW fleet (push its time — it's a new leader),
      - otherwise it catches the fleet ahead and merges (its own arrival time is
        absorbed; the leader ahead still governs the fleet's arrival).

    The number of times we push a new leader is the number of fleets. This is the
    monotonic-stack idea: the stack of arrival times stays strictly increasing
    from the target outward, and each car is resolved once.
    """
    # pair up and sort by position, closest to the target first
    cars = sorted(zip(position, speed), reverse=True)
    stack: List[float] = []  # arrival times of fleet leaders, target-outward
    for pos, spd in cars:
        time = (target - pos) / spd
        # merge if we arrive no later than the leader ahead; only push when we
        # are strictly slower (arrive later) and thus lead a new fleet.
        if not stack or time > stack[-1]:
            stack.append(time)
        # else: time <= stack[-1] -> we catch the fleet ahead, absorbed
    return len(stack)


def _test() -> None:
    assert car_fleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3]) == 3
    assert car_fleet(10, [3], [3]) == 1
    assert car_fleet(100, [0, 2, 4], [4, 2, 1]) == 1   # all merge into one
    assert car_fleet(10, [6, 8], [3, 2]) == 2          # never catch up
    assert car_fleet(10, [0, 4, 2], [2, 1, 3]) == 1
    assert car_fleet(10, [], []) == 0                  # no cars
    print("car_fleet: all cases passed")


if __name__ == "__main__":
    _test()
