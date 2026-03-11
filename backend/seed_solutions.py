"""
Problem-specific solutions: Brute Force and Optimal (and other) approaches.
Keys are problem titles; value is list of { "title": str, "content": str }.
"""
import json
import re
from pathlib import Path
from typing import Optional

from models import ProblemFunctionMetadata, ProblemFunctionParam, SUPPORTED_LANGUAGES
from signature_contract import (
    align_solution_code_to_metadata,
    extract_signature,
    LANG_CODE_KEY,
    REQUIRED_SIGNATURE_LANGS,
    metadata_signature,
    signatures_match,
)

SOLUTIONS = {
    "Two Sum": [
        {
            "title": "Brute Force",
            "content": "Check every pair of indices (i, j) with i < j. If nums[i] + nums[j] == target, return [i, j]. Time: O(n²), Space: O(1).",
            "code_python": "def twoSum(nums, target):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] + nums[j] == target:\n                return [i, j]\n    return []",
            "code_javascript": "function twoSum(nums, target) {\n  for (let i = 0; i < nums.length; i++)\n    for (let j = i + 1; j < nums.length; j++)\n      if (nums[i] + nums[j] === target) return [i, j];\n  return [];\n}",
            "code_java": "public int[] twoSum(int[] nums, int target) {\n    for (int i = 0; i < nums.length; i++)\n        for (int j = i + 1; j < nums.length; j++)\n            if (nums[i] + nums[j] == target) return new int[]{i, j};\n    return new int[]{};\n}",
            "code_cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    for (int i = 0; i < (int)nums.size(); i++)\n        for (int j = i + 1; j < (int)nums.size(); j++)\n            if (nums[i] + nums[j] == target) return {i, j};\n    return {};\n}",
            "code_c": "int* twoSum(int* nums, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2 * sizeof(int));\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j < n; j++)\n            if (nums[i] + nums[j] == target) { out[0] = i; out[1] = j; return out; }\n    return out;\n}",
        },
        {
            "title": "Optimal (Hash Map)",
            "content": "One pass: for each num, check if (target - num) is already in a hash map. If yes, return [map[target - num], i]. Otherwise store num -> i. Time: O(n), Space: O(n).",
            "code_python": "def twoSum(nums, target):\n    seen = {}\n    for i, n in enumerate(nums):\n        need = target - n\n        if need in seen:\n            return [seen[need], i]\n        seen[n] = i\n    return []",
            "code_javascript": "function twoSum(nums, target) {\n  const seen = {};\n  for (let i = 0; i < nums.length; i++) {\n    const need = target - nums[i];\n    if (need in seen) return [seen[need], i];\n    seen[nums[i]] = i;\n  }\n  return [];\n}",
            "code_java": "public int[] twoSum(int[] nums, int target) {\n    Map<Integer, Integer> seen = new HashMap<>();\n    for (int i = 0; i < nums.length; i++) {\n        int need = target - nums[i];\n        if (seen.containsKey(need)) return new int[]{seen.get(need), i};\n        seen.put(nums[i], i);\n    }\n    return new int[]{};\n}",
            "code_cpp": "vector<int> twoSum(vector<int>& nums, int target) {\n    unordered_map<int, int> seen;\n    for (int i = 0; i < (int)nums.size(); i++) {\n        int need = target - nums[i];\n        if (seen.count(need)) return {seen[need], i};\n        seen[nums[i]] = i;\n    }\n    return {};\n}",
            "code_c": "int* twoSum(int* nums, int n, int target, int* returnSize) {\n    *returnSize = 2;\n    int* out = (int*)malloc(2 * sizeof(int));\n    for (int i = 0; i < n; i++) {\n        int need = target - nums[i];\n        for (int j = 0; j < i; j++) if (nums[j] == need) { out[0] = j; out[1] = i; return out; }\n    }\n    return out;\n}",
        },
    ],
    "Contains Duplicate": [
        {"title": "Brute Force", "content": "Compare every pair. O(n²) time, O(1) space.", "code_python": "def containsDuplicate(nums):\n    for i in range(len(nums)):\n        for j in range(i + 1, len(nums)):\n            if nums[i] == nums[j]:\n                return True\n    return False", "code_javascript": "function containsDuplicate(nums) {\n  for (let i = 0; i < nums.length; i++) {\n    for (let j = i + 1; j < nums.length; j++) {\n      if (nums[i] === nums[j]) return true;\n    }\n  }\n  return false;\n}", "code_java": "public boolean containsDuplicate(int[] nums) {\n    for (int i = 0; i < nums.length; i++)\n        for (int j = i + 1; j < nums.length; j++)\n            if (nums[i] == nums[j]) return true;\n    return false;\n}", "code_cpp": "bool containsDuplicate(vector<int>& nums) {\n    for (int i = 0; i < (int)nums.size(); i++)\n        for (int j = i + 1; j < (int)nums.size(); j++)\n            if (nums[i] == nums[j]) return true;\n    return false;\n}", "code_c": "bool containsDuplicate(int* nums, int n) {\n    for (int i = 0; i < n; i++)\n        for (int j = i + 1; j < n; j++)\n            if (nums[i] == nums[j]) return true;\n    return false;\n}"},
        {"title": "Optimal (Hash Set)", "content": "Use a set. For each element, if already in set return True; else add. O(n) time, O(n) space.", "code_python": "def containsDuplicate(nums):\n    seen = set()\n    for n in nums:\n        if n in seen:\n            return True\n        seen.add(n)\n    return False", "code_javascript": "function containsDuplicate(nums) {\n  const seen = new Set();\n  for (const n of nums) {\n    if (seen.has(n)) return true;\n    seen.add(n);\n  }\n  return false;\n}", "code_java": "public boolean containsDuplicate(int[] nums) {\n    Set<Integer> seen = new HashSet<>();\n    for (int n : nums) {\n        if (seen.contains(n)) return true;\n        seen.add(n);\n    }\n    return false;\n}", "code_cpp": "bool containsDuplicate(vector<int>& nums) {\n    unordered_set<int> seen;\n    for (int n : nums) {\n        if (seen.count(n)) return true;\n        seen.insert(n);\n    }\n    return false;\n}", "code_c": "bool containsDuplicate(int* nums, int n) {\n    int seen[100000]; int sz = 0;\n    for (int i = 0; i < n; i++) {\n        for (int j = 0; j < sz; j++) if (seen[j] == nums[i]) return true;\n        seen[sz++] = nums[i];\n    }\n    return false;\n}"},
    ],
    "Valid Anagram": [
        {"title": "Brute Force (Sort)", "content": "Sort both strings and compare. O(n log n) time, O(n) space.", "code_python": "def isAnagram(s, t):\n    return sorted(s) == sorted(t)", "code_javascript": "function isAnagram(s, t) {\n  return s.split('').sort().join('') === t.split('').sort().join('');\n}", "code_java": "public boolean isAnagram(String s, String t) {\n    char[] a = s.toCharArray(); char[] b = t.toCharArray();\n    Arrays.sort(a); Arrays.sort(b);\n    return Arrays.equals(a, b);\n}", "code_cpp": "bool isAnagram(string s, string t) {\n    sort(s.begin(), s.end()); sort(t.begin(), t.end());\n    return s == t;\n}", "code_c": "int cmp(const void* a, const void* b) { return *(char*)a - *(char*)b; }\nbool isAnagram(char* s, char* t) {\n    if (strlen(s) != strlen(t)) return false;\n    qsort(s, strlen(s), 1, cmp); qsort(t, strlen(t), 1, cmp);\n    return strcmp(s, t) == 0;\n}"},
        {"title": "Optimal (Count Array)", "content": "Use a 26-length count array. Increment for s, decrement for t. All counts must be 0. O(n) time, O(1) space.", "code_python": "def isAnagram(s, t):\n    if len(s) != len(t): return False\n    cnt = [0] * 26\n    for c in s: cnt[ord(c) - ord('a')] += 1\n    for c in t: cnt[ord(c) - ord('a')] -= 1\n    return all(x == 0 for x in cnt)", "code_javascript": "function isAnagram(s, t) {\n  if (s.length !== t.length) return false;\n  const cnt = Array(26).fill(0);\n  for (const c of s) cnt[c.charCodeAt(0) - 97]++;\n  for (const c of t) cnt[c.charCodeAt(0) - 97]--;\n  return cnt.every(x => x === 0);\n}", "code_java": "public boolean isAnagram(String s, String t) {\n    if (s.length() != t.length()) return false;\n    int[] cnt = new int[26];\n    for (char c : s.toCharArray()) cnt[c-'a']++;\n    for (char c : t.toCharArray()) cnt[c-'a']--;\n    for (int x : cnt) if (x != 0) return false;\n    return true;\n}", "code_cpp": "bool isAnagram(string s, string t) {\n    if (s.size() != t.size()) return false;\n    int cnt[26] = {};\n    for (char c : s) cnt[c-'a']++;\n    for (char c : t) cnt[c-'a']--;\n    for (int i = 0; i < 26; i++) if (cnt[i]) return false;\n    return true;\n}", "code_c": "bool isAnagram(char* s, char* t) {\n    if (strlen(s) != strlen(t)) return false;\n    int cnt[26] = {0};\n    for (; *s; s++) cnt[*s-'a']++;\n    for (; *t; t++) cnt[*t-'a']--;\n    for (int i = 0; i < 26; i++) if (cnt[i]) return false;\n    return true;\n}"},
    ],
    "Valid Palindrome": [
        {"title": "Brute Force", "content": "Filter to alphanumeric, reverse and compare. O(n) time, O(n) space.", "code_python": "def isPalindrome(s):\n    t = ''.join(c.lower() for c in s if c.isalnum())\n    return t == t[::-1]", "code_javascript": "function isPalindrome(s) {\n  const t = s.toLowerCase().replace(/[^a-z0-9]/g, '');\n  return t === t.split('').reverse().join('');\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Left pointer at start, right at end. Move inward skipping non-alphanumeric; compare (case-insensitive). O(n) time, O(1) space.", "code_python": "def isPalindrome(s):\n    i, j = 0, len(s) - 1\n    while i < j:\n        if not s[i].isalnum(): i += 1; continue\n        if not s[j].isalnum(): j -= 1; continue\n        if s[i].lower() != s[j].lower(): return False\n        i += 1; j -= 1\n    return True", "code_javascript": "function isPalindrome(s) {\n  let i = 0, j = s.length - 1;\n  while (i < j) {\n    if (!/\\w/.test(s[i])) { i++; continue; }\n    if (!/\\w/.test(s[j])) { j--; continue; }\n    if (s[i].toLowerCase() !== s[j].toLowerCase()) return false;\n    i++; j--;\n  }\n  return true;\n}"},
    ],
    "Product of Array Except Self": [
        {"title": "Brute Force", "content": "For each i, compute product of all elements except i (nested loop). O(n²) time.", "code_python": "def productExceptSelf(nums):\n    n = len(nums)\n    out = [1] * n\n    for i in range(n):\n        for j in range(n):\n            if i != j: out[i] *= nums[j]\n    return out", "code_javascript": "function productExceptSelf(nums) {\n  return nums.map((_, i) => nums.reduce((p, x, j) => i === j ? p : p * x, 1));\n}"},
        {"title": "Optimal (Prefix × Suffix)", "content": "Two passes: left pass for prefix products, right pass for suffix. output[i] = prefix[i-1] * suffix[i+1]. O(n) time, O(1) extra space if we use output for prefix then multiply by suffix.", "code_python": "def productExceptSelf(nums):\n    n = len(nums)\n    out = [1] * n\n    p = 1\n    for i in range(n): out[i] = p; p *= nums[i]\n    p = 1\n    for i in range(n - 1, -1, -1): out[i] *= p; p *= nums[i]\n    return out", "code_javascript": "function productExceptSelf(nums) {\n  const n = nums.length, out = Array(n).fill(1);\n  let p = 1;\n  for (let i = 0; i < n; i++) { out[i] = p; p *= nums[i]; }\n  p = 1;\n  for (let i = n - 1; i >= 0; i--) { out[i] *= p; p *= nums[i]; }\n  return out;\n}"},
    ],
    "3Sum": [
        {"title": "Brute Force", "content": "Three nested loops over i < j < k, check sum == 0. Deduplicate triplets. O(n³) time.", "code_python": "def threeSum(nums):\n    n, res = len(nums), set()\n    nums.sort()\n    for i in range(n):\n        for j in range(i+1, n):\n            for k in range(j+1, n):\n                if nums[i]+nums[j]+nums[k] == 0:\n                    res.add((nums[i],nums[j],nums[k]))\n    return [list(t) for t in res]", "code_javascript": "function threeSum(nums) {\n  const res = new Set();\n  nums.sort((a,b)=>a-b);\n  for (let i = 0; i < nums.length; i++)\n    for (let j = i+1; j < nums.length; j++)\n      for (let k = j+1; k < nums.length; k++)\n        if (nums[i]+nums[j]+nums[k] === 0) res.add(JSON.stringify([nums[i],nums[j],nums[k]].sort((a,b)=>a-b)));\n  return [...res].map(s => JSON.parse(s));\n}"},
        {"title": "Optimal (Sort + Two Pointers)", "content": "Sort array. For each index i, use two pointers (left = i+1, right = n-1) to find pairs that sum to -nums[i]. Skip duplicates. O(n²) time, O(1) extra space.", "code_python": "def threeSum(nums):\n    nums.sort()\n    res = []\n    for i in range(len(nums)):\n        if i and nums[i]==nums[i-1]: continue\n        l, r = i+1, len(nums)-1\n        while l < r:\n            s = nums[i]+nums[l]+nums[r]\n            if s == 0: res.append([nums[i],nums[l],nums[r]]); l += 1\n            while l < r and nums[l]==nums[l-1]: l += 1\n            if s < 0: l += 1\n            else: r -= 1\n    return res", "code_javascript": "function threeSum(nums) {\n  nums.sort((a,b)=>a-b);\n  const res = [];\n  for (let i = 0; i < nums.length; i++) {\n    if (i && nums[i] === nums[i-1]) continue;\n    let l = i+1, r = nums.length-1;\n    while (l < r) {\n      const s = nums[i]+nums[l]+nums[r];\n      if (s === 0) { res.push([nums[i],nums[l],nums[r]]); l++; while (l<r && nums[l]===nums[l-1]) l++; }\n      else if (s < 0) l++; else r--;\n    }\n  }\n  return res;\n}"},
    ],
    "Maximum Subarray": [
        {"title": "Brute Force", "content": "Try every subarray [i..j], compute sum, track max. O(n²) or O(n³) time.", "code_python": "def maxSubArray(nums):\n    n, best = len(nums), float('-inf')\n    for i in range(n):\n        s = 0\n        for j in range(i, n): s += nums[j]; best = max(best, s)\n    return best", "code_javascript": "function maxSubArray(nums) {\n  let best = -Infinity;\n  for (let i = 0; i < nums.length; i++) {\n    let s = 0;\n    for (let j = i; j < nums.length; j++) { s += nums[j]; best = Math.max(best, s); }\n  }\n  return best;\n}", "code_java": "public int maxSubArray(int[] nums) {\n    int best = Integer.MIN_VALUE;\n    for (int i = 0; i < nums.length; i++) {\n        int s = 0;\n        for (int j = i; j < nums.length; j++) { s += nums[j]; best = Math.max(best, s); }\n    }\n    return best;\n}", "code_cpp": "int maxSubArray(vector<int>& nums) {\n    int best = INT_MIN;\n    for (int i = 0; i < (int)nums.size(); i++) {\n        int s = 0;\n        for (int j = i; j < (int)nums.size(); j++) { s += nums[j]; best = max(best, s); }\n    }\n    return best;\n}", "code_c": "int maxSubArray(int* nums, int n) {\n    int best = -2147483648;\n    for (int i = 0; i < n; i++) {\n        int s = 0;\n        for (int j = i; j < n; j++) { s += nums[j]; if (s > best) best = s; }\n    }\n    return best;\n}"},
        {"title": "Optimal (Kadane)", "content": "Kadane's algorithm: maxEndingHere = max(nums[i], maxEndingHere + nums[i]); maxSoFar = max(maxSoFar, maxEndingHere). O(n) time, O(1) space.", "code_python": "def maxSubArray(nums):\n    cur, best = 0, nums[0]\n    for x in nums: cur = max(x, cur + x); best = max(best, cur)\n    return best", "code_javascript": "function maxSubArray(nums) {\n  let cur = 0, best = nums[0];\n  for (const x of nums) { cur = Math.max(x, cur + x); best = Math.max(best, cur); }\n  return best;\n}", "code_java": "public int maxSubArray(int[] nums) {\n    int cur = 0, best = nums[0];\n    for (int x : nums) { cur = Math.max(x, cur + x); best = Math.max(best, cur); }\n    return best;\n}", "code_cpp": "int maxSubArray(vector<int>& nums) {\n    int cur = 0, best = nums[0];\n    for (int x : nums) { cur = max(x, cur + x); best = max(best, cur); }\n    return best;\n}", "code_c": "int maxSubArray(int* nums, int n) {\n    int cur = 0, best = nums[0];\n    for (int i = 0; i < n; i++) { int x = nums[i]; cur = (x > cur + x) ? x : cur + x; if (cur > best) best = cur; }\n    return best;\n}"},
    ],
    "Maximum Product Subarray": [
        {"title": "Brute Force", "content": "Try every subarray, compute product, track max. O(n²) time.", "code_python": "def maxProduct(nums):\n    n, best = len(nums), nums[0]\n    for i in range(n):\n        p = 1\n        for j in range(i, n): p *= nums[j]; best = max(best, p)\n    return best", "code_javascript": "function maxProduct(nums) {\n  let best = nums[0];\n  for (let i = 0; i < nums.length; i++) {\n    let p = 1;\n    for (let j = i; j < nums.length; j++) { p *= nums[j]; best = Math.max(best, p); }\n  }\n  return best;\n}"},
        {"title": "Optimal (Track Max and Min)", "content": "At each index, track max and min product ending here (min can become max when multiplied by negative). maxHere = max(nums[i], maxHere*nums[i], minHere*nums[i]). O(n) time, O(1) space.", "code_python": "def maxProduct(nums):\n    cur_max = cur_min = best = nums[0]\n    for x in nums[1:]:\n        cur_max, cur_min = max(x, cur_max*x, cur_min*x), min(x, cur_max*x, cur_min*x)\n        best = max(best, cur_max)\n    return best", "code_javascript": "function maxProduct(nums) {\n  let curMax = nums[0], curMin = nums[0], best = nums[0];\n  for (let i = 1; i < nums.length; i++) {\n    const x = nums[i], a = curMax*x, b = curMin*x;\n    curMax = Math.max(x, a, b); curMin = Math.min(x, a, b);\n    best = Math.max(best, curMax);\n  }\n  return best;\n}"},
    ],
    "Container With Most Water": [
        {"title": "Brute Force", "content": "Try every pair (i, j), area = min(height[i], height[j]) * (j - i). O(n²) time.", "code_python": "def maxArea(height):\n    best = 0\n    for i in range(len(height)):\n        for j in range(i+1, len(height)): best = max(best, min(height[i],height[j])*(j-i))\n    return best", "code_javascript": "function maxArea(height) {\n  let best = 0;\n  for (let i = 0; i < height.length; i++)\n    for (let j = i+1; j < height.length; j++) best = Math.max(best, Math.min(height[i],height[j])*(j-i));\n  return best;\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Left=0, right=n-1. Area = min(height[left], height[right]) * (right - left). Move the pointer at the shorter line inward. O(n) time, O(1) space.", "code_python": "def maxArea(height):\n    l, r, best = 0, len(height)-1, 0\n    while l < r: best = max(best, min(height[l],height[r])*(r-l)); (l, r) = (l+1, r) if height[l] < height[r] else (l, r-1)\n    return best", "code_javascript": "function maxArea(height) {\n  let l = 0, r = height.length-1, best = 0;\n  while (l < r) {\n    best = Math.max(best, Math.min(height[l],height[r])*(r-l));\n    height[l] < height[r] ? l++ : r--;\n  }\n  return best;\n}"},
    ],
    "Longest Substring Without Repeating Characters": [
        {"title": "Brute Force", "content": "Check every substring for uniqueness. O(n²) or O(n³) time.", "code_python": "def lengthOfLongestSubstring(s):\n    best = 0\n    for i in range(len(s)):\n        for j in range(i+1, len(s)+1):\n            if len(set(s[i:j])) == j-i: best = max(best, j-i)\n    return best", "code_javascript": "function lengthOfLongestSubstring(s) {\n  let best = 0;\n  for (let i = 0; i < s.length; i++)\n    for (let j = i+1; j <= s.length; j++)\n      if (new Set(s.slice(i,j)).size === j-i) best = Math.max(best, j-i);\n  return best;\n}"},
        {"title": "Optimal (Sliding Window + Set)", "content": "Sliding window [left, right]. Expand right; if s[right] in set, shrink left until valid. Track max length. O(n) time, O(min(n, 26)) space.", "code_python": "def lengthOfLongestSubstring(s):\n    seen, left, best = set(), 0, 0\n    for right in range(len(s)):\n        while s[right] in seen: seen.discard(s[left]); left += 1\n        seen.add(s[right]); best = max(best, right - left + 1)\n    return best", "code_javascript": "function lengthOfLongestSubstring(s) {\n  const seen = new Set(); let left = 0, best = 0;\n  for (let right = 0; right < s.length; right++) {\n    while (seen.has(s[right])) seen.delete(s[left++]);\n    seen.add(s[right]); best = Math.max(best, right - left + 1);\n  }\n  return best;\n}"},
    ],
    "Longest Palindromic Substring": [
        {"title": "Brute Force", "content": "Check every substring for palindrome. O(n³) time.", "code_python": "def longestPalindrome(s):\n    def ok(i,j): return s[i:j+1]==s[i:j+1][::-1]\n    best = ''\n    for i in range(len(s)):\n        for j in range(i, len(s)):\n            if ok(i,j) and j-i+1 > len(best): best = s[i:j+1]\n    return best", "code_javascript": "function longestPalindrome(s) {\n  const ok = (i,j) => s.slice(i,j+1) === s.slice(i,j+1).split('').reverse().join('');\n  let best = '';\n  for (let i = 0; i < s.length; i++)\n    for (let j = i; j < s.length; j++) if (ok(i,j) && j-i+1 > best.length) best = s.slice(i,j+1);\n  return best;\n}"},
        {"title": "Optimal (Expand Around Center)", "content": "For each index (and between indices), expand outward while characters match. Track longest. O(n²) time, O(1) space.", "code_python": "def longestPalindrome(s):\n    def expand(l, r):\n        while l >= 0 and r < len(s) and s[l]==s[r]: l -= 1; r += 1\n        return s[l+1:r]\n    best = ''\n    for i in range(len(s)):\n        for c in [expand(i,i), expand(i,i+1)]:\n            if len(c) > len(best): best = c\n    return best", "code_javascript": "function longestPalindrome(s) {\n  const expand = (l, r) => { while (l >= 0 && r < s.length && s[l]===s[r]) { l--; r++; } return s.slice(l+1, r); };\n  let best = '';\n  for (let i = 0; i < s.length; i++) {\n    for (const c of [expand(i,i), expand(i,i+1)]) if (c.length > best.length) best = c;\n  }\n  return best;\n}"},
    ],
    "Climbing Stairs": [
        {"title": "Brute Force (Recursion)", "content": "ways(n) = ways(n-1) + ways(n-2). Base cases 1 and 2. O(2^n) without memo.", "code_python": "def climbStairs(n):\n    if n <= 2: return n\n    return climbStairs(n-1) + climbStairs(n-2)", "code_javascript": "function climbStairs(n) {\n  if (n <= 2) return n;\n  return climbStairs(n-1) + climbStairs(n-2);\n}"},
        {"title": "Optimal (DP / Fibonacci)", "content": "Two variables prev and curr. For i from 3 to n: curr, prev = prev + curr, curr. O(n) time, O(1) space.", "code_python": "def climbStairs(n):\n    if n <= 2: return n\n    prev, curr = 1, 2\n    for _ in range(3, n+1): prev, curr = curr, prev + curr\n    return curr", "code_javascript": "function climbStairs(n) {\n  if (n <= 2) return n;\n  let prev = 1, curr = 2;\n  for (let i = 3; i <= n; i++) [prev, curr] = [curr, prev + curr];\n  return curr;\n}"},
    ],
    "House Robber": [
        {"title": "Brute Force (Recursion)", "content": "At each house, rob (nums[i] + f(i-2)) or skip (f(i-1)). O(2^n) without memo.", "code_python": "def rob(nums):\n    def f(i): return 0 if i < 0 else max(nums[i]+f(i-2), f(i-1))\n    return f(len(nums)-1) if nums else 0", "code_javascript": "function rob(nums) {\n  const f = i => i < 0 ? 0 : Math.max(nums[i]+f(i-2), f(i-1));\n  return nums.length ? f(nums.length-1) : 0;\n}"},
        {"title": "Optimal (DP)", "content": "dp[i] = max(dp[i-1], nums[i] + dp[i-2]). Use two variables for O(1) space. O(n) time.", "code_python": "def rob(nums):\n    prev, curr = 0, 0\n    for x in nums: prev, curr = curr, max(curr, prev + x)\n    return curr", "code_javascript": "function rob(nums) {\n  let prev = 0, curr = 0;\n  for (const x of nums) [prev, curr] = [curr, Math.max(curr, prev + x)];\n  return curr;\n}"},
    ],
    "Group Anagrams": [
        {"title": "Brute Force", "content": "For each string, compare with others by sorted form. O(n² k log k) roughly.", "code_python": "def groupAnagrams(strs):\n    from collections import defaultdict\n    d = defaultdict(list)\n    for s in strs: d[''.join(sorted(s))].append(s)\n    return list(d.values())", "code_javascript": "function groupAnagrams(strs) {\n  const d = {};\n  for (const s of strs) {\n    const k = [...s].sort().join('');\n    if (!d[k]) d[k] = []; d[k].push(s);\n  }\n  return Object.values(d);\n}"},
        {"title": "Optimal (Hash by Sorted String or Count)", "content": "Key = tuple of character counts (or sorted string). Group by key. O(n * k) with count key; O(n * k log k) with sort.", "code_python": "def groupAnagrams(strs):\n    from collections import defaultdict\n    def key(s):\n        c = [0]*26\n        for x in s: c[ord(x)-97] += 1\n        return tuple(c)\n    d = defaultdict(list)\n    for s in strs: d[key(s)].append(s)\n    return list(d.values())", "code_javascript": "function groupAnagrams(strs) {\n  const key = s => { const c = Array(26).fill(0); for (const x of s) c[x.charCodeAt(0)-97]++; return c.join(','); };\n  const d = {};\n  for (const s of strs) { const k = key(s); if (!d[k]) d[k] = []; d[k].push(s); }\n  return Object.values(d);\n}"},
    ],
    "Single Number": [
        {"title": "Brute Force", "content": "For each number, count occurrences (or use two loops). O(n²) or O(n) with extra space.", "code_python": "def singleNumber(nums):\n    from collections import Counter\n    c = Counter(nums)\n    return next(x for x in nums if c[x]==1)", "code_javascript": "function singleNumber(nums) {\n  const c = {};\n  for (const x of nums) c[x] = (c[x]||0) + 1;\n  return nums.find(x => c[x] === 1);\n}"},
        {"title": "Optimal (XOR)", "content": "XOR all numbers. Duplicates cancel (a^a=0); single number remains. O(n) time, O(1) space.", "code_python": "def singleNumber(nums):\n    res = 0\n    for x in nums: res ^= x\n    return res", "code_javascript": "function singleNumber(nums) {\n  return nums.reduce((a, b) => a ^ b, 0);\n}"},
    ],
    "Number of 1 Bits": [
        {"title": "Brute Force", "content": "Shift right and count lowest bit: count += n & 1; n >>= 1. O(32) or O(number of bits).", "code_python": "def hammingWeight(n):\n    n &= 0xFFFFFFFF\n    c = 0\n    while n: c += n & 1; n >>= 1\n    return c", "code_javascript": "function hammingWeight(n) {\n  n = n >>> 0;\n  let c = 0;\n  while (n) { c += n & 1; n >>>= 1; }\n  return c;\n}"},
        {"title": "Optimal (n & (n-1))", "content": "n & (n-1) clears the rightmost 1. Repeat until n is 0; count iterations. O(number of 1s) time.", "code_python": "def hammingWeight(n):\n    n &= 0xFFFFFFFF\n    c = 0\n    while n: n &= n - 1; c += 1\n    return c", "code_javascript": "function hammingWeight(n) {\n  n = n >>> 0;\n  let c = 0;\n  while (n) { n &= n - 1; c++; }\n  return c;\n}"},
    ],
    "Reverse Bits": [
        {"title": "Brute Force", "content": "Extract each bit and build result: result = (result << 1) | (n & 1); n >>= 1. 32 iterations.", "code_python": "def reverseBits(n):\n    n &= 0xFFFFFFFF\n    res = 0\n    for _ in range(32): res = (res << 1) | (n & 1); n >>= 1\n    return res", "code_javascript": "function reverseBits(n) {\n  n = n >>> 0;\n  let res = 0;\n  for (let i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>>= 1; }\n  return res >>> 0;\n}"},
        {"title": "Optimal (Same)", "content": "Same as above; ensure 32-bit unsigned handling. O(1) time (32 steps).", "code_python": "def reverseBits(n):\n    n &= 0xFFFFFFFF\n    res = 0\n    for _ in range(32): res = (res << 1) | (n & 1); n >>= 1\n    return res", "code_javascript": "function reverseBits(n) {\n  n = n >>> 0;\n  let res = 0;\n  for (let i = 0; i < 32; i++) { res = (res << 1) | (n & 1); n >>>= 1; }\n  return res >>> 0;\n}"},
    ],
    "Missing Number": [
        {"title": "Brute Force (Sort)", "content": "Sort and find gap. O(n log n) time.", "code_python": "def missingNumber(nums):\n    nums.sort()\n    for i in range(len(nums)):\n        if nums[i] != i: return i\n    return len(nums)", "code_javascript": "function missingNumber(nums) {\n  nums.sort((a,b)=>a-b);\n  for (let i = 0; i < nums.length; i++) if (nums[i] !== i) return i;\n  return nums.length;\n}"},
        {"title": "Optimal (Sum or XOR)", "content": "Sum: expected = n*(n+1)/2, actual = sum(nums); return expected - actual. Or XOR all indices and all values; result is missing. O(n) time, O(1) space.", "code_python": "def missingNumber(nums):\n    n = len(nums)\n    return n * (n + 1) // 2 - sum(nums)", "code_javascript": "function missingNumber(nums) {\n  const n = nums.length;\n  return n * (n + 1) / 2 - nums.reduce((a,b)=>a+b, 0);\n}"},
    ],
    "Remove Duplicates from Sorted Array": [
        {"title": "Brute Force", "content": "Use extra array, copy unique elements. O(n) time, O(n) space.", "code_python": "def removeDuplicates(nums):\n    seen, out = set(), []\n    for x in nums:\n        if x not in seen: seen.add(x); out.append(x)\n    nums[:] = out\n    return len(out)", "code_javascript": "function removeDuplicates(nums) {\n  const seen = new Set(), out = [];\n  for (const x of nums) if (!seen.has(x)) { seen.add(x); out.push(x); }\n  nums.splice(0, nums.length, ...out);\n  return out.length;\n}"},
        {"title": "Optimal (Two Pointers In-Place)", "content": "Write index w and read index i. When nums[i] != nums[w-1], write nums[i] at w and w++. Return w. O(n) time, O(1) space.", "code_python": "def removeDuplicates(nums):\n    if not nums: return 0\n    w = 1\n    for i in range(1, len(nums)):\n        if nums[i] != nums[w-1]: nums[w] = nums[i]; w += 1\n    return w", "code_javascript": "function removeDuplicates(nums) {\n  if (!nums.length) return 0;\n  let w = 1;\n  for (let i = 1; i < nums.length; i++) if (nums[i] !== nums[w-1]) nums[w++] = nums[i];\n  return w;\n}"},
    ],
    "Sort Colors": [
        {"title": "Brute Force (Sort)", "content": "Sort the array. O(n log n) time.", "code_python": "def sortColors(nums):\n    nums.sort()", "code_javascript": "function sortColors(nums) {\n  nums.sort((a,b)=>a-b);\n}"},
        {"title": "Optimal (Dutch National Flag)", "content": "Three pointers: low (0s), mid (1s), high (2s). mid scans; swap with low or high as needed. O(n) time, O(1) space.", "code_python": "def sortColors(nums):\n    lo, mid, hi = 0, 0, len(nums)-1\n    while mid <= hi:\n        if nums[mid] == 0: nums[lo], nums[mid] = nums[mid], nums[lo]; lo += 1; mid += 1\n        elif nums[mid] == 2: nums[mid], nums[hi] = nums[hi], nums[mid]; hi -= 1\n        else: mid += 1", "code_javascript": "function sortColors(nums) {\n  let lo = 0, mid = 0, hi = nums.length - 1;\n  while (mid <= hi) {\n    if (nums[mid] === 0) { [nums[lo], nums[mid]] = [nums[mid], nums[lo]]; lo++; mid++; }\n    else if (nums[mid] === 2) { [nums[mid], nums[hi]] = [nums[hi], nums[mid]]; hi--; }\n    else mid++;\n  }\n}"},
    ],
    "Search in Rotated Sorted Array": [
        {"title": "Brute Force", "content": "Linear scan for target. O(n) time.", "code_python": "def search(nums, target):\n    for i, x in enumerate(nums):\n        if x == target: return i\n    return -1", "code_javascript": "function search(nums, target) {\n  return nums.indexOf(target);\n}"},
        {"title": "Optimal (Binary Search)", "content": "Binary search: determine which half is sorted; if target in that range search there, else the other half. O(log n) time.", "code_python": "def search(nums, target):\n    lo, hi = 0, len(nums)-1\n    while lo <= hi:\n        mid = (lo+hi)//2\n        if nums[mid] == target: return mid\n        if nums[lo] <= nums[mid]:\n            if nums[lo] <= target < nums[mid]: hi = mid-1\n            else: lo = mid+1\n        else:\n            if nums[mid] < target <= nums[hi]: lo = mid+1\n            else: hi = mid-1\n    return -1", "code_javascript": "function search(nums, target) {\n  let lo = 0, hi = nums.length - 1;\n  while (lo <= hi) {\n    const mid = (lo+hi)>>1;\n    if (nums[mid] === target) return mid;\n    if (nums[lo] <= nums[mid]) {\n      if (nums[lo] <= target && target < nums[mid]) hi = mid - 1; else lo = mid + 1;\n    } else {\n      if (nums[mid] < target && target <= nums[hi]) lo = mid + 1; else hi = mid - 1;\n    }\n  }\n  return -1;\n}"},
    ],
    "Find Minimum in Rotated Sorted Array": [
        {"title": "Brute Force", "content": "Linear scan for minimum. O(n) time.", "code_python": "def findMin(nums):\n    return min(nums)", "code_javascript": "function findMin(nums) { return Math.min(...nums); }"},
        {"title": "Optimal (Binary Search)", "content": "Binary search: compare mid with right. If nums[mid] > nums[right], min is in right half; else in left (including mid). O(log n) time.", "code_python": "def findMin(nums):\n    lo, hi = 0, len(nums)-1\n    while lo < hi:\n        mid = (lo+hi)//2\n        if nums[mid] > nums[hi]: lo = mid+1\n        else: hi = mid\n    return nums[lo]", "code_javascript": "function findMin(nums) {\n  let lo = 0, hi = nums.length - 1;\n  while (lo < hi) {\n    const mid = (lo+hi)>>1;\n    if (nums[mid] > nums[hi]) lo = mid + 1; else hi = mid;\n  }\n  return nums[lo];\n}"},
    ],
    "Binary Search": [
        {"title": "Iterative", "content": "Maintain left and right. While left <= right: mid = (left+right)//2; if nums[mid] == target return mid; else narrow range. O(log n) time.", "code_python": "def search(nums, target):\n    lo, hi = 0, len(nums)-1\n    while lo <= hi:\n        mid = (lo+hi)//2\n        if nums[mid] == target: return mid\n        if nums[mid] < target: lo = mid+1\n        else: hi = mid-1\n    return -1", "code_javascript": "function search(nums, target) {\n  let lo = 0, hi = nums.length - 1;\n  while (lo <= hi) {\n    const mid = (lo+hi)>>1;\n    if (nums[mid] === target) return mid;\n    if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n  }\n  return -1;\n}", "code_java": "public int search(int[] nums, int target) {\n    int lo = 0, hi = nums.length - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n    }\n    return -1;\n}", "code_cpp": "int search(vector<int>& nums, int target) {\n    int lo = 0, hi = nums.size() - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n    }\n    return -1;\n}", "code_c": "int search(int* nums, int n, int target) {\n    int lo = 0, hi = n - 1;\n    while (lo <= hi) {\n        int mid = lo + (hi - lo) / 2;\n        if (nums[mid] == target) return mid;\n        if (nums[mid] < target) lo = mid + 1; else hi = mid - 1;\n    }\n    return -1;\n}"},
    ],
    "Longest Consecutive Sequence": [
        {"title": "Brute Force (Sort)", "content": "Sort and scan for longest consecutive run. O(n log n) time.", "code_python": "def longestConsecutive(nums):\n    if not nums: return 0\n    nums.sort()\n    cur, best = 1, 1\n    for i in range(1, len(nums)):\n        if nums[i] == nums[i-1]+1: cur += 1\n        elif nums[i] != nums[i-1]: cur = 1\n        best = max(best, cur)\n    return best", "code_javascript": "function longestConsecutive(nums) {\n  if (!nums.length) return 0;\n  nums.sort((a,b)=>a-b);\n  let cur = 1, best = 1;\n  for (let i = 1; i < nums.length; i++) {\n    if (nums[i] === nums[i-1]+1) cur++; else if (nums[i] !== nums[i-1]) cur = 1;\n    best = Math.max(best, cur);\n  }\n  return best;\n}"},
        {"title": "Optimal (Hash Set)", "content": "Put all in set. For each num, if num-1 not in set (start of sequence), count forward (num, num+1, ...). Track max length. O(n) time, O(n) space.", "code_python": "def longestConsecutive(nums):\n    s = set(nums)\n    best = 0\n    for x in s:\n        if x-1 not in s:\n            cur = 0\n            while x in s: cur += 1; x += 1\n            best = max(best, cur)\n    return best", "code_javascript": "function longestConsecutive(nums) {\n  const s = new Set(nums);\n  let best = 0;\n  for (const x of s) {\n    if (!s.has(x-1)) {\n      let cur = 0, v = x;\n      while (s.has(v)) { cur++; v++; }\n      best = Math.max(best, cur);\n    }\n  }\n  return best;\n}"},
    ],
    "Merge Intervals": [
        {"title": "Brute Force", "content": "Compare every pair of intervals, merge if overlapping. O(n²) time.", "code_python": "def merge(intervals):\n    intervals.sort(key=lambda x: x[0])\n    i = 0\n    while i < len(intervals):\n        for j in range(i+1, len(intervals)):\n            if intervals[j][0] <= intervals[i][1]:\n                intervals[i][1] = max(intervals[i][1], intervals[j][1])\n                intervals.pop(j)\n                break\n        else: i += 1\n    return intervals", "code_javascript": "function merge(intervals) {\n  intervals.sort((a,b)=>a[0]-b[0]);\n  for (let i = 0; i < intervals.length; i++)\n    for (let j = i+1; j < intervals.length; j++)\n      if (intervals[j][0] <= intervals[i][1]) {\n        intervals[i][1] = Math.max(intervals[i][1], intervals[j][1]);\n        intervals.splice(j,1); j--;\n      }\n  return intervals;\n}"},
        {"title": "Optimal (Sort + Merge)", "content": "Sort by start. Iterate: if current overlaps with previous, merge (extend end); else push new. O(n log n) time, O(n) space.", "code_python": "def merge(intervals):\n    intervals.sort(key=lambda x: x[0])\n    out = [intervals[0]]\n    for a, b in intervals[1:]:\n        if a <= out[-1][1]: out[-1][1] = max(out[-1][1], b)\n        else: out.append([a, b])\n    return out", "code_javascript": "function merge(intervals) {\n  intervals.sort((a,b)=>a[0]-b[0]);\n  const out = [intervals[0]];\n  for (let i = 1; i < intervals.length; i++) {\n    const [a,b] = intervals[i];\n    if (a <= out[out.length-1][1]) out[out.length-1][1] = Math.max(out[out.length-1][1], b);\n    else out.push([a,b]);\n  }\n  return out;\n}"},
    ],
    "Jump Game": [
        {"title": "Brute Force (DFS/DP)", "content": "Try every jump from each index. O(2^n) or O(n²) with memo.", "code_python": "def canJump(nums):\n    def f(i):\n        if i >= len(nums)-1: return True\n        for j in range(1, nums[i]+1):\n            if f(i+j): return True\n        return False\n    return f(0)", "code_javascript": "function canJump(nums) {\n  const f = i => { if (i >= nums.length-1) return true; for (let j = 1; j <= nums[i]; j++) if (f(i+j)) return true; return false; };\n  return f(0);\n}"},
        {"title": "Optimal (Greedy)", "content": "Track farthest reachable. For each i, if i > farthest return false. Else farthest = max(farthest, i + nums[i]). O(n) time, O(1) space.", "code_python": "def canJump(nums):\n    far = 0\n    for i in range(len(nums)):\n        if i > far: return False\n        far = max(far, i + nums[i])\n    return True", "code_javascript": "function canJump(nums) {\n  let far = 0;\n  for (let i = 0; i < nums.length; i++) {\n    if (i > far) return false;\n    far = Math.max(far, i + nums[i]);\n  }\n  return true;\n}"},
    ],
    "Jump Game II": [
        {"title": "Brute Force (BFS)", "content": "BFS from index 0; each step try all possible jumps. O(n²) time.", "code_python": "def jump(nums):\n    from collections import deque\n    q, seen = deque([(0,0)]), {0}\n    while q:\n        i, steps = q.popleft()\n        if i >= len(nums)-1: return steps\n        for j in range(i+1, min(i+nums[i]+1, len(nums))):\n            if j not in seen: seen.add(j); q.append((j, steps+1))\n    return -1", "code_javascript": "function jump(nums) {\n  const q = [[0,0]], seen = new Set([0]);\n  while (q.length) {\n    const [i, steps] = q.shift();\n    if (i >= nums.length-1) return steps;\n    for (let j = i+1; j < Math.min(i+nums[i]+1, nums.length); j++)\n      if (!seen.has(j)) { seen.add(j); q.push([j, steps+1]); }\n  }\n  return -1;\n}"},
        {"title": "Optimal (Greedy)", "content": "Track current end of current jump and farthest. When i == currentEnd, jump++; currentEnd = farthest. O(n) time, O(1) space.", "code_python": "def jump(nums):\n    jumps = end = far = 0\n    for i in range(len(nums)-1):\n        far = max(far, i + nums[i])\n        if i == end: jumps += 1; end = far\n    return jumps", "code_javascript": "function jump(nums) {\n  let jumps = 0, end = 0, far = 0;\n  for (let i = 0; i < nums.length - 1; i++) {\n    far = Math.max(far, i + nums[i]);\n    if (i === end) { jumps++; end = far; }\n  }\n  return jumps;\n}"},
    ],
    "Unique Paths": [
        {"title": "Brute Force (Recursion)", "content": "Paths(m,n) = Paths(m-1,n) + Paths(m,n-1). O(2^(m+n)) without memo.", "code_python": "def uniquePaths(m, n):\n    def f(r,c): return 1 if r==0 or c==0 else f(r-1,c)+f(r,c-1)\n    return f(m-1,n-1)", "code_javascript": "function uniquePaths(m, n) {\n  const f = (r,c) => r === 0 || c === 0 ? 1 : f(r-1,c) + f(r,c-1);\n  return f(m-1, n-1);\n}"},
        {"title": "Optimal (DP / Math)", "content": "DP: dp[i][j] = dp[i-1][j] + dp[i][j-1]. Or combinatorial: (m+n-2) choose (n-1). O(m*n) or O(min(m,n)) with math.", "code_python": "def uniquePaths(m, n):\n    dp = [1]*n\n    for _ in range(1, m):\n        for j in range(1, n): dp[j] += dp[j-1]\n    return dp[-1]", "code_javascript": "function uniquePaths(m, n) {\n  const dp = Array(n).fill(1);\n  for (let i = 1; i < m; i++) for (let j = 1; j < n; j++) dp[j] += dp[j-1];\n  return dp[n-1];\n}"},
    ],
    "Minimum Path Sum": [
        {"title": "Brute Force (Recursion)", "content": "From (i,j), try down and right; return grid[i][j] + min(f(i+1,j), f(i,j+1)). O(2^(m+n)) without memo.", "code_python": "def minPathSum(grid):\n    def f(r,c):\n        if r>=len(grid) or c>=len(grid[0]): return float('inf')\n        if r==len(grid)-1 and c==len(grid[0])-1: return grid[r][c]\n        return grid[r][c] + min(f(r+1,c), f(r,c+1))\n    return f(0,0)", "code_javascript": "function minPathSum(grid) {\n  const f = (r,c) => {\n    if (r>=grid.length || c>=grid[0].length) return Infinity;\n    if (r===grid.length-1 && c===grid[0].length-1) return grid[r][c];\n    return grid[r][c] + Math.min(f(r+1,c), f(r,c+1));\n  };\n  return f(0,0);\n}"},
        {"title": "Optimal (DP)", "content": "dp[i][j] = grid[i][j] + min(dp[i+1][j], dp[i][j+1]). Can do in-place. O(m*n) time, O(1) or O(n) space.", "code_python": "def minPathSum(grid):\n    m, n = len(grid), len(grid[0])\n    for j in range(n-2, -1, -1): grid[m-1][j] += grid[m-1][j+1]\n    for i in range(m-2, -1, -1):\n        grid[i][n-1] += grid[i+1][n-1]\n        for j in range(n-2, -1, -1): grid[i][j] += min(grid[i+1][j], grid[i][j+1])\n    return grid[0][0]", "code_javascript": "function minPathSum(grid) {\n  const m = grid.length, n = grid[0].length;\n  for (let j = n-2; j >= 0; j--) grid[m-1][j] += grid[m-1][j+1];\n  for (let i = m-2; i >= 0; i--) {\n    grid[i][n-1] += grid[i+1][n-1];\n    for (let j = n-2; j >= 0; j--) grid[i][j] += Math.min(grid[i+1][j], grid[i][j+1]);\n  }\n  return grid[0][0];\n}"},
    ],
    "Reverse String": [
        {"title": "Brute Force", "content": "Use extra array, copy in reverse. O(n) time, O(n) space.", "code_python": "def reverseString(s):\n    s[:] = s[::-1]", "code_javascript": "function reverseString(s) {\n  s.reverse();\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Left and right pointers; swap s[left] and s[right], move inward. O(n) time, O(1) space.", "code_python": "def reverseString(s):\n    l, r = 0, len(s)-1\n    while l < r: s[l], s[r] = s[r], s[l]; l += 1; r -= 1", "code_javascript": "function reverseString(s) {\n  let l = 0, r = s.length - 1;\n  while (l < r) { [s[l], s[r]] = [s[r], s[l]]; l++; r--; }\n}"},
    ],
    "Valid Parentheses": [
        {"title": "Brute Force", "content": "Repeatedly remove matching pairs \"()\", \"[]\", \"{}\" until no change or empty. O(n²) time.", "code_python": "def isValid(s):\n    while '()' in s or '[]' in s or '{}' in s: s = s.replace('()','').replace('[]','').replace('{}','')\n    return not s", "code_javascript": "function isValid(s) {\n  while (s.includes('()') || s.includes('[]') || s.includes('{}')) s = s.replace('()','').replace('[]','').replace('{}','');\n  return s.length === 0;\n}"},
        {"title": "Optimal (Stack)", "content": "Stack: for each char, if opening push; if closing, pop and check match. Final stack must be empty. O(n) time, O(n) space.", "code_python": "def isValid(s):\n    st, pair = [], {'(':')','[':']','{':'}'}\n    for c in s:\n        if c in pair: st.append(c)\n        elif not st or pair[st.pop()] != c: return False\n    return len(st) == 0", "code_javascript": "function isValid(s) {\n  const st = [], pair = { '(':')', '[':']', '{':'}' };\n  for (const c of s) {\n    if (pair[c]) st.push(c);\n    else if (!st.length || pair[st.pop()] !== c) return false;\n  }\n  return st.length === 0;\n}"},
    ],
    "Merge Two Sorted Lists": [
        {"title": "Brute Force", "content": "Collect all values, sort, build new list. O((m+n) log(m+n)) time.", "code_python": "def mergeTwoLists(l1, l2):\n    vals = []\n    while l1: vals.append(l1.val); l1 = l1.next\n    while l2: vals.append(l2.val); l2 = l2.next\n    vals.sort()\n    dummy = ListNode(); p = dummy\n    for v in vals: p.next = ListNode(v); p = p.next\n    return dummy.next", "code_javascript": "function mergeTwoLists(l1, l2) {\n  const vals = [];\n  while (l1) { vals.push(l1.val); l1 = l1.next; }\n  while (l2) { vals.push(l2.val); l2 = l2.next; }\n  vals.sort((a,b)=>a-b);\n  const dummy = new ListNode(); let p = dummy;\n  for (const v of vals) { p.next = new ListNode(v); p = p.next; }\n  return dummy.next;\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Dummy head; compare list1.val and list2.val, attach smaller; advance. O(m+n) time, O(1) space.", "code_python": "def mergeTwoLists(l1, l2):\n    dummy = ListNode(); p = dummy\n    while l1 and l2:\n        if l1.val <= l2.val: p.next = l1; l1 = l1.next\n        else: p.next = l2; l2 = l2.next\n        p = p.next\n    p.next = l1 or l2\n    return dummy.next", "code_javascript": "function mergeTwoLists(l1, l2) {\n  const dummy = new ListNode(); let p = dummy;\n  while (l1 && l2) {\n    if (l1.val <= l2.val) { p.next = l1; l1 = l1.next; } else { p.next = l2; l2 = l2.next; }\n    p = p.next;\n  }\n  p.next = l1 || l2;\n  return dummy.next;\n}"},
    ],
    "Subsets": [
        {"title": "Brute Force (Iterative)", "content": "Start with [[]]. For each num, append num to every existing subset and add to result. O(2^n) time and space.", "code_python": "def subsets(nums):\n    res = [[]]\n    for x in nums: res += [r + [x] for r in res]\n    return res", "code_javascript": "function subsets(nums) {\n  let res = [[]];\n  for (const x of nums) res = res.concat(res.map(r => [...r, x]));\n  return res;\n}"},
        {"title": "Optimal (Backtracking)", "content": "Backtrack: at each index, either include or exclude. O(2^n) time, O(n) recursion space.", "code_python": "def subsets(nums):\n    res = []\n    def bt(i, path):\n        res.append(path[:])\n        for j in range(i, len(nums)): path.append(nums[j]); bt(j+1, path); path.pop()\n    bt(0, [])\n    return res", "code_javascript": "function subsets(nums) {\n  const res = [];\n  const bt = (i, path) => {\n    res.push([...path]);\n    for (let j = i; j < nums.length; j++) { path.push(nums[j]); bt(j+1, path); path.pop(); }\n  };\n  bt(0, []);\n  return res;\n}"},
    ],
    "Target Sum": [
        {"title": "Brute Force (Recursion)", "content": "At each index, try +nums[i] or -nums[i]. Count when we reach end and sum == target. O(2^n) time.", "code_python": "def findTargetSumWays(nums, target):\n    def f(i, s): return 1 if i==len(nums) and s==target else 0 if i==len(nums) else f(i+1, s+nums[i]) + f(i+1, s-nums[i])\n    return f(0, 0)", "code_javascript": "function findTargetSumWays(nums, target) {\n  const f = (i, s) => i === nums.length ? (s === target ? 1 : 0) : f(i+1, s+nums[i]) + f(i+1, s-nums[i]);\n  return f(0, 0);\n}"},
        {"title": "Optimal (DP / Subset Sum)", "content": "Convert to subset sum: find subset with sum = (target + total) / 2. DP with 1D array. O(n * sum) time.", "code_python": "def findTargetSumWays(nums, target):\n    t = (sum(nums) + target) // 2\n    if (sum(nums) + target) % 2 or t < 0: return 0\n    dp = [1] + [0] * t\n    for x in nums:\n        for j in range(t, x-1, -1): dp[j] += dp[j-x]\n    return dp[t]", "code_javascript": "function findTargetSumWays(nums, target) {\n  const total = nums.reduce((a,b)=>a+b, 0), t = (total + target) / 2;\n  if ((total + target) % 2 || t < 0) return 0;\n  const dp = [1, ...Array(t).fill(0)];\n  for (const x of nums) for (let j = t; j >= x; j--) dp[j] += dp[j-x];\n  return dp[t];\n}"},
    ],
    "Top K Frequent Elements": [
        {"title": "Brute Force (Sort by Freq)", "content": "Count frequencies, sort by count, return top k. O(n log n) time.", "code_python": "def topKFrequent(nums, k):\n    from collections import Counter\n    return [x for x,_ in Counter(nums).most_common(k)]", "code_javascript": "function topKFrequent(nums, k) {\n  const c = {};\n  for (const x of nums) c[x] = (c[x]||0) + 1;\n  return Object.entries(c).sort((a,b)=>b[1]-a[1]).slice(0,k).map(([x])=>+x);\n}"},
        {"title": "Optimal (Bucket Sort)", "content": "Count frequencies. Bucket[i] = list of elements with frequency i. Scan from highest bucket. O(n) time.", "code_python": "def topKFrequent(nums, k):\n    from collections import Counter\n    c, buckets = Counter(nums), [[] for _ in range(len(nums)+1)]\n    for x, cnt in c.items(): buckets[cnt].append(x)\n    out = []\n    for i in range(len(nums), 0, -1):\n        out.extend(buckets[i]);\n        if len(out) >= k: return out[:k]\n    return out[:k]", "code_javascript": "function topKFrequent(nums, k) {\n  const c = {};\n  for (const x of nums) c[x] = (c[x]||0) + 1;\n  const buckets = Array(nums.length+1).fill(null).map(()=>[]);\n  for (const [x, cnt] of Object.entries(c)) buckets[cnt].push(+x);\n  const out = [];\n  for (let i = nums.length; i >= 1; i--) { out.push(...buckets[i]); if (out.length >= k) return out.slice(0,k); }\n  return out.slice(0,k);\n}"},
    ],
    "Two Sum II - Input Array Is Sorted": [
        {"title": "Brute Force", "content": "Same as Two Sum: check every pair. O(n²) time.", "code_python": "def twoSum(numbers, target):\n    for i in range(len(numbers)):\n        for j in range(i+1, len(numbers)):\n            if numbers[i]+numbers[j]==target: return [i+1, j+1]\n    return []", "code_javascript": "function twoSum(numbers, target) {\n  for (let i = 0; i < numbers.length; i++)\n    for (let j = i+1; j < numbers.length; j++) if (numbers[i]+numbers[j]===target) return [i+1, j+1];\n  return [];\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Left=0, right=n-1. If sum == target return [left+1, right+1]. If sum < target left++; else right--. O(n) time, O(1) space.", "code_python": "def twoSum(numbers, target):\n    l, r = 0, len(numbers)-1\n    while l < r:\n        s = numbers[l] + numbers[r]\n        if s == target: return [l+1, r+1]\n        if s < target: l += 1\n        else: r -= 1\n    return []", "code_javascript": "function twoSum(numbers, target) {\n  let l = 0, r = numbers.length - 1;\n  while (l < r) {\n    const s = numbers[l] + numbers[r];\n    if (s === target) return [l+1, r+1];\n    if (s < target) l++; else r--;\n  }\n  return [];\n}"},
    ],
    "Trapping Rain Water": [
        {"title": "Brute Force", "content": "For each index (except ends), water = min(max left, max right) - height[i]. Precompute max left/right. O(n) time, O(n) space.", "code_python": "def trap(height):\n    n = len(height)\n    left = [0]*n; left[0] = height[0]\n    for i in range(1,n): left[i] = max(left[i-1], height[i])\n    right = [0]*n; right[-1] = height[-1]\n    for i in range(n-2,-1,-1): right[i] = max(right[i+1], height[i])\n    return sum(min(left[i],right[i])-height[i] for i in range(n))", "code_javascript": "function trap(height) {\n  const n = height.length;\n  const left = [height[0]];\n  for (let i = 1; i < n; i++) left.push(Math.max(left[i-1], height[i]));\n  const right = Array(n); right[n-1] = height[n-1];\n  for (let i = n-2; i >= 0; i--) right[i] = Math.max(right[i+1], height[i]);\n  let sum = 0;\n  for (let i = 0; i < n; i++) sum += Math.min(left[i], right[i]) - height[i];\n  return sum;\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Left and right pointers; track maxLeft and maxRight. Water at current = min(maxLeft, maxRight) - height. Move pointer at smaller max. O(n) time, O(1) space.", "code_python": "def trap(height):\n    l, r = 0, len(height)-1\n    max_l = max_r = total = 0\n    while l < r:\n        if height[l] <= height[r]:\n            max_l = max(max_l, height[l]); total += max_l - height[l]; l += 1\n        else:\n            max_r = max(max_r, height[r]); total += max_r - height[r]; r -= 1\n    return total", "code_javascript": "function trap(height) {\n  let l = 0, r = height.length - 1, maxL = 0, maxR = 0, total = 0;\n  while (l < r) {\n    if (height[l] <= height[r]) { maxL = Math.max(maxL, height[l]); total += maxL - height[l]; l++; }\n    else { maxR = Math.max(maxR, height[r]); total += maxR - height[r]; r--; }\n  }\n  return total;\n}"},
    ],
    "Pascal's Triangle": [
        {"title": "Iterative", "content": "Row 0 = [1]. Row i: build from row i-1: [1] + [prev[j]+prev[j+1] for j] + [1]. O(numRows²) time.", "code_python": "def generate(numRows):\n    if numRows == 0: return []\n    res = [[1]]\n    for i in range(1, numRows):\n        prev = res[-1]\n        row = [1] + [prev[j]+prev[j+1] for j in range(len(prev)-1)] + [1]\n        res.append(row)\n    return res", "code_javascript": "function generate(numRows) {\n  if (numRows === 0) return [];\n  const res = [[1]];\n  for (let i = 1; i < numRows; i++) {\n    const prev = res[i-1];\n    const row = [1];\n    for (let j = 0; j < prev.length-1; j++) row.push(prev[j]+prev[j+1]);\n    row.push(1);\n    res.push(row);\n  }\n  return res;\n}"},
    ],
    "Search Insert Position": [
        {"title": "Brute Force", "content": "Linear scan until nums[i] >= target. O(n) time.", "code_python": "def searchInsert(nums, target):\n    for i in range(len(nums)):\n        if nums[i] >= target: return i\n    return len(nums)", "code_javascript": "function searchInsert(nums, target) {\n  for (let i = 0; i < nums.length; i++) if (nums[i] >= target) return i;\n  return nums.length;\n}"},
        {"title": "Optimal (Binary Search)", "content": "Binary search for first index where nums[i] >= target. O(log n) time.", "code_python": "def searchInsert(nums, target):\n    lo, hi = 0, len(nums)\n    while lo < hi:\n        mid = (lo+hi)//2\n        if nums[mid] < target: lo = mid+1\n        else: hi = mid\n    return lo", "code_javascript": "function searchInsert(nums, target) {\n  let lo = 0, hi = nums.length;\n  while (lo < hi) { const mid = (lo+hi)>>1; if (nums[mid] < target) lo = mid+1; else hi = mid; }\n  return lo;\n}"},
    ],
    "Find Minimum in Rotated Sorted Array": [
        {"title": "Brute Force", "content": "Linear scan. O(n) time.", "code_python": "def findMin(nums):\n    return min(nums)", "code_javascript": "function findMin(nums) { return Math.min(...nums); }"},
        {"title": "Optimal (Binary Search)", "content": "Compare mid with right; if nums[mid] > nums[right], search right; else search left (include mid). O(log n) time.", "code_python": "def findMin(nums):\n    lo, hi = 0, len(nums)-1\n    while lo < hi:\n        mid = (lo+hi)//2\n        if nums[mid] > nums[hi]: lo = mid+1\n        else: hi = mid\n    return nums[lo]", "code_javascript": "function findMin(nums) {\n  let lo = 0, hi = nums.length - 1;\n  while (lo < hi) { const mid = (lo+hi)>>1; if (nums[mid] > nums[hi]) lo = mid+1; else hi = mid; }\n  return nums[lo];\n}"},
    ],
    "Squares of a Sorted Array": [
        {"title": "Brute Force", "content": "Square each, then sort. O(n log n) time.", "code_python": "def sortedSquares(nums):\n    return sorted(x*x for x in nums)", "code_javascript": "function sortedSquares(nums) { return nums.map(x => x*x).sort((a,b)=>a-b); }"},
        {"title": "Optimal (Two Pointers)", "content": "Two pointers at start and end. Compare squares, add larger to result from the end. O(n) time, O(n) space.", "code_python": "def sortedSquares(nums):\n    res = []\n    l, r = 0, len(nums)-1\n    while l <= r:\n        if abs(nums[l]) >= abs(nums[r]): res.append(nums[l]*nums[l]); l += 1\n        else: res.append(nums[r]*nums[r]); r -= 1\n    return res[::-1]", "code_javascript": "function sortedSquares(nums) {\n  const res = []; let l = 0, r = nums.length - 1;\n  while (l <= r) {\n    if (nums[l]*nums[l] >= nums[r]*nums[r]) { res.push(nums[l]*nums[l]); l++; } else { res.push(nums[r]*nums[r]); r--; }\n  }\n  return res.reverse();\n}"},
    ],
    "Rotate Array": [
        {"title": "Brute Force", "content": "Rotate one step k times. O(n*k) time.", "code_python": "def rotate(nums, k):\n    k %= len(nums)\n    for _ in range(k): nums[:] = [nums[-1]] + nums[:-1]", "code_javascript": "function rotate(nums, k) {\n  k %= nums.length;\n  for (let i = 0; i < k; i++) nums.unshift(nums.pop());\n}"},
        {"title": "Optimal (Reverse)", "content": "Reverse entire array, then reverse first k and reverse last n-k. O(n) time, O(1) space.", "code_python": "def rotate(nums, k):\n    k %= len(nums)\n    def rev(l, r):\n        while l < r: nums[l], nums[r] = nums[r], nums[l]; l += 1; r -= 1\n    rev(0, len(nums)-1); rev(0, k-1); rev(k, len(nums)-1)", "code_javascript": "function rotate(nums, k) {\n  k %= nums.length;\n  const rev = (l, r) => { while (l < r) [nums[l], nums[r]] = [nums[r], nums[l]]; l++; r--; };\n  rev(0, nums.length-1); rev(0, k-1); rev(k, nums.length-1);\n}"},
    ],
    "Move Zeroes": [
        {"title": "Brute Force", "content": "Count zeroes, build new array (non-zeros then zeros). O(n) time, O(n) space.", "code_python": "def moveZeroes(nums):\n    non = [x for x in nums if x != 0]\n    nums[:] = non + [0]*(len(nums)-len(non))", "code_javascript": "function moveZeroes(nums) {\n  const non = nums.filter(x => x !== 0);\n  nums.splice(0, nums.length, ...non, ...Array(nums.length - non.length).fill(0));\n}"},
        {"title": "Optimal (Two Pointers)", "content": "Write index: for each non-zero, put at write index and increment. Fill rest with zeros. O(n) time, O(1) space.", "code_python": "def moveZeroes(nums):\n    w = 0\n    for x in nums:\n        if x != 0: nums[w] = x; w += 1\n    for i in range(w, len(nums)): nums[i] = 0", "code_javascript": "function moveZeroes(nums) {\n  let w = 0;\n  for (const x of nums) if (x !== 0) nums[w++] = x;\n  for (let i = w; i < nums.length; i++) nums[i] = 0;\n}"},
    ],
    "Reverse Words in a String": [
        {"title": "Brute Force", "content": "Split by spaces, reverse list, join. O(n) time, O(n) space.", "code_python": "def reverseWords(s):\n    return ' '.join(s.split()[::-1])", "code_javascript": "function reverseWords(s) { return s.trim().split(/\\s+/).reverse().join(' '); }"},
        {"title": "Optimal (In-Place if mutable)", "content": "Reverse entire string, then reverse each word. Or split and join (language-dependent). O(n) time.", "code_python": "def reverseWords(s):\n    return ' '.join(s.split()[::-1])", "code_javascript": "function reverseWords(s) { return s.trim().split(/\\s+/).reverse().join(' '); }"},
    ],
    "Isomorphic Strings": [
        {"title": "Brute Force", "content": "For each char in s, map to t; check consistency. O(n) time, O(1) space (two maps).", "code_python": "def isIsomorphic(s, t):\n    m, n = {}, {}\n    for a, b in zip(s, t):\n        if (a in m and m[a]!=b) or (b in n and n[b]!=a): return False\n        m[a], n[b] = b, a\n    return True", "code_javascript": "function isIsomorphic(s, t) {\n  const m = {}, n = {};\n  for (let i = 0; i < s.length; i++) {\n    const a = s[i], b = t[i];\n    if ((m[a] && m[a] !== b) || (n[b] && n[b] !== a)) return false;\n    m[a] = b; n[b] = a;\n  }\n  return true;\n}"},
    ],
    "Happy Number": [
        {"title": "Brute Force", "content": "Simulate; use set to detect cycle. O(log n) iterations per step.", "code_python": "def isHappy(n):\n    seen = set()\n    while n != 1 and n not in seen:\n        seen.add(n)\n        n = sum(int(d)**2 for d in str(n))\n    return n == 1", "code_javascript": "function isHappy(n) {\n  const seen = new Set();\n  while (n !== 1 && !seen.has(n)) { seen.add(n); n = String(n).split('').reduce((s,d)=>s+d*d,0); }\n  return n === 1;\n}"},
    ],
    "Plus One": [
        {"title": "Simulation", "content": "Add 1 from right; carry over. If all 9s, new array [1] + zeros. O(n) time.", "code_python": "def plusOne(digits):\n    for i in range(len(digits)-1, -1, -1):\n        digits[i] += 1\n        if digits[i] <= 9: return digits\n        digits[i] = 0\n    return [1] + digits", "code_javascript": "function plusOne(digits) {\n  for (let i = digits.length - 1; i >= 0; i--) {\n    digits[i]++;\n    if (digits[i] <= 9) return digits;\n    digits[i] = 0;\n  }\n  return [1, ...digits];\n}"},
    ],
    "Sqrt(x)": [
        {"title": "Brute Force", "content": "Try i from 0 to x until i*i > x. O(sqrt(x)) time.", "code_python": "def mySqrt(x):\n    i = 0\n    while (i+1)**2 <= x: i += 1\n    return i", "code_javascript": "function mySqrt(x) {\n  let i = 0;\n  while ((i+1)*(i+1) <= x) i++;\n  return i;\n}"},
        {"title": "Optimal (Binary Search)", "content": "Binary search in [0, x] for largest i such that i*i <= x. O(log x) time.", "code_python": "def mySqrt(x):\n    lo, hi = 0, x\n    while lo < hi:\n        mid = (lo + hi + 1) // 2\n        if mid * mid <= x: lo = mid\n        else: hi = mid - 1\n    return lo", "code_javascript": "function mySqrt(x) {\n  let lo = 0, hi = x;\n  while (lo < hi) { const mid = (lo+hi+1)>>1; if (mid*mid <= x) lo = mid; else hi = mid - 1; }\n  return lo;\n}"},
    ],
    "First Bad Version": [
        {"title": "Brute Force", "content": "Linear scan. O(n) API calls.", "code_python": "def firstBadVersion(n):\n    for i in range(1, n+1):\n        if isBadVersion(i): return i\n    return n", "code_javascript": "function firstBadVersion(n) {\n  for (let i = 1; i <= n; i++) if (isBadVersion(i)) return i;\n  return n;\n}"},
        {"title": "Optimal (Binary Search)", "content": "Binary search: if mid is bad, search left; else search right. O(log n) API calls.", "code_python": "def firstBadVersion(n):\n    lo, hi = 1, n\n    while lo < hi:\n        mid = (lo+hi)//2\n        if isBadVersion(mid): hi = mid\n        else: lo = mid+1\n    return lo", "code_javascript": "function firstBadVersion(n) {\n  let lo = 1, hi = n;\n  while (lo < hi) { const mid = (lo+hi)>>1; if (isBadVersion(mid)) hi = mid; else lo = mid+1; }\n  return lo;\n}"},
    ],
    "Count Primes": [
        {"title": "Brute Force", "content": "For each number < n, check if prime. O(n sqrt(n)) time.", "code_python": "def countPrimes(n):\n    def is_prime(x):\n        if x < 2: return False\n        for i in range(2, int(x**0.5)+1):\n            if x % i == 0: return False\n        return True\n    return sum(1 for i in range(2, n) if is_prime(i))", "code_javascript": "function countPrimes(n) {\n  const isPrime = x => { if (x < 2) return false; for (let i = 2; i*i <= x; i++) if (x%i===0) return false; return true; };\n  let c = 0; for (let i = 2; i < n; i++) if (isPrime(i)) c++; return c;\n}"},
        {"title": "Optimal (Sieve of Eratosthenes)", "content": "Mark multiples of primes. O(n log log n) time, O(n) space.", "code_python": "def countPrimes(n):\n    if n <= 2: return 0\n    is_prime = [True] * n\n    is_prime[0] = is_prime[1] = False\n    for i in range(2, int(n**0.5)+1):\n        if is_prime[i]:\n            for j in range(i*i, n, i): is_prime[j] = False\n    return sum(is_prime)", "code_javascript": "function countPrimes(n) {\n  if (n <= 2) return 0;\n  const isPrime = Array(n).fill(true); isPrime[0] = isPrime[1] = false;\n  for (let i = 2; i*i < n; i++) if (isPrime[i]) for (let j = i*i; j < n; j += i) isPrime[j] = false;\n  return isPrime.filter(Boolean).length;\n}"},
    ],
    "Insert Interval": [
        {"title": "Linear", "content": "Find where new interval fits; merge overlapping. O(n) time.", "code_python": "def insert(intervals, newInterval):\n    out, i = [], 0\n    while i < len(intervals) and intervals[i][1] < newInterval[0]: out.append(intervals[i]); i += 1\n    while i < len(intervals) and intervals[i][0] <= newInterval[1]: newInterval = [min(newInterval[0], intervals[i][0]), max(newInterval[1], intervals[i][1])]; i += 1\n    return out + [newInterval] + intervals[i:]", "code_javascript": "function insert(intervals, newInterval) {\n  const out = []; let i = 0;\n  while (i < intervals.length && intervals[i][1] < newInterval[0]) out.push(intervals[i++]);\n  while (i < intervals.length && intervals[i][0] <= newInterval[1]) { newInterval = [Math.min(newInterval[0], intervals[i][0]), Math.max(newInterval[1], intervals[i][1])]; i++; }\n  return [...out, newInterval, ...intervals.slice(i)];\n}"},
    ],
    "Continuous Subarray Sum": [
        {"title": "Brute Force", "content": "Check every subarray sum for multiple of k. O(n²) time.", "code_python": "def checkSubarraySum(nums, k):\n    for i in range(len(nums)):\n        s = 0\n        for j in range(i, len(nums)): s += nums[j];\n            if j > i and (s % k == 0 if k else s == 0): return True\n    return False", "code_javascript": "function checkSubarraySum(nums, k) {\n  for (let i = 0; i < nums.length; i++) {\n    let s = 0;\n    for (let j = i; j < nums.length; j++) { s += nums[j]; if (j > i && (k ? s % k === 0 : s === 0)) return true; }\n  }\n  return false;\n}"},
        {"title": "Optimal (Prefix Sum + Mod)", "content": "Prefix sum mod k. If same mod seen twice (with distance >= 2), return true. O(n) time, O(k) space.", "code_python": "def checkSubarraySum(nums, k):\n    seen, cur = {0: -1}, 0\n    for i, x in enumerate(nums):\n        cur = (cur + x) % k if k else cur + x\n        if cur in seen and i - seen[cur] >= 2: return True\n        if cur not in seen: seen[cur] = i\n    return False", "code_javascript": "function checkSubarraySum(nums, k) {\n  const seen = { 0: -1 }; let cur = 0;\n  for (let i = 0; i < nums.length; i++) {\n    cur = k ? (cur + nums[i]) % k : cur + nums[i];\n    if (cur in seen && i - seen[cur] >= 2) return true;\n    if (!(cur in seen)) seen[cur] = i;\n  }\n  return false;\n}"},
    ],
    "Coin Change": [
        {"title": "Brute Force (Recursion)", "content": "Try all combinations; recurse with amount - coin. O(amount^coins) without memo.", "code_python": "def coinChange(coins, amount):\n    def f(a): return 0 if a == 0 else min((1 + f(a-c) for c in coins if c <= a), default=float('inf'))\n    return f(amount) if f(amount) != float('inf') else -1", "code_javascript": "function coinChange(coins, amount) {\n  const f = a => { if (a === 0) return 0; let best = Infinity; for (const c of coins) if (c <= a) best = Math.min(best, 1 + f(a-c)); return best; };\n  const r = f(amount); return r === Infinity ? -1 : r;\n}"},
        {"title": "Optimal (DP)", "content": "dp[a] = min coins for amount a. dp[0]=0; for each coin c, dp[a] = min(dp[a], 1+dp[a-c]). O(amount * coins) time, O(amount) space.", "code_python": "def coinChange(coins, amount):\n    dp = [0] + [float('inf')] * amount\n    for c in coins:\n        for a in range(c, amount+1): dp[a] = min(dp[a], 1 + dp[a-c])\n    return dp[amount] if dp[amount] != float('inf') else -1", "code_javascript": "function coinChange(coins, amount) {\n  const dp = [0, ...Array(amount).fill(Infinity)];\n  for (const c of coins) for (let a = c; a <= amount; a++) dp[a] = Math.min(dp[a], 1 + dp[a-c]);\n  return dp[amount] === Infinity ? -1 : dp[amount];\n}"},
    ],
    "Word Break": [
        {"title": "Brute Force (Recursion)", "content": "Try each word as prefix; recurse on remainder. O(2^n) without memo.", "code_python": "def wordBreak(s, wordDict):\n    def f(i): return True if i == len(s) else any(s[i:].startswith(w) and f(i+len(w)) for w in wordDict)\n    return f(0)", "code_javascript": "function wordBreak(s, wordDict) {\n  const f = i => i === s.length ? true : wordDict.some(w => s.startsWith(w, i) && f(i + w.length));\n  return f(0);\n}"},
        {"title": "Optimal (DP)", "content": "dp[i] = true if s[0:i] can be segmented. For each i, try all words ending at i. O(n² * m) time, O(n) space.", "code_python": "def wordBreak(s, wordDict):\n    ws = set(wordDict)\n    dp = [True] + [False] * len(s)\n    for i in range(1, len(s)+1):\n        for w in ws:\n            if i >= len(w) and dp[i-len(w)] and s[i-len(w):i] == w: dp[i] = True; break\n    return dp[len(s)]", "code_javascript": "function wordBreak(s, wordDict) {\n  const ws = new Set(wordDict);\n  const dp = [true, ...Array(s.length).fill(false)];\n  for (let i = 1; i <= s.length; i++) for (const w of ws) if (i >= w.length && dp[i-w.length] && s.slice(i-w.length, i) === w) { dp[i] = true; break; }\n  return dp[s.length];\n}"},
    ],
    "Combination Sum": [
        {"title": "Backtracking", "content": "At each step try adding each candidate (reuse allowed). When sum == target record; when sum > target backtrack. O(2^target) in worst case.", "code_python": "def combinationSum(candidates, target):\n    res = []\n    def bt(i, path, s):\n        if s == target: res.append(path[:]); return\n        if s > target: return\n        for j in range(i, len(candidates)): path.append(candidates[j]); bt(j, path, s+candidates[j]); path.pop()\n    bt(0, [], 0)\n    return res", "code_javascript": "function combinationSum(candidates, target) {\n  const res = [];\n  const bt = (i, path, s) => {\n    if (s === target) { res.push([...path]); return; }\n    if (s > target) return;\n    for (let j = i; j < candidates.length; j++) { path.push(candidates[j]); bt(j, path, s+candidates[j]); path.pop(); }\n  };\n  bt(0, [], 0);\n  return res;\n}"},
    ],
    "Permutations": [
        {"title": "Backtracking", "content": "For each position try every unused element; when path has n elements record and backtrack. O(n! * n) time.", "code_python": "def permute(nums):\n    res = []\n    def bt(used, path):\n        if len(path) == len(nums): res.append(path[:]); return\n        for i in range(len(nums)):\n            if not used[i]: used[i] = True; path.append(nums[i]); bt(used, path); path.pop(); used[i] = False\n    bt([False]*len(nums), [])\n    return res", "code_javascript": "function permute(nums) {\n  const res = [];\n  const bt = (used, path) => {\n    if (path.length === nums.length) { res.push([...path]); return; }\n    for (let i = 0; i < nums.length; i++) {\n      if (!used[i]) { used[i] = true; path.push(nums[i]); bt(used, path); path.pop(); used[i] = false; }\n    }\n  };\n  bt(Array(nums.length).fill(false), []);\n  return res;\n}"},
    ],
    "Generate Parentheses": [
        {"title": "Backtracking", "content": "Add '(' when open < n and ')' when close < open. When open == close == n record. O(4^n / sqrt(n)) time.", "code_python": "def generateParenthesis(n):\n    res = []\n    def bt(s, open_c, close_c):\n        if len(s) == 2*n: res.append(s); return\n        if open_c < n: bt(s+'(', open_c+1, close_c)\n        if close_c < open_c: bt(s+')', open_c, close_c+1)\n    bt('', 0, 0)\n    return res", "code_javascript": "function generateParenthesis(n) {\n  const res = [];\n  const bt = (s, openC, closeC) => {\n    if (s.length === 2*n) { res.push(s); return; }\n    if (openC < n) bt(s+'(', openC+1, closeC);\n    if (closeC < openC) bt(s+')', openC, closeC+1);\n  };\n  bt('', 0, 0);\n  return res;\n}"},
    ],
    "Letter Combinations of a Phone Number": [
        {"title": "Backtracking / BFS", "content": "For each digit extend current strings with each mapped letter. O(4^n) time where n is digits length.", "code_python": "def letterCombinations(digits):\n    if not digits: return []\n    m = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'}\n    res = ['']\n    for d in digits: res = [r+c for r in res for c in m[d]]\n    return res", "code_javascript": "function letterCombinations(digits) {\n  if (!digits.length) return [];\n  const m = {'2':'abc','3':'def','4':'ghi','5':'jkl','6':'mno','7':'pqrs','8':'tuv','9':'wxyz'};\n  let res = [''];\n  for (const d of digits) res = res.flatMap(r => [...m[d]].map(c => r+c));\n  return res;\n}"},
    ],
    "Kth Largest Element in an Array": [
        {"title": "Sort", "content": "Sort and return index n-k. O(n log n) time.", "code_python": "def findKthLargest(nums, k):\n    nums.sort(reverse=True)\n    return nums[k-1]", "code_javascript": "function findKthLargest(nums, k) {\n  nums.sort((a,b)=>b-a);\n  return nums[k-1];\n}"},
        {"title": "Optimal (Quickselect)", "content": "Partition like quicksort; recurse on left or right based on pivot position vs k. O(n) average. Or min-heap of size k: O(n log k).", "code_python": "def findKthLargest(nums, k):\n    import random\n    k = len(nums) - k\n    def part(l, r):\n        p = random.randint(l, r); nums[p], nums[r] = nums[r], nums[p]\n        i = l\n        for j in range(l, r):\n            if nums[j] <= nums[r]: nums[i], nums[j] = nums[j], nums[i]; i += 1\n        nums[i], nums[r] = nums[r], nums[i]\n        return i\n    l, r = 0, len(nums)-1\n    while True:\n        i = part(l, r)\n        if i == k: return nums[i]\n        if i < k: l = i+1\n        else: r = i-1", "code_javascript": "function findKthLargest(nums, k) {\n  k = nums.length - k;\n  const part = (l, r) => {\n    const p = l + Math.floor(Math.random()*(r-l+1)); [nums[p], nums[r]] = [nums[r], nums[p]];\n    let i = l;\n    for (let j = l; j < r; j++) if (nums[j] <= nums[r]) [nums[i], nums[j]] = [nums[j], nums[i]], i++;\n    [nums[i], nums[r]] = [nums[r], nums[i]]; return i;\n  };\n  let l = 0, r = nums.length - 1;\n  while (true) { const i = part(l, r); if (i === k) return nums[i]; if (i < k) l = i+1; else r = i-1; }\n}"},
    ],
    "Implement Stack using Queues": [
        {"title": "Two Queues", "content": "On push: add to q2, then move all q1 to q2, swap q1 and q2 so new element is at front. pop/top from q1. O(1) pop/top, O(n) push.", "code_python": "class MyStack:\n    def __init__(self): self.q = deque()\n    def push(self, x): n = len(self.q); self.q.append(x); [self.q.append(self.q.popleft()) for _ in range(n)]\n    def pop(self): return self.q.popleft()\n    def top(self): return self.q[0]\n    def empty(self): return not self.q", "code_javascript": "class MyStack {\n  constructor() { this.q = []; }\n  push(x) { const n = this.q.length; this.q.push(x); for (let i = 0; i < n; i++) this.q.push(this.q.shift()); }\n  pop() { return this.q.shift(); }\n  top() { return this.q[0]; }\n  empty() { return !this.q.length; }\n}"},
    ],
    "Implement Queue using Stacks": [
        {"title": "Two Stacks", "content": "Input stack for push; output stack for pop/peek. When output empty, pop all from input to output. Amortized O(1) per operation.", "code_python": "class MyQueue:\n    def __init__(self): self.in_st, self.out_st = [], []\n    def push(self, x): self.in_st.append(x)\n    def pop(self): self._pour(); return self.out_st.pop()\n    def peek(self): self._pour(); return self.out_st[-1]\n    def _pour(self):\n        if not self.out_st: self.out_st = self.in_st[::-1]; self.in_st = []\n    def empty(self): return not self.in_st and not self.out_st", "code_javascript": "class MyQueue {\n  constructor() { this.in_ = []; this.out_ = []; }\n  push(x) { this.in_.push(x); }\n  pop() { this.pour(); return this.out_.pop(); }\n  peek() { this.pour(); return this.out_[this.out_.length-1]; }\n  pour() { if (!this.out_.length) while (this.in_.length) this.out_.push(this.in_.pop()); }\n  empty() { return !this.in_.length && !this.out_.length; }\n}"},
    ],
    "Evaluate Reverse Polish Notation": [
        {"title": "Stack", "content": "For each token: if number push; if operator pop two, compute, push result. Note order for minus/divide. O(n) time, O(n) space.", "code_python": "def evalRPN(tokens):\n    st = []\n    for t in tokens:\n        if t in '+-*/': b, a = st.pop(), st.pop(); st.append(int({'/':lambda a,b: int(a/b), '*':int.__mul__, '+':int.__add__, '-':int.__sub__}[t](a, b)))\n        else: st.append(int(t))\n    return st[0]", "code_javascript": "function evalRPN(tokens) {\n  const st = [];\n  for (const t of tokens) {\n    if (['+','-','*','/'].includes(t)) { const b = st.pop(), a = st.pop(); st.push(t === '/' ? (a/b)|0 : t === '*' ? a*b : t === '+' ? a+b : a-b); }\n    else st.push(Number(t));\n  }\n  return st[0];\n}"},
    ],
    "Largest Rectangle in Histogram": [
        {"title": "Stack", "content": "For each bar find prev smaller and next smaller index; area = height * (next_smaller - prev_smaller - 1). O(n) time, O(n) space.", "code_python": "def largestRectangleArea(heights):\n    st, best = [], 0\n    for i, h in enumerate(heights + [0]):\n        while st and heights[st[-1]] > h: j = st.pop(); best = max(best, heights[j] * (i - st[-1] - 1 if st else i))\n        st.append(i)\n    return best", "code_javascript": "function largestRectangleArea(heights) {\n  const st = []; let best = 0;\n  const arr = [...heights, 0];\n  for (let i = 0; i < arr.length; i++) {\n    while (st.length && heights[st[st.length-1]] > arr[i]) { const j = st.pop(); best = Math.max(best, heights[j] * (st.length ? i - st[st.length-1] - 1 : i)); }\n    st.push(i);\n  }\n  return best;\n}"},
    ],
    "Reverse Linked List": [
        {"title": "Iterative", "content": "prev=None, curr=head. While curr: next=curr.next; curr.next=prev; prev=curr; curr=next. Return prev. O(n) time, O(1) space.", "code_python": "def reverseList(head):\n    prev = None\n    while head: nxt = head.next; head.next = prev; prev = head; head = nxt\n    return prev", "code_javascript": "function reverseList(head) {\n  let prev = null;\n  while (head) { const next = head.next; head.next = prev; prev = head; head = next; }\n  return prev;\n}", "code_java": "public ListNode reverseList(ListNode head) {\n    ListNode prev = null;\n    while (head != null) {\n        ListNode next = head.next;\n        head.next = prev;\n        prev = head;\n        head = next;\n    }\n    return prev;\n}", "code_cpp": "ListNode* reverseList(ListNode* head) {\n    ListNode* prev = nullptr;\n    while (head) {\n        ListNode* next = head->next;\n        head->next = prev;\n        prev = head;\n        head = next;\n    }\n    return prev;\n}", "code_c": "struct ListNode* reverseList(struct ListNode* head) {\n    struct ListNode* prev = NULL;\n    while (head) {\n        struct ListNode* next = head->next;\n        head->next = prev;\n        prev = head;\n        head = next;\n    }\n    return prev;\n}"},
    ],
    "Linked List Cycle": [
        {"title": "Floyd's Cycle Detection", "content": "Slow and fast pointers. If they meet there is a cycle. O(n) time, O(1) space.", "code_python": "def hasCycle(head):\n    slow = fast = head\n    while fast and fast.next: slow = slow.next; fast = fast.next.next; if slow == fast: return True\n    return False", "code_javascript": "function hasCycle(head) {\n  let slow = head, fast = head;\n  while (fast && fast.next) { slow = slow.next; fast = fast.next.next; if (slow === fast) return true; }\n  return false;\n}"},
    ],
    "Remove Nth Node From End of List": [
        {"title": "Two Pointers", "content": "Advance first pointer n steps; then move both until first reaches end. Remove node after second. Use dummy head. O(n) time.", "code_python": "def removeNthFromEnd(head, n):\n    dummy = ListNode(0, head)\n    first = second = dummy\n    for _ in range(n+1): first = first.next\n    while first: first = first.next; second = second.next\n    second.next = second.next.next\n    return dummy.next", "code_javascript": "function removeNthFromEnd(head, n) {\n  const dummy = new ListNode(0, head);\n  let first = dummy, second = dummy;\n  for (let i = 0; i <= n; i++) first = first.next;\n  while (first) { first = first.next; second = second.next; }\n  second.next = second.next.next;\n  return dummy.next;\n}"},
    ],
    "Reorder List": [
        {"title": "Find Middle, Reverse, Merge", "content": "Find middle with slow/fast; reverse second half; merge first half and reversed second alternately. O(n) time, O(1) space.", "code_python": "def reorderList(head):\n    if not head or not head.next: return\n    slow = fast = head\n    while fast.next and fast.next.next: slow = slow.next; fast = fast.next.next\n    rev = None; cur = slow.next; slow.next = None\n    while cur: nxt = cur.next; cur.next = rev; rev = cur; cur = nxt\n    a, b = head, rev\n    while b: a.next, a = b, a.next; b.next, b = a, b.next", "code_javascript": "function reorderList(head) {\n  if (!head || !head.next) return;\n  let slow = head, fast = head;\n  while (fast.next && fast.next.next) slow = slow.next, fast = fast.next.next;\n  let rev = null, cur = slow.next; slow.next = null;\n  while (cur) { const next = cur.next; cur.next = rev; rev = cur; cur = next; }\n  let a = head, b = rev;\n  while (b) { const an = a.next, bn = b.next; a.next = b; b.next = an; a = an; b = bn; }\n}"},
    ],
    "Maximum Depth of Binary Tree": [
        {"title": "Recursion", "content": "If null return 0; else 1 + max(depth(left), depth(right)). O(n) time, O(h) space.", "code_python": "def maxDepth(root):\n    return 0 if not root else 1 + max(maxDepth(root.left), maxDepth(root.right))", "code_javascript": "function maxDepth(root) {\n  return !root ? 0 : 1 + Math.max(maxDepth(root.left), maxDepth(root.right));\n}"},
    ],
    "Same Tree": [
        {"title": "Recursion", "content": "Both null -> true; one null or val differ -> false; else sameTree(p.left,q.left) and sameTree(p.right,q.right). O(n) time.", "code_python": "def isSameTree(p, q):\n    if not p and not q: return True\n    if not p or not q or p.val != q.val: return False\n    return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)", "code_javascript": "function isSameTree(p, q) {\n  if (!p && !q) return true;\n  if (!p || !q || p.val !== q.val) return false;\n  return isSameTree(p.left, q.left) && isSameTree(p.right, q.right);\n}"},
    ],
    "Invert Binary Tree": [
        {"title": "Recursion", "content": "Swap left and right; invert(left); invert(right). O(n) time, O(h) space.", "code_python": "def invertTree(root):\n    if not root: return None\n    root.left, root.right = invertTree(root.right), invertTree(root.left)\n    return root", "code_javascript": "function invertTree(root) {\n  if (!root) return null;\n  [root.left, root.right] = [invertTree(root.right), invertTree(root.left)];\n  return root;\n}"},
    ],
    "Symmetric Tree": [
        {"title": "Two Trees Mirror", "content": "Helper(p,q): both null true; one null or val differ false; else mirror(p.left,q.right) and mirror(p.right,q.left). Call helper(root,root). O(n) time.", "code_python": "def isSymmetric(root):\n    def mirror(p, q): return True if not p and not q else bool(p and q and p.val == q.val and mirror(p.left, q.right) and mirror(p.right, q.left))\n    return mirror(root, root) if root else True", "code_javascript": "function isSymmetric(root) {\n  const mirror = (p, q) => !p && !q ? true : (p && q && p.val === q.val && mirror(p.left, q.right) && mirror(p.right, q.left));\n  return root ? mirror(root, root) : true;\n}"},
    ],
    "Binary Tree Level Order Traversal": [
        {"title": "BFS", "content": "Queue: process level by level; for each level poll current size nodes and add children. O(n) time, O(n) space.", "code_python": "def levelOrder(root):\n    if not root: return []\n    q, out = [root], []\n    while q:\n        out.append([n.val for n in q])\n        q = [c for n in q for c in (n.left, n.right) if c]\n    return out", "code_javascript": "function levelOrder(root) {\n  if (!root) return [];\n  let q = [root], out = [];\n  while (q.length) {\n    out.push(q.map(n => n.val));\n    q = q.flatMap(n => [n.left, n.right].filter(Boolean));\n  }\n  return out;\n}"},
    ],
    "Validate Binary Search Tree": [
        {"title": "Recursion with Range", "content": "Pass (min, max). Check min < root.val < max; recurse left (min, root.val), right (root.val, max). O(n) time.", "code_python": "def isValidBST(root):\n    def ok(node, lo, hi):\n        if not node: return True\n        if not (lo < node.val < hi): return False\n        return ok(node.left, lo, node.val) and ok(node.right, node.val, hi)\n    return ok(root, float('-inf'), float('inf'))", "code_javascript": "function isValidBST(root) {\n  const ok = (node, lo, hi) => {\n    if (!node) return true;\n    if (node.val <= lo || node.val >= hi) return false;\n    return ok(node.left, lo, node.val) && ok(node.right, node.val, hi);\n  };\n  return ok(root, -Infinity, Infinity);\n}"},
    ],
    "Lowest Common Ancestor of a BST": [
        {"title": "BST Property", "content": "If p,q < root go left; if p,q > root go right; else root is LCA. O(h) time, O(1) space iterative.", "code_python": "def lowestCommonAncestor(root, p, q):\n    while root:\n        if p.val < root.val and q.val < root.val: root = root.left\n        elif p.val > root.val and q.val > root.val: root = root.right\n        else: return root", "code_javascript": "function lowestCommonAncestor(root, p, q) {\n  while (root) {\n    if (p.val < root.val && q.val < root.val) root = root.left;\n    else if (p.val > root.val && q.val > root.val) root = root.right;\n    else return root;\n  }\n  return null;\n}"},
    ],
    "Binary Tree Maximum Path Sum": [
        {"title": "Recursion", "content": "For each node max path through node = val + max(0, left_gain) + max(0, right_gain). Return max gain (one branch); update global max. O(n) time.", "code_python": "def maxPathSum(root):\n    best = float('-inf')\n    def gain(node):\n        nonlocal best\n        if not node: return 0\n        L = max(0, gain(node.left))\n        R = max(0, gain(node.right))\n        best = max(best, node.val + L + R)\n        return node.val + max(L, R)\n    gain(root)\n    return best", "code_javascript": "function maxPathSum(root) {\n  let best = -Infinity;\n  const gain = (node) => {\n    if (!node) return 0;\n    const L = Math.max(0, gain(node.left)), R = Math.max(0, gain(node.right));\n    best = Math.max(best, node.val + L + R);\n    return node.val + Math.max(L, R);\n  };\n  gain(root);\n  return best;\n}"},
    ],
    "Serialize and Deserialize Binary Tree": [
        {"title": "Preorder with Nulls", "content": "Serialize: preorder, use 'null' for null. Deserialize: read token; if 'null' return null; else build node, recurse left and right. O(n) time.", "code_python": "def serialize(root):\n    def f(node): return 'null' if not node else str(node.val)+','+f(node.left)+','+f(node.right)\n    return f(root)\ndef deserialize(data):\n    it = iter(data.split(','))\n    def f():\n        v = next(it,'null')\n        if v == 'null': return None\n        n = TreeNode(int(v)); n.left = f(); n.right = f(); return n\n    return f()", "code_javascript": "function serialize(root) {\n  if (!root) return 'null';\n  return root.val + ',' + serialize(root.left) + ',' + serialize(root.right);\n}\nfunction deserialize(data) {\n  const arr = data.split(','); let i = 0;\n  const f = () => { const v = arr[i++]; if (v === 'null') return null; const n = new TreeNode(+v); n.left = f(); n.right = f(); return n; };\n  return f();\n}"},
    ],
    "Number of Islands": [
        {"title": "DFS/BFS", "content": "From each unvisited '1' run DFS/BFS marking visited (e.g. set to '0'). Count number of DFS/BFS starts. O(m*n) time.", "code_python": "def numIslands(grid):\n    if not grid: return 0\n    m, n = len(grid), len(grid[0])\n    def dfs(i, j):\n        if i < 0 or i >= m or j < 0 or j >= n or grid[i][j] != '1': return\n        grid[i][j] = '0'\n        for di, dj in [(0,1),(1,0),(0,-1),(-1,0)]: dfs(i+di, j+dj)\n    count = 0\n    for i in range(m):\n        for j in range(n):\n            if grid[i][j] == '1': dfs(i, j); count += 1\n    return count", "code_javascript": "function numIslands(grid) {\n  if (!grid.length) return 0;\n  const m = grid.length, n = grid[0].length;\n  const dfs = (i, j) => {\n    if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] !== '1') return;\n    grid[i][j] = '0';\n    dfs(i+1,j); dfs(i-1,j); dfs(i,j+1); dfs(i,j-1);\n  };\n  let count = 0;\n  for (let i = 0; i < m; i++) for (let j = 0; j < n; j++) if (grid[i][j] === '1') dfs(i,j), count++;\n  return count;\n}"},
    ],
    "Clone Graph": [
        {"title": "BFS/DFS with Map", "content": "Map old node -> new node. When visiting a node create clone and neighbors. O(V+E) time, O(V) space.", "code_python": "def cloneGraph(node):\n    if not node: return None\n    m = {}\n    def dfs(n):\n        if n in m: return m[n]\n        c = Node(n.val); m[n] = c\n        c.neighbors = [dfs(x) for x in n.neighbors]\n        return c\n    return dfs(node)", "code_javascript": "function cloneGraph(node) {\n  if (!node) return null;\n  const m = new Map();\n  const dfs = (n) => {\n    if (m.has(n)) return m.get(n);\n    const c = new Node(n.val); m.set(n, c);\n    c.neighbors = n.neighbors.map(dfs);\n    return c;\n  };\n  return dfs(node);\n}"},
    ],
    "Pacific Atlantic Water Flow": [
        {"title": "DFS from Borders", "content": "From Pacific (top/left) DFS mark reachable; from Atlantic (bottom/right) DFS mark reachable. Return cells reachable from both. O(m*n) time.", "code_python": "def pacificAtlantic(heights):\n    if not heights: return []\n    m, n = len(heights), len(heights[0])\n    P, A = set(), set()\n    def dfs(i, j, seen):\n        seen.add((i,j))\n        for di,dj in [(0,1),(1,0),(0,-1),(-1,0)]:\n            ni, nj = i+di, j+dj\n            if 0<=ni<m and 0<=nj<n and (ni,nj) not in seen and heights[ni][nj]>=heights[i][j]: dfs(ni,nj,seen)\n    for i in range(m): dfs(i,0,P); dfs(i,n-1,A)\n    for j in range(n): dfs(0,j,P); dfs(m-1,j,A)\n    return list(P & A)", "code_javascript": "function pacificAtlantic(heights) {\n  if (!heights.length) return [];\n  const m = heights.length, n = heights[0].length;\n  const P = new Set(), A = new Set();\n  const dfs = (i, j, seen) => {\n    seen.add(i+','+j);\n    for (const [di,dj] of [[0,1],[1,0],[0,-1],[-1,0]]) {\n      const ni = i+di, nj = j+dj;\n      if (ni>=0&&ni<m&&nj>=0&&nj<n&&!seen.has(ni+','+nj)&&heights[ni][nj]>=heights[i][j]) dfs(ni,nj,seen);\n    }\n  };\n  for (let i=0;i<m;i++) dfs(i,0,P), dfs(i,n-1,A);\n  for (let j=0;j<n;j++) dfs(0,j,P), dfs(m-1,j,A);\n  return [...P].filter(k=>A.has(k)).map(k=>k.split(',').map(Number));\n}"},
    ],
    "Course Schedule": [
        {"title": "Cycle Detection", "content": "Build graph; detect cycle with DFS (three states) or Kahn's algorithm. If no cycle return true. O(V+E) time.", "code_python": "def canFinish(numCourses, prerequisites):\n    adj = [[] for _ in range(numCourses)]\n    for a, b in prerequisites: adj[b].append(a)\n    state = [0] * numCourses\n    def has_cycle(v):\n        if state[v] == 1: return True\n        if state[v] == 2: return False\n        state[v] = 1\n        for u in adj[v]:\n            if has_cycle(u): return True\n        state[v] = 2\n        return False\n    return not any(has_cycle(i) for i in range(numCourses))", "code_javascript": "function canFinish(numCourses, prerequisites) {\n  const adj = Array.from({length: numCourses}, () => []);\n  for (const [a,b] of prerequisites) adj[b].push(a);\n  const state = Array(numCourses).fill(0);\n  const hasCycle = (v) => {\n    if (state[v] === 1) return true;\n    if (state[v] === 2) return false;\n    state[v] = 1;\n    for (const u of adj[v]) if (hasCycle(u)) return true;\n    state[v] = 2;\n    return false;\n  };\n  return ![...Array(numCourses)].some((_,i) => hasCycle(i));\n}"},
    ],
    "Implement Trie": [
        {"title": "Trie Node", "content": "Node has children dict and is_end. Insert: traverse/create nodes. Search: traverse check is_end. startsWith: traverse. O(m) per operation.", "code_python": "class TrieNode:\n    def __init__(self): self.children = {}; self.is_end = False\nclass Trie:\n    def __init__(self): self.root = TrieNode()\n    def insert(self, word):\n        n = self.root\n        for c in word: n = n.children.setdefault(c, TrieNode())\n        n.is_end = True\n    def search(self, word):\n        n = self.root\n        for c in word:\n            if c not in n.children: return False\n            n = n.children[c]\n        return n.is_end\n    def startsWith(self, prefix):\n        n = self.root\n        for c in prefix:\n            if c not in n.children: return False\n            n = n.children[c]\n        return True", "code_javascript": "class TrieNode { constructor() { this.children = {}; this.isEnd = false; } }\nclass Trie {\n  constructor() { this.root = new TrieNode(); }\n  insert(word) { let n = this.root; for (const c of word) n = n.children[c] = n.children[c] || new TrieNode(); n.isEnd = true; }\n  search(word) { let n = this.root; for (const c of word) { if (!n.children[c]) return false; n = n.children[c]; } return n.isEnd; }\n  startsWith(prefix) { let n = this.root; for (const c of prefix) { if (!n.children[c]) return false; n = n.children[c]; } return true; }\n}"},
    ],
    "Add and Search Word": [
        {"title": "Trie + Backtracking", "content": "Trie for addWord. For search with '.', at that node try all children. O(m) insert; O(26^m) worst search with dots.", "code_python": "class WordDictionary:\n    def __init__(self): self.root = {}\n    def addWord(self, word):\n        n = self.root\n        for c in word: n = n.setdefault(c, {})\n        n['#'] = True\n    def search(self, word):\n        def find(i, n):\n            if i == len(word): return '#' in n\n            c = word[i]\n            if c == '.': return any(find(i+1, n[x]) for x in n if x != '#')\n            return c in n and find(i+1, n[c])\n        return find(0, self.root)", "code_javascript": "class WordDictionary {\n  constructor() { this.root = {}; }\n  addWord(word) { let n = this.root; for (const c of word) n = n[c] = n[c] || {}; n['#'] = true; }\n  search(word) {\n    const find = (i, n) => {\n      if (i === word.length) return '#' in n;\n      if (word[i] === '.') return Object.keys(n).filter(k=>k!=='#').some(k=>find(i+1,n[k]));\n      return word[i] in n && find(i+1, n[word[i]]);\n    };\n    return find(0, this.root);\n  }\n}"},
    ],
    "Word Search II": [
        {"title": "Trie + DFS", "content": "Build Trie from words. For each cell DFS and traverse Trie; at word end add to result. Prune when not a prefix. O(board * 4^maxWordLen) time.", "code_python": "def findWords(board, words):\n    root = {}\n    for w in words:\n        n = root\n        for c in w: n = n.setdefault(c, {})\n        n['#'] = w\n    res = []\n    def dfs(i, j, n):\n        c = board[i][j]\n        node = n.get(c)\n        if not node: return\n        if '#' in node: res.append(node['#']); del node['#']\n        board[i][j] = ' '\n        for di,dj in [(0,1),(1,0),(0,-1),(-1,0)]:\n            ni, nj = i+di, j+dj\n            if 0<=ni<len(board) and 0<=nj<len(board[0]) and board[ni][nj]!=' ': dfs(ni,nj,node)\n        board[i][j] = c\n    for i in range(len(board)):\n        for j in range(len(board[0])): dfs(i, j, root)\n    return res", "code_javascript": "function findWords(board, words) {\n  const root = {};\n  for (const w of words) { let n = root; for (const c of w) n = n[c] = n[c] || {}; n['#'] = w; }\n  const res = [];\n  const dfs = (i, j, n) => {\n    const c = board[i][j]; const node = n[c]; if (!node) return;\n    if (node['#']) { res.push(node['#']); delete node['#']; }\n    board[i][j] = ' ';\n    for (const [di,dj] of [[0,1],[1,0],[0,-1],[-1,0]]) {\n      const ni = i+di, nj = j+dj;\n      if (ni>=0&&ni<board.length&&nj>=0&&nj<board[0].length&&board[ni][nj]!=' ') dfs(ni,nj,node);\n    }\n    board[i][j] = c;\n  };\n  for (let i=0;i<board.length;i++) for (let j=0;j<board[0].length;j++) dfs(i,j,root);\n  return res;\n}"},
    ],
    "LRU Cache": [
        {"title": "Hash Map + Doubly Linked List", "content": "Map key->node; list for order (recent at head). get: move to head. put: update/move or add at head, evict tail if over capacity. O(1) get/put.", "code_python": "from collections import OrderedDict\nclass LRUCache:\n    def __init__(self, capacity): self.cap = capacity; self.d = OrderedDict()\n    def get(self, key):\n        if key not in self.d: return -1\n        self.d.move_to_end(key)\n        return self.d[key]\n    def put(self, key, value):\n        if key in self.d: self.d.move_to_end(key)\n        self.d[key] = value\n        if len(self.d) > self.cap: self.d.popitem(last=False)", "code_javascript": "class LRUCache {\n  constructor(capacity) { this.cap = capacity; this.m = new Map(); }\n  get(key) { if (!this.m.has(key)) return -1; const v = this.m.get(key); this.m.delete(key); this.m.set(key, v); return v; }\n  put(key, value) { this.m.delete(key); this.m.set(key, value); if (this.m.size > this.cap) this.m.delete(this.m.keys().next().value); }\n}"},
    ],
    "K Closest Points to Origin": [
        {"title": "Max-Heap of Size k", "content": "Max-heap by distance. For each point: if size < k push; else if dist < heap top pop and push. O(n log k) time.", "code_python": "def kClosest(points, k):\n    import heapq\n    return heapq.nsmallest(k, points, key=lambda p: p[0]**2 + p[1]**2)", "code_javascript": "function kClosest(points, k) {\n  points.sort((a,b) => (a[0]**2+a[1]**2) - (b[0]**2+b[1]**2));\n  return points.slice(0, k);\n}"},
    ],
    "Merge k Sorted Lists": [
        {"title": "Min-Heap", "content": "Push head of each list to min-heap. Pop smallest, add to result, push next from that list. O(N log k) time, N = total nodes.", "code_python": "def mergeKLists(lists):\n    import heapq\n    h = [(n.val, i, n) for i, n in enumerate(lists) if n]\n    heapq.heapify(h)\n    dummy = ListNode(); p = dummy\n    while h:\n        _, i, n = heapq.heappop(h)\n        p.next = n; p = p.next\n        if n.next: heapq.heappush(h, (n.next.val, i, n.next))\n    return dummy.next", "code_javascript": "function mergeKLists(lists) {\n  const h = lists.filter(Boolean).map((n,i) => [n.val, i, n]);\n  h.sort((a,b)=>a[0]-b[0]);\n  const dummy = new ListNode(); let p = dummy;\n  while (h.length) {\n    const [_, i, n] = h.shift();\n    p.next = n; p = p.next;\n    if (n.next) { h.push([n.next.val, i, n.next]); h.sort((a,b)=>a[0]-b[0]); }\n  }\n  return dummy.next;\n}"},
    ],
    "Find Median from Data Stream": [
        {"title": "Two Heaps", "content": "Max-heap lower half, min-heap upper half. Keep sizes balanced. Median = top of max-heap or average of two tops. O(log n) addNum, O(1) findMedian.", "code_python": "import heapq\nclass MedianFinder:\n    def __init__(self): self.lo, self.hi = [], []\n    def addNum(self, num):\n        heapq.heappush(self.lo, -num)\n        heapq.heappush(self.hi, -heapq.heappop(self.lo))\n        if len(self.lo) < len(self.hi): heapq.heappush(self.lo, -heapq.heappop(self.hi))\n    def findMedian(self): return -self.lo[0] if len(self.lo)>len(self.hi) else (-self.lo[0]+self.hi[0])/2", "code_javascript": "class MedianFinder {\n  constructor() { this.lo = []; this.hi = []; }\n  addNum(num) {\n    this.lo.push(-num); this.lo.sort((a,b)=>a-b);\n    this.hi.push(-this.lo.shift()); this.hi.sort((a,b)=>a-b);\n    if (this.lo.length < this.hi.length) this.lo.push(-this.hi.shift());\n  }\n  findMedian() { return this.lo.length > this.hi.length ? -this.lo[0] : (-this.lo[0]+this.hi[0])/2; }\n}"},
    ],
    "Sliding Window Maximum": [
        {"title": "Monotonic Deque", "content": "Deque stores indices in decreasing value order. For each new element pop from back while back < new; pop front when out of window. O(n) time.", "code_python": "def maxSlidingWindow(nums, k):\n    from collections import deque\n    q, out = deque(), []\n    for i, x in enumerate(nums):\n        while q and nums[q[-1]] < x: q.pop()\n        q.append(i)\n        if q[0] <= i - k: q.popleft()\n        if i >= k - 1: out.append(nums[q[0]])\n    return out", "code_javascript": "function maxSlidingWindow(nums, k) {\n  const q = [], out = [];\n  for (let i = 0; i < nums.length; i++) {\n    while (q.length && nums[q[q.length-1]] < nums[i]) q.pop();\n    q.push(i);\n    if (q[0] <= i - k) q.shift();\n    if (i >= k - 1) out.push(nums[q[0]]);\n  }\n  return out;\n}"},
    ],
    "Minimum Window Substring": [
        {"title": "Sliding Window", "content": "Expand right until window has all chars of t; shrink left while valid. Track min length and result. Use need/have counts. O(n) time.", "code_python": "def minWindow(s, t):\n    from collections import Counter\n    need = Counter(t); have = 0; need_count = len(need)\n    best_len, best = float('inf'), ''\n    l = 0\n    for r, c in enumerate(s):\n        if c in need:\n            need[c] -= 1\n            if need[c] == 0: have += 1\n        while have == need_count:\n            if r - l + 1 < best_len: best_len, best = r - l + 1, s[l:r+1]\n            if s[l] in need:\n                need[s[l]] += 1\n                if need[s[l]] > 0: have -= 1\n            l += 1\n    return best", "code_javascript": "function minWindow(s, t) {\n  const need = {}; for (const c of t) need[c] = (need[c]||0) + 1;\n  let have = 0, needCount = Object.keys(need).length, bestLen = Infinity, best = '', l = 0;\n  for (let r = 0; r < s.length; r++) {\n    if (need[s[r]] !== undefined) { need[s[r]]--; if (need[s[r]] === 0) have++; }\n    while (have === needCount) {\n      if (r - l + 1 < bestLen) { bestLen = r - l + 1; best = s.slice(l, r+1); }\n      if (need[s[l]] !== undefined) { need[s[l]]++; if (need[s[l]] > 0) have--; }\n      l++;\n    }\n  }\n  return best;\n}"},
    ],
    "Longest Repeating Character Replacement": [
        {"title": "Sliding Window", "content": "Window valid if (length - max_count) <= k. Expand right; if invalid shrink left. Track max frequency. O(n) time.", "code_python": "def characterReplacement(s, k):\n    cnt = {}; best = 0; l = 0\n    for r in range(len(s)):\n        cnt[s[r]] = cnt.get(s[r],0) + 1\n        while (r - l + 1) - max(cnt.values()) > k:\n            cnt[s[l]] -= 1; l += 1\n        best = max(best, r - l + 1)\n    return best", "code_javascript": "function characterReplacement(s, k) {\n  const cnt = {}; let best = 0, l = 0;\n  for (let r = 0; r < s.length; r++) {\n    cnt[s[r]] = (cnt[s[r]]||0) + 1;\n    while ((r-l+1) - Math.max(...Object.values(cnt)) > k) { cnt[s[l]]--; l++; }\n    best = Math.max(best, r - l + 1);\n  }\n  return best;\n}"},
    ],
    "Palindromic Substrings": [
        {"title": "Expand Around Center", "content": "For each center (index or between) expand while chars match; count. O(n²) time, O(1) space.", "code_python": "def countSubstrings(s):\n    def expand(l, r):\n        c = 0\n        while l >= 0 and r < len(s) and s[l]==s[r]: c += 1; l -= 1; r += 1\n        return c\n    return sum(expand(i,i) + expand(i,i+1) for i in range(len(s)))", "code_javascript": "function countSubstrings(s) {\n  const expand = (l, r) => { let c = 0; while (l >= 0 && r < s.length && s[l]===s[r]) { c++; l--; r++; } return c; };\n  let out = 0; for (let i = 0; i < s.length; i++) out += expand(i,i) + expand(i,i+1);\n  return out;\n}"},
    ],
    "Decode Ways": [
        {"title": "DP", "content": "dp[i] = ways for s[0:i]. One digit valid add dp[i-1]; two digits valid add dp[i-2]. Handle '0'. O(n) time, O(n) space.", "code_python": "def numDecodings(s):\n    if not s or s[0]=='0': return 0\n    prev, curr = 1, 1\n    for i in range(1, len(s)):\n        nxt = 0\n        if s[i] != '0': nxt = curr\n        if 10 <= int(s[i-1:i+1]) <= 26: nxt += prev\n        prev, curr = curr, nxt\n    return curr", "code_javascript": "function numDecodings(s) {\n  if (!s.length || s[0]==='0') return 0;\n  let prev = 1, curr = 1;\n  for (let i = 1; i < s.length; i++) {\n    let nxt = 0;\n    if (s[i] !== '0') nxt = curr;\n    const two = parseInt(s.slice(i-1,i+1));\n    if (two >= 10 && two <= 26) nxt += prev;\n    prev = curr; curr = nxt;\n  }\n  return curr;\n}"},
    ],
    "Unique Binary Search Trees": [
        {"title": "Catalan Number DP", "content": "G(n)=sum G(j-1)*G(n-j) for j as root. G(0)=G(1)=1. O(n²) time, O(n) space.", "code_python": "def numTrees(n):\n    dp = [1, 1] + [0] * (n - 1)\n    for i in range(2, n + 1):\n        for j in range(1, i + 1): dp[i] += dp[j-1] * dp[i-j]\n    return dp[n]", "code_javascript": "function numTrees(n) {\n  const dp = [1, 1];\n  for (let i = 2; i <= n; i++) { dp[i] = 0; for (let j = 1; j <= i; j++) dp[i] += dp[j-1] * dp[i-j]; }\n  return dp[n];\n}"},
    ],
    "Maximum Product of Word Lengths": [
        {"title": "Bitmask", "content": "Each word -> bitmask of letters. Two words disjoint iff mask1 & mask2 == 0. Check all pairs. O(n²) time.", "code_python": "def maxProduct(words):\n    masks = [sum(1<<(ord(c)-97) for c in set(w)) for w in words]\n    best = 0\n    for i in range(len(words)):\n        for j in range(i+1, len(words)):\n            if not (masks[i] & masks[j]): best = max(best, len(words[i])*len(words[j]))\n    return best", "code_javascript": "function maxProduct(words) {\n  const masks = words.map(w => [...new Set(w)].reduce((m,c)=>m|(1<<(c.charCodeAt(0)-97)),0));\n  let best = 0;\n  for (let i = 0; i < words.length; i++) for (let j = i+1; j < words.length; j++) if (!(masks[i]&masks[j])) best = Math.max(best, words[i].length*words[j].length);\n  return best;\n}"},
    ],
    "Partition Equal Subset Sum": [
        {"title": "Subset Sum DP", "content": "If total odd return false. dp[j]=can we sum to j. dp[0]=true; for num: for j from sum down to num dp[j]|=dp[j-num]. O(n*sum) time.", "code_python": "def canPartition(nums):\n    s = sum(nums)\n    if s % 2: return False\n    t = s // 2; dp = [True] + [False] * t\n    for x in nums:\n        for j in range(t, x - 1, -1): dp[j] = dp[j] or dp[j - x]\n    return dp[t]", "code_javascript": "function canPartition(nums) {\n  const s = nums.reduce((a,b)=>a+b,0);\n  if (s % 2) return false;\n  const t = s/2; const dp = [true, ...Array(t).fill(false)];\n  for (const x of nums) for (let j = t; j >= x; j--) dp[j] = dp[j] || dp[j-x];\n  return dp[t];\n}"},
    ],
    "Partition to K Equal Sum Subsets": [
        {"title": "Backtracking", "content": "Target=total/k. Assign each number to one of k buckets; each bucket must sum to target. Prune: sort descending, skip if bucket+num>target. O(k^n) worst.", "code_python": "def canPartitionKSubsets(nums, k):\n    s = sum(nums)\n    if s % k: return False\n    target = s // k; nums.sort(reverse=True)\n    buckets = [0] * k\n    def bt(i):\n        if i == len(nums): return True\n        for j in range(k):\n            if buckets[j] + nums[i] <= target:\n                buckets[j] += nums[i]\n                if bt(i+1): return True\n                buckets[j] -= nums[i]\n        return False\n    return bt(0)", "code_javascript": "function canPartitionKSubsets(nums, k) {\n  const s = nums.reduce((a,b)=>a+b,0);\n  if (s % k) return false;\n  const target = s/k; nums.sort((a,b)=>b-a);\n  const buckets = Array(k).fill(0);\n  const bt = (i) => {\n    if (i === nums.length) return true;\n    for (let j = 0; j < k; j++) {\n      if (buckets[j] + nums[i] <= target) {\n        buckets[j] += nums[i];\n        if (bt(i+1)) return true;\n        buckets[j] -= nums[i];\n      }\n    }\n    return false;\n  };\n  return bt(0);\n}"},
    ],
    "Longest Increasing Subsequence": [
        {"title": "DP", "content": "dp[i]=LIS ending at i. dp[i]=1+max(dp[j]) for j<i and nums[j]<nums[i]. O(n²) time. Or patience sorting O(n log n).", "code_python": "def lengthOfLIS(nums):\n    if not nums: return 0\n    dp = [1] * len(nums)\n    for i in range(1, len(nums)):\n        for j in range(i):\n            if nums[j] < nums[i]: dp[i] = max(dp[i], dp[j] + 1)\n    return max(dp)", "code_javascript": "function lengthOfLIS(nums) {\n  if (!nums.length) return 0;\n  const dp = Array(nums.length).fill(1);\n  for (let i = 1; i < nums.length; i++) for (let j = 0; j < i; j++) if (nums[j] < nums[i]) dp[i] = Math.max(dp[i], dp[j] + 1);\n  return Math.max(...dp);\n}"},
    ],
    "Longest Common Subsequence": [
        {"title": "DP", "content": "dp[i][j]=LCS of text1[0:i], text2[0:j]. If match dp[i][j]=1+dp[i-1][j-1]; else max(dp[i-1][j], dp[i][j-1]). O(m*n) time.", "code_python": "def longestCommonSubsequence(text1, text2):\n    m, n = len(text1), len(text2)\n    dp = [[0]*(n+1) for _ in range(m+1)]\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            if text1[i-1]==text2[j-1]: dp[i][j] = 1 + dp[i-1][j-1]\n            else: dp[i][j] = max(dp[i-1][j], dp[i][j-1])\n    return dp[m][n]", "code_javascript": "function longestCommonSubsequence(text1, text2) {\n  const m = text1.length, n = text2.length;\n  const dp = Array(m+1).fill(0).map(()=>Array(n+1).fill(0));\n  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++) dp[i][j] = text1[i-1]===text2[j-1] ? 1+dp[i-1][j-1] : Math.max(dp[i-1][j], dp[i][j-1]);\n  return dp[m][n];\n}"},
    ],
    "Edit Distance": [
        {"title": "DP", "content": "dp[i][j]=min ops to convert word1[0:i] to word2[0:j]. Insert/delete/replace. Base dp[0][j]=j, dp[i][0]=i. O(m*n) time.", "code_python": "def minDistance(word1, word2):\n    m, n = len(word1), len(word2)\n    dp = [[0]*(n+1) for _ in range(m+1)]\n    for i in range(m+1): dp[i][0] = i\n    for j in range(n+1): dp[0][j] = j\n    for i in range(1, m+1):\n        for j in range(1, n+1):\n            dp[i][j] = min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(0 if word1[i-1]==word2[j-1] else 1))\n    return dp[m][n]", "code_javascript": "function minDistance(word1, word2) {\n  const m = word1.length, n = word2.length;\n  const dp = Array(m+1).fill(0).map((_,i)=>[i]);\n  for (let j = 1; j <= n; j++) dp[0][j] = j;\n  for (let i = 1; i <= m; i++) for (let j = 1; j <= n; j++) dp[i][j] = Math.min(dp[i-1][j]+1, dp[i][j-1]+1, dp[i-1][j-1]+(word1[i-1]===word2[j-1]?0:1));\n  return dp[m][n];\n}"},
    ],
    "Word Break II": [
        {"title": "Backtracking + Memo", "content": "For each prefix that is a word recurse on remainder; memo s -> list of sentences. O(2^n) worst, memo helps.", "code_python": "def wordBreak(s, wordDict):\n    ws = set(wordDict)\n    def f(s):\n        if not s: return ['']\n        if s in memo: return memo[s]\n        out = []\n        for i in range(1, len(s)+1):\n            if s[:i] in ws:\n                for tail in f(s[i:]): out.append((s[:i] + ' ' + tail).strip())\n        memo[s] = out\n        return out\n    memo = {}\n    return f(s)", "code_javascript": "function wordBreak(s, wordDict) {\n  const ws = new Set(wordDict);\n  const memo = {};\n  const f = (s) => {\n    if (!s) return [''];\n    if (memo[s]) return memo[s];\n    const out = [];\n    for (let i = 1; i <= s.length; i++) if (ws.has(s.slice(0,i))) for (const t of f(s.slice(i))) out.push((s.slice(0,i)+' '+t).trim());\n    memo[s] = out;\n    return out;\n  };\n  return f(s);\n}"},
    ],
    "N-Queens": [
        {"title": "Backtracking", "content": "Place queen row by row; try each column; check no conflict (col, diag row-col, row+col). O(n!) time.", "code_python": "def solveNQueens(n):\n    res = []\n    def bt(row, cols, d1, d2, path):\n        if row == n: res.append(['.'*c+'Q'+'.'*(n-1-c) for c in path]); return\n        for c in range(n):\n            if c in cols or (row-c) in d1 or (row+c) in d2: continue\n            bt(row+1, cols|{c}, d1|{row-c}, d2|{row+c}, path+[c])\n    bt(0, set(), set(), set(), [])\n    return res", "code_javascript": "function solveNQueens(n) {\n  const res = [];\n  const bt = (row, cols, d1, d2, path) => {\n    if (row === n) { res.push(path.map(c=>'.'.repeat(c)+'Q'+'.'.repeat(n-1-c))); return; }\n    for (let c = 0; c < n; c++) {\n      if (cols.has(c) || d1.has(row-c) || d2.has(row+c)) continue;\n      bt(row+1, new Set([...cols,c]), new Set([...d1,row-c]), new Set([...d2,row+c]), path.concat(c));\n    }\n  };\n  bt(0, new Set(), new Set(), new Set(), []);\n  return res;\n}"},
    ],
    "N-Queens II": [
        {"title": "Backtracking", "content": "Same as N-Queens but count solutions only. O(n!) time.", "code_python": "def totalNQueens(n):\n    count = 0\n    def bt(row, cols, d1, d2):\n        nonlocal count\n        if row == n: count += 1; return\n        for c in range(n):\n            if c in cols or (row-c) in d1 or (row+c) in d2: continue\n            bt(row+1, cols|{c}, d1|{row-c}, d2|{row+c})\n    bt(0, set(), set(), set())\n    return count", "code_javascript": "function totalNQueens(n) {\n  let count = 0;\n  const bt = (row, cols, d1, d2) => {\n    if (row === n) { count++; return; }\n    for (let c = 0; c < n; c++) {\n      if (cols.has(c) || d1.has(row-c) || d2.has(row+c)) continue;\n      bt(row+1, new Set([...cols,c]), new Set([...d1,row-c]), new Set([...d2,row+c]));\n    }\n  };\n  bt(0, new Set(), new Set(), new Set());\n  return count;\n}"},
    ],
    "Maximum XOR of Two Numbers in an Array": [
        {"title": "Trie", "content": "Build binary Trie. For each number traverse trying opposite bit when available to maximize XOR. O(n * 32) time.", "code_python": "def findMaximumXOR(nums):\n    root = {}\n    for x in nums:\n        n = root\n        for b in range(31, -1, -1):\n            bit = (x >> b) & 1\n            n = n.setdefault(bit, {})\n    best = 0\n    for x in nums:\n        n, cur = root, 0\n        for b in range(31, -1, -1):\n            bit = (x >> b) & 1\n            want = 1 - bit\n            cur <<= 1\n            if want in n: n, cur = n[want], cur | 1\n            else: n = n[bit]\n        best = max(best, cur ^ x)\n    return best", "code_javascript": "function findMaximumXOR(nums) {\n  const root = {};\n  for (const x of nums) { let n = root; for (let b = 31; b >= 0; b--) { const bit = (x>>b)&1; n = n[bit] = n[bit] || {}; } }\n  let best = 0;\n  for (const x of nums) { let n = root, cur = 0; for (let b = 31; b >= 0; b--) { const bit = (x>>b)&1, want = 1-bit; cur <<= 1; if (n[want]) { n = n[want]; cur |= 1; } else n = n[bit]; } best = Math.max(best, cur ^ x); }\n  return best;\n}"},
    ],
    "Count of Smaller Numbers After Self": [
        {"title": "Merge Sort / Fenwick", "content": "From right to left insert into sorted structure; count smaller. Or merge sort count inversions. O(n log n) time.", "code_python": "def countSmaller(nums):\n    res = [0] * len(nums)\n    def merge_sort(inds):\n        if len(inds) <= 1: return inds\n        m = len(inds) // 2\n        L = merge_sort(inds[:m]); R = merge_sort(inds[m:])\n        j = 0\n        for i in range(len(L)):\n            while j < len(R) and nums[R[j]] < nums[L[i]]: j += 1\n            res[L[i]] += j\n        return sorted(inds, key=lambda i: nums[i])\n    merge_sort(list(range(len(nums))))\n    return res", "code_javascript": "function countSmaller(nums) {\n  const res = Array(nums.length).fill(0);\n  const inds = nums.map((_,i)=>i);\n  const merge = (l, r) => {\n    if (r - l <= 1) return inds.slice(l, r);\n    const m = (l+r)>>1;\n    const L = merge(l, m), R = merge(m, r);\n    let j = 0;\n    for (let i = 0; i < L.length; i++) { while (j < R.length && nums[R[j]] < nums[L[i]]) j++; res[L[i]] += j; }\n    return [...L, ...R].sort((a,b)=>nums[a]-nums[b]);\n  };\n  merge(0, nums.length);\n  return res;\n}"},
    ],
    "Remove Invalid Parentheses": [
        {"title": "BFS", "content": "Find min removals; BFS remove one char at a time, check valid, add to result. Use set for dedup. O(2^n) worst.", "code_python": "def removeInvalidParentheses(s):\n    def valid(x):\n        b = 0\n        for c in x:\n            if c == '(': b += 1\n            elif c == ')': b -= 1\n            if b < 0: return False\n        return b == 0\n    level = {s}\n    while level:\n        ok = [x for x in level if valid(x)]\n        if ok: return ok\n        level = {x[:i]+x[i+1:] for x in level for i in range(len(x))}\n    return ['']", "code_javascript": "function removeInvalidParentheses(s) {\n  const valid = (x) => { let b = 0; for (const c of x) { if (c==='(') b++; else if (c===')') b--; if (b<0) return false; } return b===0; };\n  let level = new Set([s]);\n  while (level.size) { const ok = [...level].filter(valid); if (ok.length) return ok; level = new Set([...level].flatMap(x=>[...Array(x.length)].map((_,i)=>x.slice(0,i)+x.slice(i+1)))); }\n  return [''];\n}"},
    ],
    "Find the Duplicate Number": [
        {"title": "Floyd's Cycle", "content": "Array as linked list i->nums[i]. Find cycle start (duplicate). Or binary search on value: count elements <= mid. O(n) time, O(1) space.", "code_python": "def findDuplicate(nums):\n    slow = fast = nums[0]\n    while True:\n        slow = nums[slow]; fast = nums[nums[fast]]\n        if slow == fast: break\n    slow = nums[0]\n    while slow != fast: slow = nums[slow]; fast = nums[fast]\n    return slow", "code_javascript": "function findDuplicate(nums) {\n  let slow = nums[0], fast = nums[0];\n  do { slow = nums[slow]; fast = nums[nums[fast]]; } while (slow !== fast);\n  slow = nums[0];\n  while (slow !== fast) { slow = nums[slow]; fast = nums[fast]; }\n  return slow;\n}"},
    ],
    "Set Matrix Zeroes": [
        {"title": "First Row/Col as Flag", "content": "Use first row and first col to mark; handle first row/col separately. Two passes. O(1) space.", "code_python": "def setZeroes(matrix):\n    m, n = len(matrix), len(matrix[0])\n    r0 = any(matrix[0][j]==0 for j in range(n))\n    c0 = any(matrix[i][0]==0 for i in range(m))\n    for i in range(1, m):\n        for j in range(1, n):\n            if matrix[i][j]==0: matrix[i][0]=0; matrix[0][j]=0\n    for i in range(1, m):\n        for j in range(1, n):\n            if matrix[i][0]==0 or matrix[0][j]==0: matrix[i][j]=0\n    if r0: matrix[0][:] = [0]*n\n    if c0: for i in range(m): matrix[i][0]=0", "code_javascript": "function setZeroes(matrix) {\n  const m = matrix.length, n = matrix[0].length;\n  const r0 = matrix[0].some(v=>v===0), c0 = matrix.some(row=>row[0]===0);\n  for (let i = 1; i < m; i++) for (let j = 1; j < n; j++) if (matrix[i][j]===0) matrix[i][0]=0, matrix[0][j]=0;\n  for (let i = 1; i < m; i++) for (let j = 1; j < n; j++) if (matrix[i][0]===0 || matrix[0][j]===0) matrix[i][j]=0;\n  if (r0) matrix[0].fill(0);\n  if (c0) for (let i = 0; i < m; i++) matrix[i][0]=0;\n}"},
    ],
    "Spiral Matrix": [
        {"title": "Layer by Layer", "content": "Four boundaries top,bottom,left,right. Traverse top row, right col, bottom row, left col; shrink. O(m*n) time.", "code_python": "def spiralOrder(matrix):\n    if not matrix: return []\n    t, b, l, r = 0, len(matrix)-1, 0, len(matrix[0])-1\n    out = []\n    while t <= b and l <= r:\n        for j in range(l, r+1): out.append(matrix[t][j])\n        t += 1\n        for i in range(t, b+1): out.append(matrix[i][r])\n        r -= 1\n        if t <= b:\n            for j in range(r, l-1, -1): out.append(matrix[b][j])\n            b -= 1\n        if l <= r:\n            for i in range(b, t-1, -1): out.append(matrix[i][l])\n            l += 1\n    return out", "code_javascript": "function spiralOrder(matrix) {\n  if (!matrix.length) return [];\n  let t = 0, b = matrix.length-1, l = 0, r = matrix[0].length-1, out = [];\n  while (t <= b && l <= r) {\n    for (let j = l; j <= r; j++) out.push(matrix[t][j]); t++;\n    for (let i = t; i <= b; i++) out.push(matrix[i][r]); r--;\n    if (t <= b) { for (let j = r; j >= l; j--) out.push(matrix[b][j]); b--; }\n    if (l <= r) { for (let i = b; i >= t; i--) out.push(matrix[i][l]); l++; }\n  }\n  return out;\n}"},
    ],
    "Rotate Image": [
        {"title": "Transpose + Reverse", "content": "Transpose matrix (swap [i][j] with [j][i] for i<j), then reverse each row. O(n²) time, in-place.", "code_python": "def rotate(matrix):\n    n = len(matrix)\n    for i in range(n):\n        for j in range(i+1, n): matrix[i][j], matrix[j][i] = matrix[j][i], matrix[i][j]\n    for i in range(n): matrix[i].reverse()", "code_javascript": "function rotate(matrix) {\n  const n = matrix.length;\n  for (let i = 0; i < n; i++) for (let j = i+1; j < n; j++) [matrix[i][j], matrix[j][i]] = [matrix[j][i], matrix[i][j]];\n  for (let i = 0; i < n; i++) matrix[i].reverse();\n}"},
    ],
    "Search a 2D Matrix": [
        {"title": "Binary Search", "content": "Treat as 1D sorted array; index i -> row i//n, col i%n. O(log(m*n)) time.", "code_python": "def searchMatrix(matrix, target):\n    if not matrix: return False\n    m, n = len(matrix), len(matrix[0])\n    lo, hi = 0, m * n - 1\n    while lo <= hi:\n        mid = (lo + hi) // 2\n        v = matrix[mid // n][mid % n]\n        if v == target: return True\n        if v < target: lo = mid + 1\n        else: hi = mid - 1\n    return False", "code_javascript": "function searchMatrix(matrix, target) {\n  if (!matrix.length) return false;\n  const m = matrix.length, n = matrix[0].length;\n  let lo = 0, hi = m*n - 1;\n  while (lo <= hi) { const mid = (lo+hi)>>1, v = matrix[Math.floor(mid/n)][mid%n]; if (v===target) return true; if (v<target) lo = mid+1; else hi = mid-1; }\n  return false;\n}"},
    ],
    "Search a 2D Matrix II": [
        {"title": "Start Top-Right", "content": "From top-right: if current>target move left; if current<target move down. O(m+n) time.", "code_python": "def searchMatrix(matrix, target):\n    if not matrix: return False\n    i, j = 0, len(matrix[0]) - 1\n    while i < len(matrix) and j >= 0:\n        if matrix[i][j] == target: return True\n        if matrix[i][j] > target: j -= 1\n        else: i += 1\n    return False", "code_javascript": "function searchMatrix(matrix, target) {\n  if (!matrix.length) return false;\n  let i = 0, j = matrix[0].length - 1;\n  while (i < matrix.length && j >= 0) { if (matrix[i][j]===target) return true; if (matrix[i][j]>target) j--; else i++; }\n  return false;\n}"},
    ],
    "Find First and Last Position of Element in Sorted Array": [
        {"title": "Two Binary Searches", "content": "Left bound: first i where nums[i]>=target. Right bound: first i where nums[i]>target minus 1. O(log n) time.", "code_python": "def searchRange(nums, target):\n    def left():\n        lo, hi = 0, len(nums)\n        while lo < hi:\n            mid = (lo+hi)//2\n            if nums[mid] < target: lo = mid+1\n            else: hi = mid\n        return lo\n    def right():\n        lo, hi = 0, len(nums)\n        while lo < hi:\n            mid = (lo+hi)//2\n            if nums[mid] <= target: lo = mid+1\n            else: hi = mid\n        return lo - 1\n    l, r = left(), right()\n    return [l, r] if l <= r else [-1, -1]", "code_javascript": "function searchRange(nums, target) {\n  const left = () => { let lo = 0, hi = nums.length; while (lo < hi) { const mid = (lo+hi)>>1; if (nums[mid] < target) lo = mid+1; else hi = mid; } return lo; };\n  const right = () => { let lo = 0, hi = nums.length; while (lo < hi) { const mid = (lo+hi)>>1; if (nums[mid] <= target) lo = mid+1; else hi = mid; } return lo-1; };\n  const l = left(), r = right(); return l <= r ? [l, r] : [-1, -1];\n}"},
    ],
    "Next Permutation": [
        {"title": "In-Place", "content": "Find largest i with nums[i]<nums[i+1]. Find largest j>i with nums[j]>nums[i]; swap; reverse nums[i+1:]. O(n) time.", "code_python": "def nextPermutation(nums):\n    i = len(nums) - 2\n    while i >= 0 and nums[i] >= nums[i+1]: i -= 1\n    if i >= 0:\n        j = len(nums) - 1\n        while nums[j] <= nums[i]: j -= 1\n        nums[i], nums[j] = nums[j], nums[i]\n    nums[i+1:] = reversed(nums[i+1:])", "code_javascript": "function nextPermutation(nums) {\n  let i = nums.length - 2;\n  while (i >= 0 && nums[i] >= nums[i+1]) i--;\n  if (i >= 0) { let j = nums.length - 1; while (nums[j] <= nums[i]) j--; [nums[i], nums[j]] = [nums[j], nums[i]]; }\n  for (let l = i+1, r = nums.length-1; l < r; l++, r--) [nums[l], nums[r]] = [nums[r], nums[l]];\n}"},
    ],
    "Pow(x, n)": [
        {"title": "Binary Exponentiation", "content": "x^n = (x^2)^(n/2) if n even; x * (x^2)^((n-1)/2) if odd. Handle negative n. O(log n) time.", "code_python": "def myPow(x, n):\n    if n < 0: x, n = 1/x, -n\n    out = 1\n    while n:\n        if n & 1: out *= x\n        x *= x; n //= 2\n    return out", "code_javascript": "function myPow(x, n) {\n  if (n < 0) { x = 1/x; n = -n; }\n  let out = 1;\n  while (n) { if (n & 1) out *= x; x *= x; n = n >>> 1; }\n  return out;\n}"},
    ],
    "Subarray Sum Equals K": [
        {"title": "Prefix Sum + Map", "content": "Map prefix sum -> count. For each prefix add count of (prefix - k). O(n) time, O(n) space.", "code_python": "def subarraySum(nums, k):\n    from collections import Counter\n    pre = 0; cnt = Counter({0: 1}); ans = 0\n    for x in nums:\n        pre += x\n        ans += cnt.get(pre - k, 0)\n        cnt[pre] = cnt.get(pre, 0) + 1\n    return ans", "code_javascript": "function subarraySum(nums, k) {\n  const cnt = { 0: 1 };\n  let pre = 0, ans = 0;\n  for (const x of nums) { pre += x; ans += cnt[pre - k] || 0; cnt[pre] = (cnt[pre]||0) + 1; }\n  return ans;\n}"},
    ],
}

