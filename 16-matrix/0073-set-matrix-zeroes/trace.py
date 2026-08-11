"""Rich full-arc trace for Set Matrix Zeroes (grid renderer).
Arc: brute (two marker sets = extra O(m+n) space, the waste) -> reuse row 0 and
column 0 as markers, in place -> edge (zero touching row 0 and col 0).
Mirrors solution.py. Writes trace.json.
"""
import json
import os

frames = []

CODE_MARK = [
    "for r,c in cells:",
    "    if grid[r][c]==0: zero_rows.add(r); zero_cols.add(c)",
    "for r in range(m):",
    "    for c in range(n):",
    "        if r in zero_rows or c in zero_cols: grid[r][c]=0",
]
CODE_FAST = [
    "for r in range(m):",
    "    if matrix[r][0]==0: first_col_zero=True",
    "    for c in range(1,n):",
    "        if matrix[r][c]==0: matrix[r][0]=0; matrix[0][c]=0",
    "for r in range(1,m):",
    "    for c in range(1,n):",
    "        if matrix[r][0]==0 or matrix[0][c]==0: matrix[r][c]=0",
    "if matrix[0][0]==0: blank row 0",
    "if first_col_zero: blank col 0",
]


def add(**f):
    frames.append(f)


def grid_of(m):
    return [row[:] for row in m]


def rlabels(m):
    return [str(i) for i in range(len(m))]


def clabels(m):
    return [str(i) for i in range(len(m[0]))]


# ---- Act 0: brute — why you can't zero on sight; the marker sets ----
g0 = [[1, 1, 1], [1, 0, 1], [1, 1, 1]]
M, N = 3, 3
add(act=0, rows=grid_of(g0), rowLabels=rlabels(g0), colLabels=clabels(g0),
    code="mark", line=0,
    intro="why blanking a row the moment you see a 0 destroys the grid.",
    invariant="the ORIGINAL zeros decide which rows/cols blank, not the ones we write.",
    note="Brute force: scan for zeros first, remember each zero's row and column in "
    "two sets, then blank in a second pass. Found a 0 at (1,1).",
    marks={"1,1": "bad"},
    state=[["zero_rows", "{1}"], ["zero_cols", "{1}"], ["extra space", "O(m+n)"]])
add(act=0, code="mark", line=4,
    note="Second pass blanks row 1 and column 1 using the sets. Correct — but the two "
    "sets are extra O(m+n) storage. That is the waste we remove.",
    set={"1,0": 0, "1,2": 0, "0,1": 0, "2,1": 0, "1,1": 0},
    marks={"1,0": "good", "1,1": "good", "1,2": "good", "0,1": "good", "2,1": "good"},
    state=[["zero_rows", "{1}"], ["zero_cols", "{1}"], ["extra space", "O(m+n)"]])

