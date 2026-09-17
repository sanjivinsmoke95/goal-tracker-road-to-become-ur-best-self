"""A small starter corpus of real LeetCode problems.

Because the adapter can't enumerate the full LC problem set, we seed a handful
of well-known problems so the LeetCode Problem-of-the-Day always has real,
verifiable candidates. Extend freely; every entry is a real problem/URL.
"""

from app.services.adapters.leetcode import lc_problem

SEED = [
    lc_problem("two-sum", "Two Sum", "Easy", ["array", "hash-table"]),
    lc_problem("valid-parentheses", "Valid Parentheses", "Easy", ["string", "stack"]),
    lc_problem("merge-two-sorted-lists", "Merge Two Sorted Lists", "Easy", ["linked-list", "recursion"]),
    lc_problem("best-time-to-buy-and-sell-stock", "Best Time to Buy and Sell Stock", "Easy", ["array", "dp"]),
    lc_problem("valid-anagram", "Valid Anagram", "Easy", ["hash-table", "string", "sorting"]),
    lc_problem("binary-search", "Binary Search", "Easy", ["array", "binary-search"]),
    lc_problem("add-two-numbers", "Add Two Numbers", "Medium", ["linked-list", "math"]),
    lc_problem("longest-substring-without-repeating-characters", "Longest Substring Without Repeating Characters", "Medium", ["hash-table", "string", "sliding-window"]),
    lc_problem("3sum", "3Sum", "Medium", ["array", "two-pointers", "sorting"]),
    lc_problem("group-anagrams", "Group Anagrams", "Medium", ["array", "hash-table", "string"]),
    lc_problem("product-of-array-except-self", "Product of Array Except Self", "Medium", ["array", "prefix-sum"]),
    lc_problem("coin-change", "Coin Change", "Medium", ["array", "dp", "bfs"]),
    lc_problem("number-of-islands", "Number of Islands", "Medium", ["array", "dfs", "bfs", "union-find"]),
    lc_problem("course-schedule", "Course Schedule", "Medium", ["graph", "topological-sort"]),
    lc_problem("median-of-two-sorted-arrays", "Median of Two Sorted Arrays", "Hard", ["array", "binary-search", "divide-and-conquer"]),
    lc_problem("trapping-rain-water", "Trapping Rain Water", "Hard", ["array", "two-pointers", "stack", "dp"]),
    lc_problem("word-ladder", "Word Ladder", "Hard", ["hash-table", "string", "bfs"]),
]