# Rich format: Prerequisites, Intuition, Algorithm, Code, Complexity, Common Pitfalls 
RICH_SOLUTIONS = {
    "Min Stack": {
        "prerequisites": [
            "Stack Data Structure - Understanding LIFO (Last In First Out) operations including push, pop, and peek",
            "Auxiliary Data Structures - Using additional stacks or variables to track extra state alongside the main data structure",
            "Space-Time Tradeoffs - Trading extra memory for faster operations (e.g., O(n) space for O(1) getMin)",
        ],
        "approaches": [
            {
                "title": "1. Brute Force",
                "intuition": "To get the minimum value, this approach simply looks through all elements in the stack. Since a normal stack does not store any extra information about the minimum, the only way to find it is to temporarily remove every element, track the smallest one, and then put everything back. It's easy to understand but slow because each getMin call scans the entire stack.",
                "algorithm": "To push a value, append it to the stack.\nTo pop, remove the top element of the stack.\nTo top, return the last element.\nTo getMin:\n- Create a temporary list.\n- Pop all elements from the stack while tracking the smallest value.\n- Push all elements back from the temporary list to restore the stack.\n- Return the smallest value found.",
                "code": """class MinStack:

    def __init__(self):
        self.stack = []

    def push(self, val: int) -> None:
        self.stack.append(val)

    def pop(self) -> None:
        self.stack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        tmp = []
        mini = self.stack[-1]

        while len(self.stack):
            mini = min(mini, self.stack[-1])
            tmp.append(self.stack.pop())

        while len(tmp):
            self.stack.append(tmp.pop())

        return mini""",
                "code_javascript": """class MinStack {
  constructor() {
    this.stack = [];
  }
  push(val) {
    this.stack.push(val);
  }
  pop() {
    this.stack.pop();
  }
  top() {
    return this.stack[this.stack.length - 1];
  }
  getMin() {
    const tmp = [];
    let mini = this.stack[this.stack.length - 1];
    while (this.stack.length) {
      mini = Math.min(mini, this.stack[this.stack.length - 1]);
      tmp.push(this.stack.pop());
    }
    while (tmp.length) this.stack.push(tmp.pop());
    return mini;
  }
}""",
                "complexity": "Time complexity: O(n) for getMin() and O(1) for other operations.\nSpace complexity: O(n) for getMin() and O(1) for other operations.",
            },
            {
                "title": "2. Two Stacks",
                "intuition": "Instead of searching the whole stack to find the minimum every time, we can keep a second stack that always stores the minimum value up to that point. So whenever we push a new value, we compare it with the current minimum and store the smaller one on the minStack. This guarantees that the top of minStack is always the minimum of the entire stack — allowing getMin() to work in constant time.",
                "algorithm": "Maintain two stacks:\n- stack → stores all pushed values.\n- minStack → stores the minimum so far at each level.\nOn push(val): Push val onto stack; compute new minimum (between val and current min on minStack); push this minimum onto minStack.\nOn pop(): Pop from both stack and minStack to keep them aligned.\nOn top(): Return the top of stack.\nOn getMin(): Return the top of minStack.",
                "code": """class MinStack:
    def __init__(self):
        self.stack = []
        self.minStack = []

    def push(self, val: int) -> None:
        self.stack.append(val)
        val = min(val, self.minStack[-1] if self.minStack else val)
        self.minStack.append(val)

    def pop(self) -> None:
        self.stack.pop()
        self.minStack.pop()

    def top(self) -> int:
        return self.stack[-1]

    def getMin(self) -> int:
        return self.minStack[-1]""",
                "code_javascript": """class MinStack {
  constructor() {
    this.stack = [];
    this.minStack = [];
  }
  push(val) {
    this.stack.push(val);
    val = Math.min(val, this.minStack.length ? this.minStack[this.minStack.length - 1] : val);
    this.minStack.push(val);
  }
  pop() {
    this.stack.pop();
    this.minStack.pop();
  }
  top() {
    return this.stack[this.stack.length - 1];
  }
  getMin() {
    return this.minStack[this.minStack.length - 1];
  }
}""",
                "complexity": "Time complexity: O(1) for all operations.\nSpace complexity: O(n).",
            },
            {
                "title": "3. One Stack",
                "intuition": "This approach keeps only one stack and stores encoded values instead of the actual numbers. The trick is to record the difference between the pushed value and the current minimum. Whenever a new minimum is pushed, we store a negative encoded value, which signals that the minimum has changed. Later, when popping such a value, we can decode it to restore the previous minimum.",
                "algorithm": "Maintain: stack (encoded values), min (current minimum).\nPush(val): If stack empty push 0 and set min=val; else push val-min and update min if val is new min.\nPop(): Pop encoded value; if negative, restore previous min.\nTop(): If encoded > 0 return encoded+min else return min.\ngetMin(): Return min.",
                "code": """class MinStack:
    def __init__(self):
        self.min = float('inf')
        self.stack = []

    def push(self, val: int) -> None:
        if not self.stack:
            self.stack.append(0)
            self.min = val
        else:
            self.stack.append(val - self.min)
            if val < self.min:
                self.min = val

    def pop(self) -> None:
        if not self.stack:
            return
        pop = self.stack.pop()
        if pop < 0:
            self.min = self.min - pop

    def top(self) -> int:
        top = self.stack[-1]
        if top > 0:
            return top + self.min
        else:
            return self.min

    def getMin(self) -> int:
        return self.min""",
                "code_javascript": """class MinStack {
  constructor() {
    this.min = Number.POSITIVE_INFINITY;
    this.stack = [];
  }
  push(val) {
    if (!this.stack.length) {
      this.stack.push(0);
      this.min = val;
    } else {
      this.stack.push(val - this.min);
      if (val < this.min) this.min = val;
    }
  }
  pop() {
    if (!this.stack.length) return;
    const pop = this.stack.pop();
    if (pop < 0) this.min = this.min - pop;
  }
  top() {
    const top = this.stack[this.stack.length - 1];
    return top > 0 ? top + this.min : this.min;
  }
  getMin() {
    return this.min;
  }
}""",
                "complexity": "Time complexity: O(1) for all operations.\nSpace complexity: O(n).",
            },
        ],
        "common_pitfalls": "Not Synchronizing the Two Stacks: When using the two-stack approach, only push to minStack when the new value is smaller than the current minimum. During pop(), only pop from minStack when the popped value equals the current minimum. Forgetting this causes incorrect minimums.\n\nInteger Overflow in the Encoded Value Approach: The one-stack solution stores val - min. With extreme integer values this can overflow. Use long for encoded values and minimum in fixed-width integer languages.",
    },
    "Two Sum": {
        "prerequisites": [
            "Hash Map / Hash Table - Storing values for O(1) lookup by key",
            "Array Traversal - Iterating through arrays and using indices",
            "Complement Pattern - Finding pairs that sum to a target by checking for (target - current) in a data structure",
        ],
        "approaches": [
            {
                "title": "1. Brute Force",
                "intuition": "Check every pair of indices (i, j) with i < j. If nums[i] + nums[j] == target, return [i, j]. Simple and correct but slow for large arrays.",
                "algorithm": "Use two nested loops: outer loop i from 0 to n-1, inner loop j from i+1 to n-1. If nums[i] + nums[j] == target, return [i, j]. Return empty if no pair found (problem guarantees one solution).",
                "code": """def twoSum(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []""",
                "code_javascript": """function twoSum(nums, target) {
  for (let i = 0; i < nums.length; i++) {
    for (let j = i + 1; j < nums.length; j++) {
      if (nums[i] + nums[j] === target) return [i, j];
    }
  }
  return [];
}""",
                "code_java": "public int[] twoSum(int[] nums, int target) {\n    for (int i = 0; i < nums.length; i++)\n        for (int j = i + 1; j < nums.length; j++)\n            if (nums[i] + nums[j] == target) return new int[]{i, j};\n    return new int[]{};\n}",
                "code_cpp": "vector<int> twoSum(const vector<int>& nums, int target) {\n    for (int i = 0; i < (int)nums.size(); i++)\n        for (int j = i + 1; j < (int)nums.size(); j++)\n            if (nums[i] + nums[j] == target) return {i, j};\n    return {};\n}",
                "complexity": "Time complexity: O(n²) - two nested loops.\nSpace complexity: O(1).",
            },
            {
                "title": "2. Optimal (Hash Map)",
                "intuition": "In one pass, for each number we need to know if (target - num) was already seen and at which index. A hash map lets us store each number and its index for O(1) lookup.",
                "algorithm": "Maintain a map: value -> index. For each index i and value n: compute need = target - n. If need is in the map, return [map[need], i]. Otherwise set map[n] = i. One pass guarantees we find the pair.",
                "code": """def twoSum(nums, target):
    seen = {}
    for i, n in enumerate(nums):
        need = target - n
        if need in seen:
            return [seen[need], i]
        seen[n] = i
    return []""",
                "code_javascript": """function twoSum(nums, target) {
  const seen = {};
  for (let i = 0; i < nums.length; i++) {
    const need = target - nums[i];
    if (need in seen) return [seen[need], i];
    seen[nums[i]] = i;
  }
  return [];
}""",
                "code_java": "public int[] twoSum(int[] nums, int target) {\n    Map<Integer, Integer> seen = new HashMap<>();\n    for (int i = 0; i < nums.length; i++) {\n        int need = target - nums[i];\n        if (seen.containsKey(need)) return new int[]{seen.get(need), i};\n        seen.put(nums[i], i);\n    }\n    return new int[]{};\n}",
                "code_cpp": "vector<int> twoSum(const vector<int>& nums, int target) {\n    unordered_map<int, int> seen;\n    for (int i = 0; i < (int)nums.size(); i++) {\n        int need = target - nums[i];\n        if (seen.count(need)) return {seen[need], i};\n        seen[nums[i]] = i;\n    }\n    return {};\n}",
                "complexity": "Time complexity: O(n) - single pass.\nSpace complexity: O(n) for the hash map.",
            },
        ],
        "common_pitfalls": "Using the same element twice: Ensure j starts at i+1 in brute force, and in the hash map approach you only look at indices before the current one.\n\nDuplicate values: The hash map approach overwrites the index for the same value; that is fine because we only need one valid pair.",
        "pattern_recognition": "Category: Hash Map / Two Sum (complement pattern).\n\nWhy: We need two indices whose values sum to target — i.e. for each value we look for (target - value). That \"lookup\" suggests a hash structure for O(1) check.\n\nSignals: \"find two numbers that sum to X\", \"return indices\", \"exactly one solution\" — classic two sum. If array were sorted, two pointers would also apply; unsorted → hash map.",
        "dry_run": "Sample: nums = [2, 7, 11, 15], target = 9.\n\nOptimal (hash map):\n- i=0, n=2, need=7; 7 not in map → seen = {2: 0}\n- i=1, n=7, need=2; 2 in map at index 0 → return [0, 1].\n\nBrute: (0,1) → 2+7=9 ✓ return [0, 1].",
        "edge_cases": "Empty input: problem states 2 <= n; no need to handle empty.\nSingle element: n >= 2 per constraints.\nDuplicates: hash map overwrites index; we only need one pair — correct index is the most recent, and we check (target - current) before inserting, so we still find a valid pair.\nLarge input: O(n) time and O(n) space avoid TLE.\nNegative values: no overflow; sum and complement work the same.",
        "interview_tips": "Explain: \"This is a two-sum style problem; we can brute-force all pairs in O(n²) or use a hash map to store value→index and in one pass check if (target - current) exists — O(n) time, O(n) space.\"\nFollow-ups: \"What if we need all pairs?\" — still hash map but collect pairs; \"What if array is sorted?\" — two pointers, O(1) space. \"What if no solution?\" — return empty or throw per problem.",
        "pitfalls": [
            {"title": "Using the same element twice", "wrong_example": "if nums[i] + nums[j] == target  # with j starting at 0", "correct_example": "for j in range(i + 1, len(nums))  # j must be after i", "warning": "Inner loop must start at i+1 so we never use the same index twice."},
            {"title": "Returning value instead of index", "wrong_example": "return [nums[i], nums[j]]", "correct_example": "return [i, j]", "warning": "Problem asks for indices, not the values."},
            {"title": "Hash map: checking after insert", "wrong_example": "seen[n] = i; if (target - n) in seen: ...", "correct_example": "if (target - n) in seen: return [seen[target-n], i]; seen[n] = i", "warning": "Check for complement before storing current element so we don't match self."},
        ],
    },
    "Best Time to Buy and Sell Stock": {
        "prerequisites": [
            "Array Traversal - Single pass through the array to track state",
            "Dynamic Programming (Kadane-style) - Tracking best answer so far while iterating",
            "Greedy - Choosing the best local decision (buy at min so far, sell today).",
        ],
        "approaches": [
            {
                "title": "1. Brute Force",
                "intuition": "Try every pair of days (i, j) with i < j: buy on day i, sell on day j. Profit is prices[j] - prices[i]. Track the maximum profit over all pairs. Correct but slow for large inputs.",
                "algorithm": "Use two nested loops: outer i from 0 to n-1, inner j from i+1 to n-1. Compute profit = prices[j] - prices[i]. Update maxProfit = max(maxProfit, profit). Return maxProfit (or 0 if no profit possible).",
                "code": """def maxProfit(prices):
    n = len(prices)
    max_profit = 0
    for i in range(n):
        for j in range(i + 1, n):
            profit = prices[j] - prices[i]
            max_profit = max(max_profit, profit)
    return max_profit""",
                "code_javascript": """function maxProfit(prices) {
  let maxProfit = 0;
  for (let i = 0; i < prices.length; i++) {
    for (let j = i + 1; j < prices.length; j++) {
      const profit = prices[j] - prices[i];
      maxProfit = Math.max(maxProfit, profit);
    }
  }
  return maxProfit;
}""",
                "code_java": "public int maxProfit(int[] prices) {\n    int maxProfit = 0;\n    for (int i = 0; i < prices.length; i++)\n        for (int j = i + 1; j < prices.length; j++)\n            maxProfit = Math.max(maxProfit, prices[j] - prices[i]);\n    return maxProfit;\n}",
                "code_cpp": "int maxProfit(vector<int>& prices) {\n    int maxProfit = 0;\n    for (int i = 0; i < (int)prices.size(); i++)\n        for (int j = i + 1; j < (int)prices.size(); j++)\n            maxProfit = max(maxProfit, prices[j] - prices[i]);\n    return maxProfit;\n}",
                "complexity": "Time complexity: O(n²) - two nested loops.\nSpace complexity: O(1).",
            },
            {
                "title": "2. Optimal (One Pass)",
                "intuition": "In a single pass, we only need to know the minimum price seen so far. For each day, if we had bought at that minimum and sold today, our profit would be price - minPrice. Track the minimum price and the maximum profit seen so far.",
                "algorithm": "Initialize minPrice = infinity (or prices[0]) and maxProfit = 0. For each price in prices: update minPrice = min(minPrice, price); profit = price - minPrice; maxProfit = max(maxProfit, profit). Return maxProfit.",
                "code": """def maxProfit(prices):
    if not prices:
        return 0
    min_price = float('inf')
    max_profit = 0
    for price in prices:
        min_price = min(min_price, price)
        profit = price - min_price
        max_profit = max(max_profit, profit)
    return max_profit""",
                "code_javascript": """function maxProfit(prices) {
  if (prices.length === 0) return 0;
  let minPrice = Infinity;
  let maxProfit = 0;
  for (const price of prices) {
    minPrice = Math.min(minPrice, price);
    const profit = price - minPrice;
    maxProfit = Math.max(maxProfit, profit);
  }
  return maxProfit;
}""",
                "code_java": "public int maxProfit(int[] prices) {\n    if (prices.length == 0) return 0;\n    int minPrice = Integer.MAX_VALUE, maxProfit = 0;\n    for (int price : prices) {\n        minPrice = Math.min(minPrice, price);\n        maxProfit = Math.max(maxProfit, price - minPrice);\n    }\n    return maxProfit;\n}",
                "code_cpp": "int maxProfit(vector<int>& prices) {\n    if (prices.empty()) return 0;\n    int minPrice = INT_MAX, maxProfit = 0;\n    for (int price : prices) {\n        minPrice = min(minPrice, price);\n        maxProfit = max(maxProfit, price - minPrice);\n    }\n    return maxProfit;\n}",
                "complexity": "Time complexity: O(n) - single pass.\nSpace complexity: O(1).",
            },
        ],
        "common_pitfalls": "Selling before buying: Ensure you only consider profit when j > i (sell day after buy day). In the one-pass solution, we implicitly buy at minPrice (which is always from a previous day) and sell at the current price.\n\nEmpty or single-day input: Return 0 when no profit is possible (e.g. empty array or strictly decreasing prices).",
    },
}


