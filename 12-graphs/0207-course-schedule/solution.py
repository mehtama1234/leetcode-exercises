"""207. Course Schedule — https://leetcode.com/problems/course-schedule/

There are numCourses courses (0..numCourses-1) and prerequisite pairs [a, b]
meaning "to take a you must first take b". Decide whether you can finish all
courses.

Prerequisites form a directed graph. You can finish everything iff there's no
cycle — a cycle means a set of courses that all wait on each other and can never
start. So this is pure cycle detection on a directed graph.
"""
from typing import List
from collections import deque


def can_finish(num_courses: int, prerequisites: List[List[int]]) -> bool:
    """Kahn's algorithm (BFS topological sort). O(V + E) time, O(V + E) space.

    Build the graph b -> a (take b, then a becomes more available) and count each
    course's in-degree = how many prereqs it still waits on. Courses with in-degree
    0 are ready now; queue them. Repeatedly take a ready course, "finish" it, and
    for each course that depended on it, drop that dependency (in-degree -= 1); if
    that course now has no remaining prereqs, it becomes ready too.

    If we manage to finish all num_courses this way, there's a valid order. If we
    stall with courses left, those courses form a cycle (each still waiting on
    another that never got finished) — so it's impossible.
    """
    adj: List[List[int]] = [[] for _ in range(num_courses)]
    indegree = [0] * num_courses
    for course, prereq in prerequisites:
        adj[prereq].append(course)  # finishing prereq unlocks course
        indegree[course] += 1

    # All courses that start with no prerequisites are ready immediately.
    ready = deque(c for c in range(num_courses) if indegree[c] == 0)

    finished = 0
    while ready:
        course = ready.popleft()
        finished += 1
        for nxt in adj[course]:
            indegree[nxt] -= 1          # one prereq satisfied
            if indegree[nxt] == 0:
                ready.append(nxt)       # now unblocked

    return finished == num_courses      # leftover courses => a cycle blocked them


def _test() -> None:
    # Official examples
    assert can_finish(2, [[1, 0]]) is True                 # 0 then 1
    assert can_finish(2, [[1, 0], [0, 1]]) is False        # 0<->1 cycle

    # Edge cases
    assert can_finish(1, []) is True                       # one course, no prereqs
    assert can_finish(3, []) is True                       # no prereqs at all
    # A 3-cycle 0->1->2->0 is impossible.
    assert can_finish(3, [[0, 1], [1, 2], [2, 0]]) is False
    # A valid diamond: 0 needs 1 and 2; both need 3. No cycle.
    assert can_finish(4, [[0, 1], [0, 2], [1, 3], [2, 3]]) is True

    print("can_finish: all cases passed")


if __name__ == "__main__":
    _test()
