"""Rich full-arc trace for Course Schedule (tree renderer as a directed graph).
Arc: the rule (finishable == no cycle, peel off in-degree-0 courses) -> run
Kahn's on a diamond that succeeds -> a 3-cycle edge case that stalls. Mirrors
Kahn's BFS in solution.py. Node x,y computed here; badges show in-degree, then
the finish order. Writes trace.json.
"""
import json
import os
from collections import deque

frames = []

CODE = [
    "indegree[c] = # prereqs c still waits on",
    "ready = [c for c in courses if indegree[c] == 0]",
    "while ready:",
    "    course = ready.popleft()",
    "    finished += 1",
    "    for nxt in adj[course]:      # course unlocks nxt",
    "        indegree[nxt] -= 1",
    "        if indegree[nxt] == 0:",
    "            ready.append(nxt)",
    "return finished == num_courses   # else a cycle blocked us",
]


def add(**f):
    frames.append(f)


def build(num, prereqs, pos):
    adj = [[] for _ in range(num)]
    indeg = [0] * num
    for course, prereq in prereqs:
        adj[prereq].append(course)
        indeg[course] += 1
    nodes = [{"id": i, "val": i, "x": pos[i][0], "y": pos[i][1]} for i in range(num)]
    edges = [[prereq, course] for course, prereq in prereqs]  # prereq -> course
    return adj, indeg, nodes, edges


# Diamond: 0 needs 1 and 2; both need 3. Edges point prereq -> course (unlock dir).
POS_A = {3: (110, 0), 1: (0, 120), 2: (220, 120), 0: (110, 230)}
NUM_A = 4
PRE_A = [[0, 1], [0, 2], [1, 3], [2, 3]]
adj_a, indeg_a, nodes_a, edges_a = build(NUM_A, PRE_A, POS_A)


# ---- Act 0: the rule ----
add(act=0, nodes=nodes_a, edges=edges_a, code="dfs", line=0,
    intro="a course is ready the moment its in-degree (unmet prereqs) hits 0.",
    invariant="finishing a course lowers its dependents' in-degree by one.",
    note="Prereqs form a directed graph; edges point prereq -> the course it "
    "unlocks. You can finish everything iff there's no cycle. The badge shows how "
    "many prereqs each course still waits on (its in-degree).",
    active=[], done={i: indeg_a[i] for i in range(NUM_A)},
    state=[["rule", "peel off in-degree 0"]])
ready0 = [c for c in range(NUM_A) if indeg_a[c] == 0]
add(act=0, code="dfs", line=1,
    note=f"Courses with in-degree 0 need no prereqs, so they're ready right now: "
    f"{ready0}. Here only course 3.",
    active=list(ready0), done={i: indeg_a[i] for i in range(NUM_A)},
    state=[["ready", str(ready0)]])

# ---- Act 1: run Kahn's on the diamond ----
adj_a, indeg_a, nodes_a, edges_a = build(NUM_A, PRE_A, POS_A)
add(act=1, nodes=nodes_a, edges=edges_a, code="dfs", line=2,
    intro="each course finishes once; its badge drops to a check when it's done.",
    invariant="finished courses only ever came from in-degree 0.",
    note="Run Kahn's. Take a ready course, finish it, and drop the in-degree of "
    "everything it unlocks; anything that reaches 0 joins the ready queue.",
    active=[], done={i: indeg_a[i] for i in range(NUM_A)},
    state=[["finished", 0], ["of", NUM_A]])
ready = deque(c for c in range(NUM_A) if indeg_a[c] == 0)
finished = 0
done_badges = {i: indeg_a[i] for i in range(NUM_A)}
while ready:
    course = ready.popleft()
    finished += 1
    done_badges[course] = "done"
    add(act=1, code="dfs", line=4,
        note=f"Course {course} has no unmet prereqs — finish it. ({finished}/{NUM_A})",
        active=[course], done=dict(done_badges),
        state=[["finished", finished], ["taking", course]])
    for nxt in adj_a[course]:
        indeg_a[nxt] -= 1
        if done_badges.get(nxt) != "done":
            done_badges[nxt] = indeg_a[nxt]
        add(act=1, code="dfs", line=6,
            note=f"Course {course} unlocked {nxt}: its in-degree drops to "
            f"{indeg_a[nxt]}." + ("  Now ready." if indeg_a[nxt] == 0 else ""),
            active=[course, nxt], done=dict(done_badges),
            state=[["unlocked", nxt], ["its in-degree", indeg_a[nxt]]])
        if indeg_a[nxt] == 0:
            ready.append(nxt)
add(act=1, code="dfs", line=9,
    note=f"Finished all {finished} of {NUM_A} courses — every one reached in-degree 0 "
    f"in turn. No cycle, so the schedule is possible.",
    active=[], done=dict(done_badges),
    state=[["finished", finished], ["of", NUM_A]],
    banner=f"Finishable: all {NUM_A} courses ordered, no cycle")

# ---- Act 2: 3-cycle edge case ----
POS_B = {0: (110, 0), 1: (0, 150), 2: (220, 150)}
NUM_B = 3
PRE_B = [[0, 1], [1, 2], [2, 0]]  # 0<-1<-2<-0 : a cycle
adj_b, indeg_b, nodes_b, edges_b = build(NUM_B, PRE_B, POS_B)
add(act=2, nodes=nodes_b, edges=edges_b, code="dfs", line=1,
    intro="no course ever reaches in-degree 0 — the queue starts empty.",
    invariant="a cycle means every course waits on another that never finishes.",
    note="Edge case: 0 -> 1 -> 2 -> 0, a cycle. Every course has an unmet prereq, "
    "so nothing is ready to start.",
    active=[], done={i: indeg_b[i] for i in range(NUM_B)},
    state=[["all in-degrees", "1"]])
ready_b = deque(c for c in range(NUM_B) if indeg_b[c] == 0)
add(act=2, code="dfs", line=2,
    note="The ready queue is empty from the start, so the loop never runs. 0 of 3 "
    "courses finish — the cycle blocks them all.",
    active=[0, 1, 2], done={i: indeg_b[i] for i in range(NUM_B)},
    state=[["finished", 0], ["of", NUM_B]])
add(act=2, code="dfs", line=9,
    note="finished (0) != num_courses (3): leftover courses form a cycle, each "
    "waiting on the next. Impossible to finish.",
    active=[], done={i: indeg_b[i] for i in range(NUM_B)},
    state=[["finished", 0], ["of", NUM_B]],
    banner="Not finishable: a cycle stalls all 3 courses")

trace = {
    "player": "tree",
    "title": "Course Schedule - peel off zero-prereq courses; a leftover cycle blocks",
    "acts": ["The rule: in-degree 0", "Run Kahn's (diamond)", "Edge: a 3-cycle stalls"],
    "code": {"dfs": CODE},
    "legend": [["active", "current course / unlocked"], ["good", "finished (badge = in-degree)"]],
    "nodes": nodes_a, "edges": edges_a, "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
