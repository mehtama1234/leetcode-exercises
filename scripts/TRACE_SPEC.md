# Trace authoring spec — build a step-through animation for each problem

You write one `trace.py` per assigned problem folder. It runs the algorithm and
emits `trace.json`, which the site's visualizer replays. **Do not edit
`solution.py` or `README.md`.**

## Read the gold-standard references first (one per renderer)
- linear:     `02-arrays-hashing/0001-two-sum/trace.py`
- tree:       `08-trees/0104-maximum-depth-of-binary-tree/trace.py`
- grid:       `13-dynamic-programming/0062-unique-paths/trace.py`
- linkedlist: `05-linked-list/0206-reverse-linked-list/trace.py`
Match their structure and depth. Look at `scripts/assets/viz.js` if unsure what a
field does.

## Pick the renderer
- **linear** — arrays, two pointers, sliding window, binary search, 1-D DP,
  greedy, bit manipulation, cyclic sort, prefix sum, stacks/heaps-as-array,
  intervals. Cells in a row; named pointers; optional window shade; optional
  `sidebar` (a small table, e.g. a stack or hash map); optional `arc` between two
  cells.
- **tree** — binary trees, BSTs, tries, heaps-as-tree, backtracking decision
  trees, graphs (give each node an x,y), union-find forests. You compute node
  x,y positions in Python.
- **grid** — matrices, 2-D DP tables, grid graphs (islands, etc.), Fenwick/BIT.
- **linkedlist** — linked lists, LRU-style node chains.

## The arc (this is the point)
Tell the whole first-principles story as labeled `acts`, usually:
1. **Brute force** — run the slow idea and let the waste be *visible* (a pointer
   re-sweeping, the same cell recomputed, a counter climbing).
2. **The waste** — name what got repeated; show the work counter's size.
3. **Fast** — the real solution running, the waste gone.
4. **Edge case** — a tricky input (duplicate, empty, single element, all-same,
   lopsided) run through the fast solution.
Adapt when a problem has no wasteful baseline (trees, design): use acts like
"The rule → run it → edge case". 3–4 acts, ~15–35 frames total.

## Trace shape
Top level: `player`, `title`, `acts` (labels), `code` ({blockName: [source
lines]}), `legend` ([[markClass,label]]), `frames`.
Every frame: `act` (int index into acts). Optional: `note` (one plain sentence),
`banner` (result line), `intro` (first frame of an act: "what to watch for"),
`invariant` (what stays true this act), `code` (block name) + `line` (int, the
0-based line to highlight), `state` ([[label, value]] — the live HUD; include a
work counter like ["comparisons", n] so brute-vs-fast is visible).

Renderer-specific frame fields:
- **linear**: `cells` [vals], `labels` [vals], `pointers` {name: idx},
  `marks` {idxStr: "active"|"good"|"bad"|"dim"}, `window` [a,b], `arc` [a,b],
  `sidebar` {title, rows:[[k,v]]}.
- **tree**: `nodes` [{id,val,x,y}], `edges` [[a,b]], `active` [ids],
  `done` {id: value shown as a badge}.
- **grid**: `rows` [[vals; use null for blank]], `rowLabels`, `colLabels`,
  `set` {"r,c": value to write}, `marks` {"r,c": class}.
- **linkedlist**: `vals` [node values], `edges` [[from_idx, to_idx or null]]
  (arrows; forward arcs above, reversed arcs below), `pointers` {name: idx|null},
  `marks` {idxStr: class}.

**Scene rule:** the first frame of a scene must carry the structure (`cells` /
`nodes` / `rows` / `vals`). A later act that changes the input (edge case)
carries the new structure on its first frame — that rebuilds the scene.

## Mark colors (keep meaning consistent + set a legend)
`active` = what we're looking at now; `good` = the answer / a resolved value;
`bad` = discarded / the waste; `dim` = filed away / inactive.

## Correctness
Mirror the real algorithm and **verify every number** you show (grid values,
depths, counts) by computing them, not guessing. A wrong frame is worse than no
animation. Keep `note` plain and short (same voice as the READMEs — no clichés).

## Test before you finish
Run `python3 trace.py` in the folder. It must exit 0 and write `trace.json`.
Then confirm the JSON is valid and has `acts`, `code`, and a reasonable frame
count. If a problem genuinely wouldn't gain from an animation, it's OK to skip it
— say which and why in your report.

Report: which problems got a trace, renderer used, frame count each; which you
skipped and why.
