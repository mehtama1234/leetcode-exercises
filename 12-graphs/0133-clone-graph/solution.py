"""133. Clone Graph — https://leetcode.com/problems/clone-graph/

Given a reference to a node in a connected, undirected graph, return a deep copy:
a brand-new graph with the same shape but all-new node objects.

The trick is not the traversal — it's remembering the copies. If you just DFS and
make a new node every time you see one, you'll build duplicates and loop forever
on cycles. A map from "original node -> its clone" gives you both a done-list and
the mirror wiring in one.
"""
from typing import Dict, List, Optional


class Node:
    """The graph node LeetCode hands you. Value + a list of neighbor Nodes."""

    def __init__(self, val: int = 0, neighbors: Optional[List["Node"]] = None):
        self.val = val
        self.neighbors = neighbors if neighbors is not None else []


def clone_graph(node: Optional["Node"]) -> Optional["Node"]:
    """DFS with an original->clone map. O(V + E) time, O(V) space.

    Two things must happen for every node: (1) create its clone exactly once, and
    (2) copy its edges to point at the *clones* of its neighbors. The map does the
    heavy lifting: before recursing into a neighbor we check the map, so a node is
    cloned only the first time we reach it. That single check is also what makes
    cycles safe — the second time we arrive at a node, its clone already exists,
    so we return it instead of recursing forever.
    """
    if node is None:
        return None

    clones: Dict[Node, Node] = {}  # original node -> its freshly-made copy

    def dfs(original: "Node") -> "Node":
        if original in clones:
            return clones[original]  # already copied — hand back the same clone
        copy = Node(original.val)
        clones[original] = copy      # record BEFORE recursing, so cycles terminate
        for nb in original.neighbors:
            copy.neighbors.append(dfs(nb))
        return copy

    return dfs(node)


# ---- helpers so the file runs standalone -----------------------------------

def build_graph(adj: List[List[int]]) -> Optional["Node"]:
    """Build a graph from an adjacency list (LeetCode's input format).

    adj[i] lists the neighbors of the node whose val is i+1 (1-indexed vals).
    Returns the node with val 1, or None for an empty graph.
    """
    if not adj:
        return None
    nodes = {i: Node(i) for i in range(1, len(adj) + 1)}
    for i, neighbors in enumerate(adj, start=1):
        nodes[i].neighbors = [nodes[j] for j in neighbors]
    return nodes[1]


def to_adj(node: Optional["Node"]) -> List[List[int]]:
    """Serialize a graph back to an adjacency list keyed by val order."""
    if node is None:
        return []
    seen: Dict[int, List[int]] = {}
    stack = [node]
    visited = set()
    while stack:
        cur = stack.pop()
        if cur.val in visited:
            continue
        visited.add(cur.val)
        seen[cur.val] = [nb.val for nb in cur.neighbors]
        for nb in cur.neighbors:
            if nb.val not in visited:
                stack.append(nb)
    return [seen[v] for v in sorted(seen)]


def _test() -> None:
    # Official example: 4-node graph, a square 1-2-3-4-1.
    adj = [[2, 4], [1, 3], [2, 4], [1, 3]]
    original = build_graph(adj)
    clone = clone_graph(original)

    # Same shape...
    assert to_adj(clone) == adj

    # ...but genuinely NEW objects (deep copy, not the same references).
    assert clone is not original
    assert clone.neighbors[0] is not original.neighbors[0]

    # Edge cases
    assert clone_graph(None) is None                 # empty graph
    single = build_graph([[]])                        # one node, no neighbors
    single_clone = clone_graph(single)
    assert single_clone is not single
    assert single_clone.val == 1 and single_clone.neighbors == []

    # Two-node graph with a cycle back-edge must terminate and copy correctly.
    assert to_adj(clone_graph(build_graph([[2], [1]]))) == [[2], [1]]

    print("clone_graph: all cases passed")


if __name__ == "__main__":
    _test()
