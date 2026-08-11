"""Rich full-arc trace for Merge Two Sorted Lists (linked-list renderer).
Arc: the rule (smaller head wins) -> zip a full merge -> edge (one list empty).
Mirrors merge_two_lists in solution.py. Both input lists are shown as one row of
node values: list A first, then list B; the picked node is marked 'good' and
edges chain the answer in the order chosen. Writes trace.json.
"""
import json
import os

frames = []

CODE = [
    "dummy = ListNode(); tail = dummy",
    "while l1 and l2:",
    "    if l1.val <= l2.val:",
    "        tail.next = l1; l1 = l1.next",
    "    else:",
    "        tail.next = l2; l2 = l2.next",
    "    tail = tail.next",
    "tail.next = l1 if l1 else l2",
    "return dummy.next",
]


def add(**f):
    frames.append(f)


# Two sorted lists laid out in one row: A = [1,2,4] at idx 0..2, B = [1,3,4] at 3..5.
A = [1, 2, 4]
B = [1, 3, 4]
vals = A + B                      # [1,2,4,1,3,4]
labels = ["A", "A", "A", "B", "B", "B"]
Aidx = [0, 1, 2]
Bidx = [3, 4, 5]


def base_state(i, j, note_order):
    return


def run_merge(act, first_frame_intro=None, edge=False):
    """Emit frames for a full merge of A and B, chaining picked nodes."""
    i = j = 0            # cursor into A, into B
    picked = []          # sequence of global indices in answer order
    while i < len(A) and j < len(B):
        ai = Aidx[i]
        bj = Bidx[j]
        take_a = A[i] <= B[j]
        chosen = ai if take_a else bj
        marks = {}
        for p in picked:
            marks[str(p)] = "dim"
        marks[str(ai)] = marks.get(str(ai), "active")
        marks[str(bj)] = marks.get(str(bj), "active")
        marks[str(chosen)] = "good"
        # answer chain: consecutive picked -> pointer arrows in answer order
        chain = picked + [chosen]
        edges = [[chain[k], chain[k + 1]] for k in range(len(chain) - 1)]
        edges.append([chosen, None])
        add(act=act, vals=vals if not picked and not edge else None,
            labels=labels if not picked and not edge else None,
            code="merge", line=2 if take_a else 4,
            note=f"Compare heads: A={A[i]} vs B={B[j]}. "
                 f"{'A' if take_a else 'B'}={min(A[i], B[j])} is smaller (or tied), so it goes next.",
            pointers={"l1": ai, "l2": bj, "tail": chosen},
            marks=marks,
            edges=edges,
            state=[["l1 head", A[i]], ["l2 head", B[j]],
                   ["picked", "".join(str(vals[p]) for p in chain)]])
        picked.append(chosen)
        if take_a:
            i += 1
        else:
            j += 1
    # one list exhausted — splice the rest wholesale
    rest_idx = [Aidx[k] for k in range(i, len(A))] + [Bidx[k] for k in range(j, len(B))]
    chain = picked + rest_idx
    edges = [[chain[k], chain[k + 1]] for k in range(len(chain) - 1)]
    edges.append([chain[-1], None])
    marks = {str(p): "dim" for p in picked}
    for p in rest_idx:
        marks[str(p)] = "good"
    which = "l1" if i < len(A) else "l2"
    add(act=act, code="merge", line=7, edges=edges,
        note=f"{'A' if which == 'l1' else 'B'} still has "
             f"{''.join(str(vals[p]) for p in rest_idx)} left, and it is already sorted — "
             f"attach the whole tail at once.",
        pointers={which: rest_idx[0], "tail": picked[-1] if picked else rest_idx[0]},
        marks=marks,
        state=[["remainder", "".join(str(vals[p]) for p in rest_idx)]])
    return chain


# ============ Act 0: the rule ============
add(act=0, vals=vals, labels=labels,
    edges=[[Aidx[k], Aidx[k + 1] if k + 1 < len(A) else None] for k in range(len(A))] +
          [[Bidx[k], Bidx[k + 1] if k + 1 < len(B) else None] for k in range(len(B))],
    code="merge", line=0,
    intro="both lists are already sorted, so the next answer node is always the smaller head.",
    invariant="the answer stays sorted because we only ever attach the current minimum.",
    note="Two sorted lists, A on the left and B on the right (both shown in one row). "
    "We never sort — we just repeatedly take whichever head is smaller.",
    pointers={"l1": 0, "l2": 3},
    state=[["A", "1->2->4"], ["B", "1->3->4"]])

# ============ Act 1: zip a full merge ============
add(act=1, vals=vals, labels=labels,
    edges=[[Aidx[k], Aidx[k + 1] if k + 1 < len(A) else None] for k in range(len(A))] +
          [[Bidx[k], Bidx[k + 1] if k + 1 < len(B) else None] for k in range(len(B))],
    code="merge", line=1,
    intro="a dummy head means we never special-case which list starts the result.",
    invariant="tail always points at the last node placed into the answer.",
    note="Walk both lists together. Each step, attach the smaller head to the answer's "
    "tail and advance that list.",
    pointers={"l1": 0, "l2": 3, "tail": None},
    state=[["l1 head", A[0]], ["l2 head", B[0]]])
final = run_merge(1)

add(act=1, code="merge", line=8,
    edges=[[final[k], final[k + 1]] for k in range(len(final) - 1)] + [[final[-1], None]],
    note="Merged: " + " -> ".join(str(vals[p]) for p in final) +
         ". Every node reused; nothing copied.",
    marks={str(p): "good" for p in final},
    pointers={"head": final[0]},
    state=[["result", "".join(str(vals[p]) for p in final)]],
    banner="Merged: 1 -> 1 -> 2 -> 3 -> 4 -> 4")

# ============ Act 2: edge — one list empty ============
vals2 = [0]
labels2 = ["B"]
add(act=2, vals=vals2, labels=labels2, edges=[[0, None]], code="merge", line=1,
    intro="if one list is empty the loop never runs — just return the other.",
    invariant="an empty list contributes nothing; the other is already the answer.",
    note="Edge case: A is empty, B = [0]. The while loop's condition (l1 and l2) is false "
    "immediately, so we skip straight to attaching the remainder.",
    pointers={"l2": 0, "tail": None}, state=[["A", "empty"], ["B", "0"]])

add(act=2, code="merge", line=7, edges=[[0, None]],
    note="Nothing to compare. Splice B on directly: the merged list is just [0].",
    pointers={"l2": 0}, marks={"0": "good"},
    state=[["result", "0"]],
    banner="One list empty: return the other")

trace = {
    "player": "linkedlist",
    "title": "Merge Two Sorted Lists - always take the smaller head",
    "acts": ["The rule: smaller head wins", "Zip both lists", "Edge: one list empty"],
    "code": {"merge": CODE},
    "legend": [["good", "picked into the answer"], ["active", "heads being compared"],
               ["dim", "already merged"]],
    "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