def _is_placeholder_code(code: str) -> bool:
    """Return True if the code is a placeholder (e.g. 'See Python tab for logic') rather than real implementation."""
    if not code or not isinstance(code, str):
        return True
    s = code.strip()
    return (
        "See Python" in s or "See python" in s or
        "Same algorithm as Python" in s or "Same algorithm as python" in s or
        "Use arrays, pointers, or hash table" in s or "See Python tab" in s
    )


def normalize_code_indent(code: str) -> str:
    """Normalize indentation: expand tabs to 4 spaces, then strip common leading whitespace. Preserves relative indent."""
    if code is None or not isinstance(code, str):
        return code
    code = code.replace("\t", "    ")
    lines = code.splitlines()
    min_indent = float("inf")
    for line in lines:
        if line.strip():
            m = re.match(r"^(\s*)", line)
            min_indent = min(min_indent, len(m.group(1)) if m else 0)
    if min_indent == 0 or min_indent == float("inf"):
        return "\n".join(lines)
    return "\n".join(line[min_indent:] if len(line) >= min_indent else line for line in lines)


def _brace_pretty_indent(code: str, indent_size: int = 4) -> str:
    """Re-indent brace-based code: insert newlines after { and }, then indent each line by brace depth."""
    if not code or not code.strip():
        return code
    code = code.replace("\t", "    ")
    # Insert newline after { and before/after } so structure is one-per-line
    code = re.sub(r"\{\s*", "{\n", code)
    code = re.sub(r"\s*\}\s*", "\n}\n", code)  # break before and after } so closing brace gets its own line
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    if not lines:
        return code.strip()
    out = []
    depth = 0
    for line in lines:
        opens = line.count("{")
        closes = line.count("}")
        # Closing brace line: indent one level less so } aligns with block start
        if line.strip() == "}":
            indent = max(0, depth - 1)
        else:
            indent = depth
        prefix = " " * (indent * indent_size)
        out.append(prefix + line)
        depth += opens - closes
        depth = max(0, depth)
    return "\n".join(out)


