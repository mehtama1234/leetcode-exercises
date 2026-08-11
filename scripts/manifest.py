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
