"""Single source of truth for the curriculum.

Each entry: (leetcode_number, title, pattern-slug already implied by chapter).
Chapter tuple: (chapter_number, chapter_title, dir_slug, [problems]).
"""

CHAPTERS = [
    (2, "Arrays & Strings: Manipulation & Hashing", "02-arrays-hashing", [
        (1, "Two Sum"),
        (217, "Contains Duplicate"),
        (242, "Valid Anagram"),
        (49, "Group Anagrams"),
        (347, "Top K Frequent Elements"),
        (392, "Is Subsequence"),
        (128, "Longest Consecutive Sequence"),
        (238, "Product of Array Except Self"),
    ]),
    (3, "Arrays & Strings: Two Pointers", "03-two-pointers", [
        (125, "Valid Palindrome"),
        (167, "Two Sum II - Input Array Is Sorted"),
        (15, "3Sum"),
        (11, "Container With Most Water"),
    ]),
    (4, "Arrays & Strings: Sliding Window", "04-sliding-window", [
        (643, "Maximum Average Subarray I"),
        (121, "Best Time to Buy and Sell Stock"),
        (424, "Longest Repeating Character Replacement"),
        (3, "Longest Substring Without Repeating Characters"),
        (76, "Minimum Window Substring"),
    ]),
    (5, "Linked List: Fast & Slow Pointers", "05-linked-list", [
        (876, "Middle of the Linked List"),
        (141, "Linked List Cycle"),
        (142, "Linked List Cycle II"),
        (206, "Reverse Linked List"),
        (143, "Reorder List"),
        (19, "Remove Nth Node From End of List"),
        (21, "Merge Two Sorted Lists"),
        (23, "Merge k Sorted Lists"),
    ]),
    (6, "Stack", "06-stack", [
        (20, "Valid Parentheses"),
        (739, "Daily Temperatures"),
    ]),
    (7, "Binary Search", "07-binary-search", [
        (704, "Binary Search"),
        (153, "Find Minimum In Rotated Sorted Array"),
        (33, "Search In Rotated Sorted Array"),
    ]),
    (8, "Trees: DFS / BFS", "08-trees", [
        (226, "Invert Binary Tree"),
        (104, "Maximum Depth of Binary Tree"),
        (100, "Same Tree"),
        (572, "Subtree of Another Tree"),
        (235, "Lowest Common Ancestor of a Binary Search Tree"),
        (102, "Binary Tree Level Order Traversal"),
        (98, "Validate Binary Search Tree"),
        (230, "Kth Smallest Element in a BST"),
        (105, "Construct Binary Tree from Preorder and Inorder Traversal"),
        (124, "Binary Tree Maximum Path Sum"),
        (297, "Serialize and Deserialize Binary Tree"),
    ]),
    (9, "Backtracking", "09-backtracking", [
        (39, "Combination Sum"),
        (79, "Word Search"),
    ]),
    (10, "Tries", "10-tries", [
        (208, "Implement Trie (Prefix Tree)"),
        (211, "Design Add and Search Words Data Structure"),
        (212, "Word Search II"),
    ]),
    (11, "Heap / Priority Queue", "11-heap", [
        (295, "Find Median from Data Stream"),
        (703, "Kth Largest Element in a Stream"),
        (1046, "Last Stone Weight"),
        (973, "K Closest Points to Origin"),
        (215, "Kth Largest Element in an Array"),
        (621, "Task Scheduler"),
    ]),
    (12, "Graphs: DFS / BFS / Union Find", "12-graphs", [
        (200, "Number of Islands"),
        (133, "Clone Graph"),
        (417, "Pacific Atlantic Water Flow"),
        (261, "Graph Valid Tree"),
        (323, "Number of Connected Components In An Undirected Graph"),
        (207, "Course Schedule"),
        (269, "Alien Dictionary"),
    ]),
    (13, "Dynamic Programming: Memoization / Tabulation", "13-dynamic-programming", [
        (509, "Fibonacci Number"),
        (322, "Coin Change"),
        (70, "Climbing Stairs"),
        (198, "House Robber"),
        (213, "House Robber II"),
        (647, "Palindromic Substrings"),
        (5, "Longest Palindromic Substring"),
        (152, "Maximum Product Subarray"),
        (91, "Decode Ways"),
        (139, "Word Break"),
        (300, "Longest Increasing Subsequence"),
        (1143, "Longest Common Subsequence"),
        (62, "Unique Paths"),
    ]),
    (14, "Greedy", "14-greedy", [
        (881, "Boats to Save People"),
        (53, "Maximum Subarray"),
        (55, "Jump Game"),
    ]),
    (15, "Merge Intervals", "15-intervals", [
        (56, "Merge Intervals"),
        (57, "Insert Interval"),
        (435, "Non-overlapping Intervals"),
        (252, "Meeting Rooms"),
        (253, "Meeting Rooms II"),
    ]),
    (16, "Matrix", "16-matrix", [
        (48, "Rotate Image"),
        (54, "Spiral Matrix"),
        (73, "Set Matrix Zeroes"),
    ]),
    (17, "Binary: Bit Manipulation", "17-bit-manipulation", [
        (338, "Counting Bits"),
        (268, "Missing Number"),
        (191, "Number of 1 Bits"),
        (190, "Reverse Bits"),
        (371, "Sum of Two Integers"),
    ]),
    # --- Expansion beyond the original course: fills the gaps vs NeetCode 250
    # + Grokking patterns (advanced graphs, 2-D DP, design, subsets, monotonic
    # stack, prefix sum, cyclic sort, math, advanced data structures). ---
    (18, "Advanced Graphs: Shortest Paths & MST", "18-advanced-graphs", [
        (743, "Network Delay Time"),
        (1584, "Min Cost to Connect All Points"),
        (787, "Cheapest Flights Within K Stops"),
        (778, "Swim in Rising Water"),
        (332, "Reconstruct Itinerary"),
    ]),
    (19, "2-D Dynamic Programming", "19-2d-dynamic-programming", [
        (309, "Best Time to Buy and Sell Stock with Cooldown"),
        (518, "Coin Change II"),
        (494, "Target Sum"),
        (97, "Interleaving String"),
        (329, "Longest Increasing Path in a Matrix"),
        (115, "Distinct Subsequences"),
        (72, "Edit Distance"),
        (312, "Burst Balloons"),
        (10, "Regular Expression Matching"),
    ]),
    (20, "Design", "20-design", [
        (146, "LRU Cache"),
        (155, "Min Stack"),
        (232, "Implement Queue using Stacks"),
        (355, "Design Twitter"),
        (981, "Time Based Key-Value Store"),
        (380, "Insert Delete GetRandom O(1)"),
        (460, "LFU Cache"),
    ]),
    (21, "Subsets & Combinatorial Backtracking", "21-subsets", [
        (78, "Subsets"),
        (90, "Subsets II"),
        (46, "Permutations"),
        (47, "Permutations II"),
        (77, "Combinations"),
        (17, "Letter Combinations of a Phone Number"),
        (131, "Palindrome Partitioning"),
        (51, "N-Queens"),
    ]),
    (22, "Monotonic Stack", "22-monotonic-stack", [
        (84, "Largest Rectangle in Histogram"),
        (42, "Trapping Rain Water"),
        (853, "Car Fleet"),
        (496, "Next Greater Element I"),
        (901, "Online Stock Span"),
    ]),
    (23, "Prefix Sum", "23-prefix-sum", [
        (303, "Range Sum Query - Immutable"),
        (304, "Range Sum Query 2D - Immutable"),
        (560, "Subarray Sum Equals K"),
        (525, "Contiguous Array"),
    ]),
    (24, "Cyclic Sort & Index Tricks", "24-cyclic-sort", [
        (41, "First Missing Positive"),
        (442, "Find All Duplicates in an Array"),
        (448, "Find All Numbers Disappeared in an Array"),
        (287, "Find the Duplicate Number"),
    ]),
    (25, "Math & Geometry", "25-math-geometry", [
        (50, "Pow(x, n)"),
        (202, "Happy Number"),
        (66, "Plus One"),
        (43, "Multiply Strings"),
        (7, "Reverse Integer"),
        (9, "Palindrome Number"),
    ]),
    (26, "Advanced Data Structures: Segment Tree, BIT, Union-Find", "26-advanced-ds", [
        (307, "Range Sum Query - Mutable"),
        (684, "Redundant Connection"),
        (547, "Number of Provinces"),
        (315, "Count of Smaller Numbers After Self"),
    ]),
]


def slugify(number, title):
    import re
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return f"{number:04d}-{s}"


def all_problems():
    for ch_no, ch_title, ch_slug, problems in CHAPTERS:
        for num, title in problems:
            yield ch_no, ch_title, ch_slug, num, title


def total_count():
    return sum(len(p) for _, _, _, p in CHAPTERS)