def normalize_code_indent_by_lang(code: str, code_key: str) -> str:
    """Normalize code: expand tabs, strip common leading space; for brace-based langs also apply brace pretty-indent."""
    if code is None or not isinstance(code, str):
        return code
    code = code.replace("\t", "    ")
    # Strip common leading whitespace first
    lines = code.splitlines()
    min_indent = float("inf")
    for line in lines:
        if line.strip():
            m = re.match(r"^(\s*)", line)
            min_indent = min(min_indent, len(m.group(1)) if m else 0)
    if min_indent and min_indent != float("inf"):
        lines = [line[min_indent:] if len(line) >= min_indent else line for line in lines]
    code = "\n".join(lines)
    # For brace-based languages, re-indent by brace depth so minified/ugly code looks readable
    if code_key in ("code_java", "code_javascript", "code_cpp", "code_c", "code_typescript"):
        code = _brace_pretty_indent(code, indent_size=4)
    return code


def _normalize_approach(
    approach: dict,
    problem_title: str = "",
    metadata: Optional[object] = None,
    enforce_signature: bool = True,
    metadata_from_registry: bool = False,
) -> dict:
    """Ensure approach has code_python (from code) and passes through code_* for supported languages. Fills missing from supplemental module. Never emits placeholder text.
    When metadata_from_registry is True, strips code that doesn't match the registry signature. When False, keeps all merged code so solutions in all languages are shown."""
    out = {k: v for k, v in approach.items() if k in ("title", "content", "intuition", "algorithm", "complexity", "complexity_time", "complexity_space")}
    code_python = approach.get("code_python") or approach.get("code")
    if code_python is not None and not _is_placeholder_code(code_python):
        out["code"] = code_python  # backward compat
        out["code_python"] = code_python
    for lang in ("code_javascript", "code_java", "code_cpp", "code_c", "code_go", "code_csharp", "code_typescript"):
        val = approach.get(lang)
        if val is not None and not _is_placeholder_code(val):
            out[lang] = val
    # Fill missing Java/C++/C/Go/C# from supplemental multilang module (real code only, no placeholders)
    try:
        from solution_code_multilang import get_multilang
        supplemental = get_multilang(problem_title, approach.get("title") or "")
        for lang in ("code_java", "code_cpp", "code_c", "code_go", "code_csharp"):
            if out.get(lang) is None and supplemental.get(lang) and not _is_placeholder_code(supplemental[lang]):
                out[lang] = supplemental[lang]
    except ImportError:
        pass
    for key in ("code", "code_python", "code_javascript", "code_java", "code_cpp", "code_c", "code_go", "code_csharp", "code_typescript"):
        if key in out and out[key]:
            out[key] = normalize_code_indent_by_lang(out[key], key)
    # Only strip by signature when we have registry metadata; otherwise keep all merged code so all languages show.
    if enforce_signature and metadata is not None and metadata_from_registry:
        key_to_lang = {
            "code_python": "python",
            "code_javascript": "javascript",
            "code_java": "java",
            "code_cpp": "cpp",
            "code_go": "go",
            "code_csharp": "csharp",
            "code_typescript": "typescript",
        }
        for code_key, lang in key_to_lang.items():
            if out.get(code_key):
                out[code_key] = align_solution_code_to_metadata(out[code_key], lang, metadata)
        # Keep only signature-compatible code snippets.
        for code_key, lang in key_to_lang.items():
            code_val = out.get(code_key)
            if not code_val:
                continue
            expected_sig = metadata_signature(metadata, lang)
            actual_sig = extract_signature(code_val, lang)
            if not expected_sig or not actual_sig or not signatures_match(
                expected_sig,
                actual_sig,
                strict_types=True,
                strict_param_names=False,
            ):
                out.pop(code_key, None)
        # Keep legacy "code" mirror aligned to python.
        if out.get("code_python"):
            out["code"] = out["code_python"]
        else:
            out.pop("code", None)
    return out


