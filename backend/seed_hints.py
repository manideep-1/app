"""
Problem-specific hints (LeetCode-style progressive hints).
Keys are problem titles; values are lists of hints shown in order.
"""

PROBLEM_HINTS = {
    "Two Sum": [
        "A hash map lets you look up whether (target - current) was already seen in O(1).",
        "Iterate once: for each element, check if (target - nums[i]) is in the map; if yes return [map[target - nums[i]], i]; else store nums[i] -> i.",
        "Edge cases: exactly one solution guaranteed; same element cannot be used twice.",
    ],
    "3Sum": [
        "Sort the array first. For each index i, use two pointers (left = i+1, right = n-1) to find pairs that sum to -nums[i].",
        "If nums[i] + nums[left] + nums[right] == 0, record the triplet and skip duplicates by moving left/right past same values.",
        "If sum < 0, move left forward; if sum > 0, move right backward. Skip duplicate nums[i] by advancing i while nums[i] == nums[i-1].",
    ],
    "Contains Duplicate": [
        "A hash set lets you check in O(1) whether you've already seen an element.",
        "Iterate through the array; if the current element is in the set, return True; otherwise add it.",
        "Empty array and single element are edge cases (no duplicates).",
    ],
    "Valid Anagram": [
        "Two anagrams have the same character counts. Use a single array of 26 counts (or a hash map).",
        "Increment counts for s, decrement for t. If any count is non-zero at the end, they are not anagrams.",
        "If lengths differ, return false immediately.",
    ],
    "Best Time to Buy and Sell Stock": [
        "Track the minimum price seen so far and the maximum profit so far.",
        "For each day, profit = price - minPrice; update minPrice = min(minPrice, price) and maxProfit = max(maxProfit, profit).",
        "Single pass O(n). Edge case: no profit possible (return 0).",
    ],
    "Valid Palindrome": [
        "Use two pointers: one at the start, one at the end. Move them inward, skipping non-alphanumeric characters.",
        "Compare characters (case-insensitive). If they ever differ, return false.",
        "Handle empty string and single character (both are palindromes).",
    ],
    "Product of Array Except Self": [
        "You cannot use division. Use two passes: one for prefix products, one for suffix products.",
        "Or: output[i] = prefix[i-1] * suffix[i+1], where prefix[i] = product of nums[0..i] and suffix[i] = product of nums[i..n-1].",
        "Space O(1) follow-up: use the output array to store prefix, then multiply by suffix in a second pass from the right.",
    ],
    "Maximum Product Subarray": [
        "Track both max and min product ending at current index (negative can become max when multiplied by another negative).",
        "maxHere = max(nums[i], maxHere * nums[i], minHere * nums[i]); minHere = min(nums[i], maxHere * nums[i], minHere * nums[i]).",
        "Update global max from maxHere. Handle zeros (reset or include).",
    ],
    "Container With Most Water": [
        "Two pointers at left=0 and right=n-1. Area = min(height[left], height[right]) * (right - left).",
        "Move the pointer that points to the shorter line inward (only the shorter height limits the area).",
        "Track the maximum area seen. Stop when left >= right.",
    ],
    "Longest Substring Without Repeating Characters": [
        "Use a sliding window (left, right) and a set (or map) of characters in the current window.",
        "Expand right: if s[right] is already in the set, move left forward and remove s[left] until s[right] can be added.",
        "Update max length as right - left + 1 after each expansion. O(n) time.",
    ],
    "Longest Palindromic Substring": [
        "For each index (and between indices), expand outward while characters match. Track the longest palindrome.",
        "Handle odd length (center at i) and even length (center between i and i+1) in the expansion.",
        "Alternatively, use dynamic programming: dp[i][j] = true if s[i..j] is a palindrome.",
    ],
    "Climbing Stairs": [
        "Same as Fibonacci: ways(n) = ways(n-1) + ways(n-2). Use two variables to avoid full DP array.",
        "Base cases: ways(1)=1, ways(2)=2. Iterate from 3 to n.",
        "Can also use a single recurrence with prev and curr.",
    ],
    "House Robber": [
        "At each house, either rob it (add to profit from two houses back) or skip (keep profit from previous house).",
        "dp[i] = max(dp[i-1], nums[i] + dp[i-2]). Use two variables for O(1) space.",
        "Edge: empty array, one house, two houses.",
    ],
    "Group Anagrams": [
        "Two strings are anagrams iff their sorted versions are equal, or their character counts are equal.",
        "Use a map: key = tuple of character counts (or sorted string), value = list of strings.",
        "Return the list of values. O(n * k log k) with sort; O(n * k) with count array as key.",
    ],
    "Single Number": [
        "XOR of a number with itself is 0. XOR of 0 with x is x. XOR is commutative and associative.",
        "XOR all numbers: duplicates cancel, the single number remains.",
        "One pass, O(1) space.",
    ],
    "Number of 1 Bits": [
        "Repeatedly take n & (n-1) to clear the rightmost 1. Count how many times until n becomes 0.",
        "Alternatively, shift n right and count the lowest bit: count += n & 1; n >>= 1.",
        "n & (n-1) trick: each iteration removes one 1 bit.",
    ],
    "Reverse Bits": [
        "Extract the lowest bit of n, add it to result, then shift result left and n right. Do 32 times.",
        "Or: result = (result << 1) | (n & 1); n >>= 1; in a loop of 32.",
        "Handle unsigned 32-bit: ensure result is truncated to 32 bits if needed.",
    ],
    "Missing Number": [
        "Sum of 0..n is n*(n+1)/2. Subtract the sum of the array to get the missing number.",
        "Or use XOR: XOR all indices 0..n and all array elements; duplicates cancel, missing number remains.",
        "Edge: n=0 (array empty, missing is 0).",
    ],
    "Remove Duplicates from Sorted Array": [
        "Two pointers: write index (next position to write) and read index. Only write when nums[read] != nums[write-1].",
        "Increment read each time. When you see a new value, write it at write and increment write.",
        "Return write (number of unique elements).",
    ],
    "Sort Colors": [
        "Dutch national flag: three pointers - low (0s), mid (1s), high (2s). mid scans the array.",
        "If nums[mid]==0, swap with low and advance low and mid. If nums[mid]==2, swap with high and decrement high. If nums[mid]==1, just mid++.",
        "Loop while mid <= high.",
    ],
    "Reverse String": [
        "Use two pointers: one at the start, one at the end. Swap characters at both pointers and move them inward.",
        "Only iterate until the pointers meet in the middle to avoid swapping back.",
    ],
    "Valid Parentheses": [
        "Use a stack: push opening brackets, and for each closing bracket pop and check it matches the top.",
        "If you see a closing bracket when the stack is empty or top doesn't match, return false. At the end the stack must be empty.",
    ],
    "Merge Two Sorted Lists": [
        "Use a dummy head and two pointers, one per list. Compare current nodes and link the smaller one to the result.",
        "When one list is exhausted, attach the rest of the other list.",
    ],
    "Maximum Subarray": [
        "Kadane's algorithm: at each index, either extend the current subarray (current_sum + num) or start fresh (num).",
        "Track the maximum sum seen so far. One pass, O(1) space.",
    ],
    "Min Stack": [
        "Keep a second stack (or structure) that stores the minimum value at each level so getMin is O(1).",
        "On push: push value to main stack; push min(new value, current min) to min stack. On pop: pop from both.",
    ],
    "Pascal's Triangle": [
        "Row 0 is [1]. Each next row: start with 1, then sum of adjacent values from previous row, then end with 1.",
        "Build row i from row i-1: row[j] = prev[j-1] + prev[j] for 1 <= j < i.",
    ],
    "Search in Rotated Sorted Array": [
        "Binary search: determine which half (left or right of mid) is sorted by comparing mid with left/right.",
        "If target lies in the sorted half, search there; otherwise search the other half.",
    ],
    "Find Minimum in Rotated Sorted Array": [
        "Binary search: compare mid with the right end. If nums[mid] > nums[right], minimum is in the right half.",
        "Otherwise minimum is in the left half (including mid). Narrow until left == right.",
    ],
    "Binary Search": [
        "Maintain left and right. While left <= right: mid = (left+right)//2; if nums[mid] == target return mid.",
        "If nums[mid] < target search right (left = mid+1); else search left (right = mid-1).",
    ],
    "First Bad Version": [
        "Binary search over versions 1..n: if mid is bad, first bad is mid or left; else search right.",
        "Minimize API calls by using binary search instead of linear scan.",
    ],
    "Search Insert Position": [
        "Binary search for the smallest index i such that nums[i] >= target. If found return that index; else return n.",
        "Standard lower_bound / bisect_left pattern.",
    ],
    "Squares of a Sorted Array": [
        "Largest squares are at the ends (most negative or most positive). Use two pointers at start and end.",
        "Compare squares, add the larger to the result from the end, and move the pointer that contributed.",
    ],
    "Rotate Array": [
        "Reverse the entire array, then reverse the first k elements and the last n-k elements.",
        "Or: rotate one step k % n times (slower).",
    ],
    "Move Zeroes": [
        "Use a write index: scan the array; for each non-zero, write it at the write index and increment.",
        "Fill the remaining positions with zeros. Single pass, in-place.",
    ],
    "Two Sum II - Input Array Is Sorted": [
        "Two pointers at left=0 and right=n-1. If sum == target return [left+1, right+1] (1-indexed).",
        "If sum < target move left forward; if sum > target move right backward.",
    ],
    "Reverse Words in a String": [
        "Split by spaces, reverse the list of words, then join with a single space. Trim leading/trailing.",
        "Or reverse the whole string then reverse each word for in-place in languages that allow it.",
    ],
    "Longest Consecutive Sequence": [
        "Put all numbers in a set. For each num, if num-1 is not in the set (start of a run), count forward (num, num+1, ...).",
        "Track the maximum run length. Each number is visited at most twice → O(n).",
    ],
    "Isomorphic Strings": [
        "Use two maps: s -> t and t -> s. For each index, ensure s[i] maps to t[i] and t[i] maps to s[i] consistently.",
        "If a character was already mapped to something different, return false.",
    ],
    "Happy Number": [
        "Simulate the process; use a set to detect cycles. If you see 1 return true; if you see a number again return false.",
        "Sum of squares of digits: extract digits with n % 10 and n // 10 in a loop.",
    ],
    "Count Primes": [
        "Sieve of Eratosthenes: mark multiples of each prime starting from 2. Multiples of p start at p*p.",
        "Count unmarked numbers at the end. O(n log log n) time, O(n) space.",
    ],
    "Plus One": [
        "Add 1 from the least significant digit. Carry over; if all 9s, result is 1 followed by zeros.",
        "Work from right to left; stop when no carry.",
    ],
    "Sqrt(x)": [
        "Binary search in [0, x] for the largest integer m such that m*m <= x.",
        "Use long or avoid overflow: compare with x using m <= x // m if needed.",
    ],
    "Merge Intervals": [
        "Sort intervals by start. Then merge: if current overlaps with the last in result, extend the end; else append.",
        "Overlap when current.start <= result[-1].end.",
    ],
    "Insert Interval": [
        "Find where the new interval fits (all intervals before with end < new.start). Then merge all that overlap with new.",
        "Add non-overlapping intervals after. One pass.",
    ],
    "Jump Game": [
        "Track the farthest index you can reach. For each i, if i > farthest return false.",
        "Update farthest = max(farthest, i + nums[i]). If farthest >= n-1 return true.",
    ],
    "Jump Game II": [
        "Greedy: track current jump end and farthest. When i reaches current end, take a jump (jump++) and set current end = farthest.",
        "Ensure you don't go past the last index.",
    ],
    "Unique Paths": [
        "DP: dp[i][j] = number of ways to reach (i,j). dp[i][j] = dp[i-1][j] + dp[i][j-1]. Base: first row and column are 1.",
        "Or use combinatorics: (m+n-2) choose (n-1).",
    ],
    "Minimum Path Sum": [
        "DP: dp[i][j] = grid[i][j] + min(dp[i+1][j], dp[i][j+1]). Fill from bottom-right to top-left.",
        "Can use one row or the grid itself for space O(n) or O(1).",
    ],
    "Coin Change": [
        "DP: dp[a] = minimum coins for amount a. dp[0]=0; for each coin c, dp[a] = min(dp[a], 1 + dp[a-c]) for a >= c.",
        "If dp[amount] is still infinity, return -1.",
    ],
    "Word Break": [
        "DP: dp[i] = true if s[0:i] can be segmented. dp[0]=true. For each i, try all words that end at i.",
        "If s[j:i] is a word and dp[j] is true, then dp[i] = true.",
    ],
    "Combination Sum": [
        "Backtracking: at each step, try adding each candidate (same number can be used repeatedly).",
        "If current sum equals target, record the combination. If sum exceeds target, backtrack.",
    ],
    "Permutations": [
        "Backtracking: swap or track used. For each position, try every unused element.",
        "When the current path has n elements, record it and backtrack.",
    ],
    "Subsets": [
        "Backtracking: for each index, either include the element or skip. When you've considered all elements, add current list to result.",
        "Or iterative: start with [[]]; for each num, append num to every existing subset and add to result.",
    ],
    "Generate Parentheses": [
        "Backtrack: add '(' when open < n and ')' when close < open. When open == close == n, record the string.",
        "Maintain counts of open and close parentheses used.",
    ],
    "Letter Combinations of a Phone Number": [
        "Backtracking or BFS: for each digit, extend current strings with each letter the digit maps to.",
        "Digits 2-9 map to 3–4 letters. Build all combinations level by level.",
    ],
    "Kth Largest Element in an Array": [
        "Quickselect: partition like quicksort; if pivot is at index n-k return it, else recurse on left or right.",
        "Or use a min-heap of size k: push all; pop until size k; then top is kth largest. Or sort and index.",
    ],
    "Top K Frequent Elements": [
        "Count frequencies with a hash map. Then bucket sort: bucket[i] = list of elements with frequency i.",
        "Scan from the highest bucket and collect until you have k elements.",
    ],
    "Implement Stack using Queues": [
        "Use one queue: on push, add to queue then rotate so the new element is at the front (pop n-1 and re-enqueue).",
        "Then pop and top are O(1). Alternative: two queues, keep one empty and swap after push.",
    ],
    "Implement Queue using Stacks": [
        "Two stacks: input stack for push; output stack for pop/peek. When output is empty, pop all from input into output.",
        "Then pop and peek read from output. Amortized O(1) per operation.",
    ],
    "Evaluate Reverse Polish Notation": [
        "Use a stack. For each token: if number, push; if operator, pop two operands, compute, push result.",
        "Note order: second popped is left operand for minus and divide.",
    ],
    "Largest Rectangle in Histogram": [
        "For each bar, the largest rectangle with that bar as height extends until a smaller bar on left and right.",
        "Use a stack to find previous smaller and next smaller for each index; then area = height * (next_smaller - prev_smaller - 1).",
    ],
    "Reverse Linked List": [
        "Iterative: maintain prev, curr, next. While curr: next = curr.next; curr.next = prev; prev = curr; curr = next. Return prev.",
        "Recursive: reverse rest, then point next node's next to current; current.next = null.",
    ],
    "Linked List Cycle": [
        "Floyd's cycle detection: slow and fast pointers. If there is a cycle they eventually meet.",
        "If fast reaches null, no cycle. Start both at head; slow = slow.next, fast = fast.next.next.",
    ],
    "Remove Nth Node From End of List": [
        "Two pointers: advance first by n steps, then move both until first reaches end. Second is at (n+1)th from end.",
        "Remove the node after second. Use a dummy head to handle removing the first node.",
    ],
    "Reorder List": [
        "Find middle, reverse the second half, then merge the first half and reversed second half alternately.",
        "Use slow/fast to find middle; reverse from mid; then interleave two lists.",
    ],
    "Maximum Depth of Binary Tree": [
        "Recursion: if root is null return 0; else return 1 + max(depth(left), depth(right)).",
        "Or BFS: count levels. O(n) time.",
    ],
    "Same Tree": [
        "Recursion: if both null return true; if one null or values differ return false; return sameTree(p.left, q.left) and sameTree(p.right, q.right).",
    ],
    "Invert Binary Tree": [
        "Recursion: swap left and right children, then invert(left) and invert(right). Base: if null return null.",
    ],
    "Symmetric Tree": [
        "Two trees are mirrors if roots are equal and left of one is mirror of right of other. Call helper(root, root).",
        "Helper(p, q): if both null return true; if one null or p.val != q.val return false; return mirror(p.left, q.right) and mirror(p.right, q.left).",
    ],
    "Binary Tree Level Order Traversal": [
        "BFS with a queue: process level by level. For each level, take current queue size and poll that many nodes; add children.",
        "Append each level's values to the result.",
    ],
    "Validate Binary Search Tree": [
        "Recursion: pass (min, max) allowed range. For root, check min < root.val < max; then recurse left with (min, root.val) and right with (root.val, max).",
        "Or inorder traversal: values must be strictly increasing.",
    ],
    "Lowest Common Ancestor of a BST": [
        "Use BST property: if p and q are both less than root, LCA is in left; both greater then right; else root is LCA.",
        "Iterative or recursive. Single traversal.",
    ],
    "Binary Tree Maximum Path Sum": [
        "For each node, max path through node = node.val + max(0, left_gain) + max(0, right_gain).",
        "Recursion: return the max gain from this node (node + one branch); update a global max with path through node.",
    ],
    "Serialize and Deserialize Binary Tree": [
        "Serialize: e.g. preorder with 'null' for null nodes. Deserialize: read next token; if 'null' return null; else build node and recurse left and right.",
        "Alternative: level-order with nulls. Same idea: encode structure so you can reconstruct.",
    ],
    "Number of Islands": [
        "DFS or BFS from each unvisited '1'. Each connected component of '1's is one island. Mark visited (e.g. set to '0').",
        "Count how many times you start a DFS/BFS from a '1'.",
    ],
    "Clone Graph": [
        "BFS or DFS with a map: old node -> new node. When you see a neighbor not yet cloned, create clone and add to queue/stack.",
        "Copy neighbors list for each node. Handle null and single-node graph.",
    ],
    "Pacific Atlantic Water Flow": [
        "From Pacific (top/left) do DFS marking reachable cells. From Atlantic (bottom/right) do DFS marking reachable.",
        "Return cells that are reachable from both. Or reverse: from borders inward by height.",
    ],
    "Course Schedule": [
        "Build graph: edge from b to a for each [a, b]. Detect cycle: if cycle exists return false. Use DFS with three states (unvisited, visiting, done) or Kahn's algorithm.",
        "Topological sort: if you can build a valid order, return true.",
    ],
    "Implement Trie": [
        "Each node has children (dict or array of 26) and a flag is_end. Insert: traverse and create nodes; set is_end at last. Search: traverse and check is_end. startsWith: traverse and check if path exists.",
    ],
    "Add and Search Word": [
        "Use a Trie for storage. For search with '.', at that node try all children (or all 26) recursively.",
        "If character is a letter, go to that child only. Base: when word ends check is_end.",
    ],
    "Word Search II": [
        "Build a Trie from the words. For each cell on the board, DFS and traverse the Trie; when you hit a word end add to result.",
        "Prune when the current path is not a prefix of any word. Mark board cell visited during DFS, unmark on backtrack.",
    ],
    "LRU Cache": [
        "Use a hash map for key -> node and a doubly linked list for order (most recent at head). get: move to head if exists. put: if exists update and move to head; else add at head, evict tail if over capacity.",
        "Need O(1) get and put: map gives O(1) access; list gives O(1) add/remove for LRU order.",
    ],
    "K Closest Points to Origin": [
        "Use a max-heap of size k (by distance). For each point, if heap size < k push; else if distance < heap top, pop and push.",
        "Or quickselect by distance. Or sort by distance and take first k. Output the k points.",
    ],
    "Merge k Sorted Lists": [
        "Push the head of each list into a min-heap (value, list_index). Repeatedly pop smallest, add to result, push next from that list.",
        "O(N log k) where N is total nodes and k is number of lists.",
    ],
    "Find Median from Data Stream": [
        "Two heaps: max-heap for lower half, min-heap for upper half. Keep sizes balanced (differ by at most 1).",
        "Median is top of max-heap (if lower half is larger) or average of two tops (if equal size).",
    ],
    "Sliding Window Maximum": [
        "Use a deque that stores indices; values in the deque are in decreasing order. For each new element, pop from back while back value < new; then push back index.",
        "Front of deque is max of current window. Pop front when it's outside the window.",
    ],
    "Minimum Window Substring": [
        "Sliding window: expand right until the window has all chars of t (counts). Then shrink left while window still valid; track minimum length.",
        "Use two maps: need (from t) and have (current window). When have[c] >= need[c] for all c, window is valid.",
    ],
    "Longest Repeating Character Replacement": [
        "Sliding window: for each right, count chars in window. Window is valid if (length - max_count) <= k. If invalid, move left.",
        "Track max frequency in current window. Longest valid window length is the answer.",
    ],
    "Palindromic Substrings": [
        "For each center (index or between two indices), expand outward while characters match. Count each palindrome found.",
        "Or DP: dp[i][j] = true if s[i..j] is palindrome; count all true. O(n^2) time.",
    ],
    "Decode Ways": [
        "DP: dp[i] = number of ways to decode s[0:i]. dp[0]=1. One digit: if s[i-1] in '1'..'9' add dp[i-1]. Two digits: if s[i-2:i] in 10..26 add dp[i-2].",
        "Handle '0' carefully: single '0' is invalid; '10' and '20' are valid.",
    ],
    "Unique Binary Search Trees": [
        "Catalan number: G(n) = sum over j of G(j-1)*G(n-j) for root j. G(0)=G(1)=1. DP: fill G[0..n].",
    ],
    "Maximum Product of Word Lengths": [
        "For each word, compute a bitmask of which letters appear (bit 0 = 'a', etc.). Two words don't share letters iff mask1 & mask2 == 0.",
        "For each pair with zero intersection, update max product of lengths. O(n^2) with small constant.",
    ],
    "Partition Equal Subset Sum": [
        "Subset sum: if total is odd return false. Check if there is a subset with sum total/2. DP: dp[j] = true if some subset sums to j.",
        "dp[0]=true; for each num, from sum down to num: dp[j] |= dp[j-num].",
    ],
    "Partition to K Equal Sum Subsets": [
        "If total not divisible by k return false. Target = total/k. Backtracking: assign each number to one of k buckets; each bucket must sum to target.",
        "Prune: sort descending; if current bucket + num > target skip; if we've seen this state (e.g. used mask) skip.",
    ],
    "Target Sum": [
        "At each index, try adding +nums[i] or -nums[i]. Recurse; count ways when you reach end with sum == target. Memoize (index, current_sum).",
        "Or convert to subset sum: find subsets with sum = (target + total) / 2. Use 1D DP. Handle (target + total) odd or negative.",
    ],
    "Longest Increasing Subsequence": [
        "DP: dp[i] = length of LIS ending at i. dp[i] = 1 + max(dp[j]) for j < i and nums[j] < nums[i]. Answer = max(dp).",
        "Or patience sorting: maintain a list of tails; binary search to extend or start new pile. O(n log n).",
    ],
    "Longest Common Subsequence": [
        "DP: dp[i][j] = LCS of text1[0:i] and text2[0:j]. If text1[i-1]==text2[j-1] then dp[i][j]=1+dp[i-1][j-1]; else dp[i][j]=max(dp[i-1][j], dp[i][j-1]).",
    ],
    "Edit Distance": [
        "DP: dp[i][j] = min operations to convert word1[0:i] to word2[0:j]. Insert: 1+dp[i][j-1]; Delete: 1+dp[i-1][j]; Replace or same: dp[i-1][j-1] + (0 if same else 1).",
        "Base: dp[0][j]=j, dp[i][0]=i.",
    ],
    "Word Break II": [
        "Backtracking with memo: for each prefix that is a word, recurse on remainder and combine. Memo: s -> list of sentences.",
        "Return memo[s] = [word + (' ' + rest) for word in words for rest in recur(s[len(word):])].",
    ],
    "N-Queens": [
        "Backtrack row by row. For each row, try each column; check no conflict with previous queens (same col, same diagonal: row-col or row+col).",
        "Store column positions; diagonals: row-col and row+col must be unique.",
    ],
    "N-Queens II": [
        "Same as N-Queens but only count solutions. Use same backtracking; increment count when a valid placement is found for the last row.",
    ],
    "Maximum XOR of Two Numbers in an Array": [
        "For each number build a binary Trie (bits from high to low). For each number, traverse Trie trying the opposite bit when available to maximize XOR.",
        "Query: go down the path that gives 1 in that bit when possible. Track max XOR.",
    ],
    "Count of Smaller Numbers After Self": [
        "From right to left, insert elements into a sorted structure (e.g. Fenwick tree or sorted list with bisect). Count how many smaller are already present.",
        "Or merge sort: during merge, count inversions where right is smaller.",
    ],
    "Remove Invalid Parentheses": [
        "First find minimum removals: count unmatched '(' and ')'. Then BFS: remove one char at a time, check if valid; if valid add to result; use set to avoid duplicates.",
        "Or DFS: try removing each redundant ')' then each redundant '('; recurse and collect valid strings.",
    ],
    "Find the Duplicate Number": [
        "Floyd's cycle detection: treat array as linked list (i -> nums[i]). There is a cycle because of the duplicate. Find cycle start.",
        "Or binary search on value: count how many elements <= mid; if count > mid, duplicate is in [1..mid].",
    ],
    "Trapping Rain Water": [
        "For each index, water trapped = min(max height to left, max height to right) - height[i]. Precompute prefix max and suffix max, or use two pointers.",
        "Two pointers: left and right; track maxLeft and maxRight. Water at current = min(maxLeft, maxRight) - height. Move the pointer at the smaller max inward.",
    ],
    "Set Matrix Zeroes": [
        "If we use O(m+n) space: store rows and columns to zero. For O(1): use first row and first column as flags; handle first row/col separately.",
        "Two passes: first mark; second set zeros. Avoid overwriting flags before reading.",
    ],
    "Spiral Matrix": [
        "Maintain four boundaries: top, bottom, left, right. Traverse top row (left to right), right column (top+1 to bottom), bottom row (right-1 to left), left column (bottom-1 to top+1); then shrink boundaries.",
        "Stop when top > bottom or left > right.",
    ],
    "Rotate Image": [
        "Transpose the matrix (swap matrix[i][j] with matrix[j][i] for i < j), then reverse each row.",
        "Or rotate in groups of four: for each cell in top-left quadrant, swap with three others.",
    ],
    "Search a 2D Matrix": [
        "Treat as a sorted 1D array: index i corresponds to row i//n, col i%n. Binary search on index 0..m*n-1.",
        "Or binary search row then column. O(log(m*n)).",
    ],
    "Search a 2D Matrix II": [
        "Start from top-right (or bottom-left). If current > target move left; if current < target move down. O(m+n).",
        "This works because each row is sorted and each column is sorted.",
    ],
    "Find First and Last Position of Element in Sorted Array": [
        "Binary search for left bound: first index where nums[i] >= target. Binary search for right bound: first index where nums[i] > target, then subtract 1.",
        "Or use a single binary search and expand. Two separate binary searches are clean.",
    ],
    "Next Permutation": [
        "Find largest i such that nums[i] < nums[i+1]. If none, reverse entire array. Else find largest j > i with nums[j] > nums[i]; swap nums[i] and nums[j]; reverse nums[i+1:].",
        "In-place. One pass to find i, one pass to find j, then reverse.",
    ],
    "Pow(x, n)": [
        "Binary exponentiation: x^n = (x^2)^(n/2) if n even; x^n = x * (x^2)^((n-1)/2) if n odd. Handle negative n: x^(-n) = 1/x^n.",
        "Recursive or iterative. O(log n) multiplications. Handle n = -2^31 (overflow when negating).",
    ],
    "Subarray Sum Equals K": [
        "Prefix sum: if prefix[j] - prefix[i] = k then subarray (i+1..j) sums to k. So we need prefix[i] = prefix[j] - k. Use a map: prefix sum -> count.",
        "For each prefix, add to result the count of previous prefixes with value (current_prefix - k).",
    ],
}


def get_hints_for_problem(title: str):
    """Return problem-specific hints if available, else None (caller can keep existing)."""
    return PROBLEM_HINTS.get(title)