# ---- Act 1: reuse row 0 / col 0 as the markers, in place ----
g = [[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]
M, N = 3, 4
add(act=1, rows=grid_of(g), rowLabels=rlabels(g), colLabels=clabels(g),
    code="fast", line=0,
    intro="the grid's own first row and column stand in for the two sets.",
    invariant="row 0 marks which columns to blank; column 0 marks which rows.",
    note="No extra storage: reuse row 0 and column 0 as the markers. Column 0 clashes "
    "with row 0 at (0,0), so track column 0's own zero in one boolean flag first.",
    marks={f"0,{c}": "dim" for c in range(N)}, state=[["first_col_zero", "False"]])

first_col_zero = False
# Step 1: scan and set markers
step1_note = "Scan. When a cell is 0, mark its column in row 0 and its row in column 0."
for r in range(M):
    if g[r][0] == 0:
        first_col_zero = True
        add(act=1, code="fast", line=1,
            note=f"matrix[{r}][0] is 0 -> remember column 0 in the flag.",
            marks={f"{r},0": "active"},
            state=[["first_col_zero", str(first_col_zero)]])
    for c in range(1, N):
        if g[r][c] == 0:
            g[r][0] = 0
            g[0][c] = 0
            add(act=1, code="fast", line=3,
                note=f"matrix[{r}][{c}]=0 -> set marker matrix[{r}][0] and matrix[0][{c}].",
                set={f"{r},0": 0, f"0,{c}": 0},
                marks={f"{r},{c}": "bad", f"{r},0": "active", f"0,{c}": "active"},
                state=[["first_col_zero", str(first_col_zero)]])
# after scan: g[0] = [0,1,2,0] (0,0 stayed 0 from original; 0,3 marked), g[1][0]=0
# markers: matrix[0][3]=0 (col 3), matrix[1][0]=0 (row 1), matrix[0][0]=0, flag True

# Step 2: blank the interior from the markers
add(act=1, code="fast", line=4,
    note="Now blank the interior (r>=1, c>=1) wherever its row marker or column marker "
    "is 0. Markers are still intact because we haven't touched row 0 / column 0.",
    marks={f"0,{c}": "dim" for c in range(N)}, state=[["pass", "interior"]])
for r in range(1, M):
    for c in range(1, N):
        if g[r][0] == 0 or g[0][c] == 0:
            g[r][c] = 0
            why = []
            if g[r][0] == 0:
                why.append(f"row marker ({r},0)")
            if g[0][c] == 0:
                why.append(f"col marker (0,{c})")
            add(act=1, code="fast", line=6,
                note=f"blank ({r},{c}) via " + " and ".join(why) + ".",
                set={f"{r},{c}": 0},
                marks={f"{r},{c}": "good", f"{r},0": "active", f"0,{c}": "active"},
                state=[["pass", "interior"]])

# Step 3: blank row 0 and column 0 last
if g[0][0] == 0:
    for c in range(N):
        g[0][c] = 0
    add(act=1, code="fast", line=7,
        note="matrix[0][0] was 0, so blank all of row 0 now (done last, after its "
        "markers were read).",
        set={f"0,{c}": 0 for c in range(N)},
        marks={f"0,{c}": "good" for c in range(N)}, state=[["row 0", "blanked"]])
if first_col_zero:
    for r in range(M):
        g[r][0] = 0
    add(act=1, code="fast", line=8,
        note="first_col_zero was True, so blank all of column 0 now.",
        set={f"{r},0": 0 for r in range(M)},
        marks={f"{r},0": "good" for r in range(M)}, state=[["col 0", "blanked"]])

assert g == [[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
add(act=1, code="fast", line=8,
    note="Done in place with O(1) extra space: every original zero blanked its row and "
    "column, no chain reaction.",
    marks={f"{r},{c}": ("good" if g[r][c] == 0 else "dim") for r in range(M) for c in range(N)},
    banner="Zeroed in place, O(1) extra space")

# ---- Act 2: edge — zero in the first row AND first column ----
e = [[0, 2, 3], [4, 5, 6]]
ME, NE = 2, 3
add(act=2, rows=grid_of(e), rowLabels=rlabels(e), colLabels=clabels(e),
    code="fast", line=0,
    intro="the (0,0) conflict case: a zero sits in both marker strips.",
    invariant="the col0 flag keeps (0,0) from being overwritten too early.",
    note="Edge case: the only zero is at (0,0), on both marker strips. The flag "
    "captures column 0 up front so it survives.",
    marks={"0,0": "bad"}, state=[["first_col_zero", "False"]])
efcz = False
if e[0][0] == 0:
    efcz = True
    add(act=2, code="fast", line=1, note="matrix[0][0]=0 -> set first_col_zero flag.",
        marks={"0,0": "active"}, state=[["first_col_zero", "True"]])
# no interior zeros to propagate (0,0 is a marker itself)
add(act=2, code="fast", line=4,
    note="Interior (r>=1, c>=1) checks its markers: row 1 marker (1,0)=4 not 0, but "
    "column markers depend on row 0. Only column 0's marker matters here.",
    marks={"0,0": "dim"}, state=[["pass", "interior"]])
# blank row 0 because matrix[0][0]==0
for c in range(NE):
    e[0][c] = 0
add(act=2, code="fast", line=7, note="matrix[0][0]=0 -> blank row 0.",
    set={f"0,{c}": 0 for c in range(NE)},
    marks={f"0,{c}": "good" for c in range(NE)}, state=[["row 0", "blanked"]])
for r in range(ME):
    e[r][0] = 0
add(act=2, code="fast", line=8, note="flag True -> blank column 0.",
    set={f"{r},0": 0 for r in range(ME)},
    marks={f"{r},0": "good" for r in range(ME)}, state=[["col 0", "blanked"]])
assert e == [[0, 0, 0], [0, 5, 6]]
add(act=2, code="fast", line=8, note="Result: [[0,0,0],[0,5,6]]. The (0,0) conflict "
    "is handled by the extra flag, nothing else.",
    marks={f"{r},{c}": ("good" if e[r][c] == 0 else "dim") for r in range(ME) for c in range(NE)},
    banner="(0,0) edge handled")

trace = {
    "player": "grid",
    "title": "Set Matrix Zeroes - reuse row 0 and column 0 as the markers",
    "acts": ["Brute: two marker sets", "In place via row 0 / col 0", "Edge: zero at (0,0)"],
    "code": {"mark": CODE_MARK, "fast": CODE_FAST},
    "legend": [["active", "marker being set / read"], ["good", "blanked to 0 / marker"],
               ["bad", "an original zero"], ["dim", "kept / marker strip"]],
    "rows": grid_of(g0), "frames": frames,
}
out = os.path.join(os.path.dirname(__file__), "trace.json")
json.dump(trace, open(out, "w"), indent=1)
print(f"wrote {out}  ({len(frames)} frames)")