def _parse_complexity_from_content(content: str) -> str:
    """Extract 'Time: O(...) Space: O(...)' or 'O(...) time, O(...) space' from content for consistent complexity field."""
    if not content:
        return ""
    # "Time: O(n)\nSpace: O(1)" or "Time: O(n²) Space: O(1)"
    m = re.search(r"Time:\s*O\([^)]+\)[\s\S]*?Space:\s*O\([^)]+\)", content, re.IGNORECASE)
    if m:
        return ("Time complexity: " + m.group(0).replace("Time:", "").split("Space:")[0].strip() + ".\n"
                "Space complexity: " + (m.group(0).split("Space:")[1] or "").strip() + ".")
    # "O(n) time, O(1) space." or "O(n²) time, O(1) space."
    m = re.search(r"O\([^)]+\)\s*time[^.]*\.?\s*O\([^)]+\)\s*space", content, re.IGNORECASE)
    if m:
        return "Time complexity: " + m.group(0).split(",")[0].strip() + ".\nSpace complexity: " + (m.group(0).split(",")[1] or "").strip() + "."
    # Single "O(...) time" or "O(...) space"
    parts = []
    for prefix, label in [("time", "Time"), ("space", "Space")]:
        m = re.search(r"O\([^)]+\)\s*" + prefix + r"[^.\n]*", content, re.IGNORECASE)
        if m:
            parts.append(f"{label} complexity: {m.group(0).strip()}.")
    return "\n".join(parts) if parts else ""


def _simple_entry_to_rich(e: dict) -> dict:
    """Convert a SOLUTIONS list entry (title, content, optional code_*) into rich format: title, intuition, algorithm, code*, complexity."""
    title = e.get("title", "")
    content = (e.get("content") or "").strip()
    complexity_parsed = _parse_complexity_from_content(content)
    # Use content as intuition; if we parsed complexity, intuition can be the part before "Time:" or first sentence
    intuition = content
    if "Time:" in content or "time, " in content.lower():
        for sep in ["Time:", "time,", "time.", "Space:"]:
            if sep in content:
                intuition = content.split(sep)[0].strip()
                if intuition.endswith("."):
                    break
                intuition = content
                break
    approach = {
        "title": title,
        "intuition": intuition or "",
        "algorithm": e.get("algorithm") or "",
    }
    code_python = e.get("code_python") or e.get("code")
    if code_python is not None:
        approach["code"] = code_python
        approach["code_python"] = code_python
    for lang in ("code_javascript", "code_java", "code_cpp", "code_c", "code_go", "code_csharp", "code_typescript"):
        if e.get(lang) is not None:
            approach[lang] = e[lang]
    approach["complexity"] = e.get("complexity") or complexity_parsed or ("See approach description." if content else "")
    return approach


def _first_non_empty(values, default=""):
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return default


def _infer_alignment_metadata(title: str, approaches: list) -> Optional[ProblemFunctionMetadata]:
    """Infer a schema for alignment when explicit registry metadata is missing."""
    try:
        from problem_metadata_registry import get_metadata
        entry = get_metadata(title)
        if entry is not None:
            return entry[0]
    except Exception:
        pass

    signatures_by_lang = {}
    try:
        from seed_starters import get_starters_for_problem
        starters = get_starters_for_problem(title) or {}
        for lang in REQUIRED_SIGNATURE_LANGS:
            sig = extract_signature(starters.get(f"starter_code_{lang}") or "", lang)
            if sig:
                signatures_by_lang[lang] = sig
    except Exception:
        pass

    if approaches:
        first = approaches[0] if isinstance(approaches[0], dict) else {}
        for lang in REQUIRED_SIGNATURE_LANGS:
            ckey = LANG_CODE_KEY[lang]
            code = first.get(ckey) or (first.get("code") if lang == "python" else "")
            sig = extract_signature(code or "", lang)
            if sig and lang not in signatures_by_lang:
                signatures_by_lang[lang] = sig

    if not signatures_by_lang:
        return None

    preferred = (
        signatures_by_lang.get("python")
        or signatures_by_lang.get("javascript")
        or signatures_by_lang.get("java")
        or next(iter(signatures_by_lang.values()))
    )
    if preferred is None:
        return None

    param_names = [p.name for p in preferred.params]
    return_type_by_language = {}
    param_types_by_lang = [dict() for _ in param_names]

    for lang, sig in signatures_by_lang.items():
        if sig.return_type:
            return_type_by_language[lang] = sig.return_type
        for i, p in enumerate(sig.params):
            if i >= len(param_types_by_lang):
                break
            if p.type:
                param_types_by_lang[i][lang] = p.type

    canonical_return = _first_non_empty(
        [
            return_type_by_language.get("python", ""),
            return_type_by_language.get("java", ""),
            return_type_by_language.get("cpp", ""),
            "int",
        ]
    )

    params = []
    for i, pname in enumerate(param_names):
        typed = param_types_by_lang[i]
        canonical_ptype = _first_non_empty(
            [
                typed.get("python", ""),
                typed.get("java", ""),
                typed.get("cpp", ""),
                "int",
            ]
        )
        full_param_map = typed if all(lang in typed for lang in SUPPORTED_LANGUAGES) else None
        params.append(
            ProblemFunctionParam(
                name=pname,
                type=canonical_ptype,
                type_by_language=full_param_map,
            )
        )

    full_return_map = return_type_by_language if all(lang in return_type_by_language for lang in SUPPORTED_LANGUAGES) else None

    return ProblemFunctionMetadata(
        function_name=preferred.function_name,
        return_type=canonical_return,
        return_type_by_language=full_return_map,
        parameters=params,
    )


# Optional: cached YouTube video ID per problem (Video Explanation section). Populate via script or YouTube API.
YOUTUBE_VIDEO_IDS = {
    "Two Sum": "KLlXCFG5TnA",
    "Best Time to Buy and Sell Stock": "1pkOgXD63yU",
    "Contains Duplicate": "3OamzN90kPg",
    "Valid Anagram": "9UtInBqnCgA",
    "Valid Palindrome": "jJXJ16kPFWg",
    "Product of Array Except Self": "bNvIQI2wAjk",
    "Maximum Subarray": "5WZl3MMT0Eg",
    "3Sum": "jzZsG8nc2N0",
    "Container With Most Water": "UuiTKBwPgAo",
    "Longest Substring Without Repeating Characters": "wi4pETE4Ubhk",
    "Climbing Stairs": "Y0lT9FSckIM",
    "Binary Search": "s4DPMJct5J4",
}

_GENERATED_SOLUTIONS_DIR = Path(__file__).resolve().parent / "generated_solutions"
_GENERATED_SOLUTIONS_CACHE = {}


def _slug_title(title: str) -> str:
    return re.sub(r"[^\w\-]", "_", (title or "").strip())[:80]


def _load_generated_solution_override(title: str):
    """Load generated solution JSON for title if present; cache results."""
    if title in _GENERATED_SOLUTIONS_CACHE:
        return _GENERATED_SOLUTIONS_CACHE[title]
    slug = _slug_title(title)
    path = _GENERATED_SOLUTIONS_DIR / f"{slug}.json"
    if not path.exists():
        _GENERATED_SOLUTIONS_CACHE[title] = None
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            data = None
    except Exception:
        data = None
    _GENERATED_SOLUTIONS_CACHE[title] = data
    return data


def _get_metadata_and_registry_flag(title: str, raw_approaches: list):
    """Return (metadata, metadata_from_registry). Use registry when present so signature filtering only runs for registered problems."""
    try:
        from problem_metadata_registry import get_metadata
        entry = get_metadata(title)
        if entry is not None:
            return (entry[0], True)
    except Exception:
        pass
    meta = _infer_alignment_metadata(title, raw_approaches) if raw_approaches else None
    return (meta, False)


def get_solutions_for_problem(title: str, enforce_signature: bool = True):
    """Return dict with approaches (list), optional prerequisites, common_pitfalls, youtube_video_id. Or None.
    Approaches are in LEARNING ORDER: Brute Force first, then Better, then Optimal. Each has intuition, algorithm, code (all langs), complexity."""
    generated = _load_generated_solution_override(title)
    if generated and isinstance(generated.get("approaches"), list):
        raw_approaches = list(generated.get("approaches") or [])
        metadata, from_registry = _get_metadata_and_registry_flag(title, raw_approaches)
        approaches = [
            _normalize_approach(
                a,
                title,
                metadata=metadata,
                # Generated outputs are already stage-validated; keep all language blocks visible.
                enforce_signature=False,
                metadata_from_registry=from_registry,
            )
            for a in raw_approaches
            if isinstance(a, dict)
        ]
        out = dict(generated)
        out["approaches"] = approaches
        if not out.get("pattern_recognition"):
            out["pattern_recognition"] = (out.get("patternRecognition") or "").strip()
        if not out.get("dry_run"):
            out["dry_run"] = (out.get("dryRun") or "").strip()
        if not out.get("edge_cases"):
            out["edge_cases"] = (out.get("edgeCases") or "").strip()
        if not out.get("common_pitfalls"):
            out["common_pitfalls"] = (
                out.get("commonPitfalls")
                or out.get("pitfalls")
                or ""
            )
        out["youtube_video_id"] = YOUTUBE_VIDEO_IDS.get(title)
        return out

    if title in RICH_SOLUTIONS:
        rich = RICH_SOLUTIONS[title]
        raw_approaches = list(rich["approaches"] or [])
        metadata, from_registry = _get_metadata_and_registry_flag(title, raw_approaches)
        approaches = [
            _normalize_approach(
                a,
                title,
                metadata=metadata,
                enforce_signature=enforce_signature,
                metadata_from_registry=from_registry,
            )
            for a in raw_approaches
        ]
        out = {**rich, "approaches": approaches}
        out["youtube_video_id"] = YOUTUBE_VIDEO_IDS.get(title)
        return out
    entries = SOLUTIONS.get(title)
    if not entries:
        return None
    raw_approaches = [_simple_entry_to_rich(e) for e in entries]
    metadata, from_registry = _get_metadata_and_registry_flag(title, raw_approaches)
    approaches = [
        _normalize_approach(
            e,
            title,
            metadata=metadata,
            enforce_signature=enforce_signature,
            metadata_from_registry=from_registry,
        )
        for e in raw_approaches
    ]
    return {
        "approaches": approaches,
        "prerequisites": None,
        "common_pitfalls": None,
        "youtube_video_id": YOUTUBE_VIDEO_IDS.get(title),
    }
