"""
LeetCode-style problem-specific starter and driver code.
Each problem has its own function signature; driver handles stdin parsing and output.
Keys are problem titles (must match seed_problems_top100 / seed_db).
"""

# Format: (starter_py, driver_py, starter_js, driver_js)
STARTERS = {
    "Contains Duplicate": (
        "def containsDuplicate(nums):\n    # Return True if any value appears at least twice, else False\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = containsDuplicate(nums)
    print('true' if result else 'false')""",
        "function containsDuplicate(nums) {\n    // Return true if any value appears at least twice\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = containsDuplicate(nums);
    console.log(result ? 'true' : 'false');
    rl.close();
});""",
    ),
    "Best Time to Buy and Sell Stock": (
        "def maxProfit(prices):\n    # Return max profit (buy one day, sell another). Return 0 if no profit.\n    pass",
        """if __name__ == "__main__":
    import sys
    prices = list(map(int, sys.stdin.read().strip().split()))
    result = maxProfit(prices)
    print(result)""",
        "function maxProfit(prices) {\n    // Return max profit\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const prices = line.split(' ').map(Number);
    const result = maxProfit(prices);
    console.log(result);
    rl.close();
});""",
    ),
    "Valid Anagram": (
        "def isAnagram(s, t):\n    # Return True if t is an anagram of s\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    s, t = lines[0], lines[1]
    result = isAnagram(s, t)
    print('true' if result else 'false')""",
        "function isAnagram(s, t) {\n    // Return true if t is an anagram of s\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const [s, t] = lines;
    const result = isAnagram(s, t);
    console.log(result ? 'true' : 'false');
});""",
    ),
    "Product of Array Except Self": (
        "def productExceptSelf(nums):\n    # Return array where answer[i] = product of all nums except nums[i]. O(n), no division.\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = productExceptSelf(nums)
    print(' '.join(map(str, result)))""",
        "function productExceptSelf(nums) {\n    // Return array\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = productExceptSelf(nums);
    console.log(result.join(' '));
    rl.close();
});""",
    ),
    "Maximum Product Subarray": (
        "def maxProduct(nums):\n    # Return the largest product of a contiguous subarray\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = maxProduct(nums)
    print(result)""",
        "function maxProduct(nums) {\n    // Return largest product\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = maxProduct(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Valid Palindrome": (
        "def isPalindrome(s):\n    # Return True if s is a palindrome (ignore non-alphanumeric, case)\n    pass",
        """if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip()
    result = isPalindrome(s)
    print('true' if result else 'false')""",
        "function isPalindrome(s) {\n    // Return true if palindrome\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const result = isPalindrome(line);
    console.log(result ? 'true' : 'false');
    rl.close();
});""",
    ),
    "3Sum": (
        "def threeSum(nums):\n    # Return list of unique triplets [a,b,c] that sum to 0. Format: list of lists.\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = threeSum(nums)
    # Output: one triplet per line, space-separated
    for row in result:
        print(' '.join(map(str, row)))""",
        "function threeSum(nums) {\n    // Return array of triplets (each triplet is array of 3 numbers)\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = threeSum(nums);
    console.log(result.map(r => r.join(' ')).join('\\n'));
    rl.close();
});""",
    ),
    "Container With Most Water": (
        "def maxArea(height):\n    # Return max area of water container between two lines\n    pass",
        """if __name__ == "__main__":
    import sys
    height = list(map(int, sys.stdin.read().strip().split()))
    result = maxArea(height)
    print(result)""",
        "function maxArea(height) {\n    // Return max area\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const height = line.split(' ').map(Number);
    const result = maxArea(height);
    console.log(result);
    rl.close();
});""",
    ),
    "Longest Substring Without Repeating Characters": (
        "def lengthOfLongestSubstring(s):\n    # Return length of longest substring without repeating characters\n    pass",
        """if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip()
    result = lengthOfLongestSubstring(s)
    print(result)""",
        "function lengthOfLongestSubstring(s) {\n    // Return length\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const result = lengthOfLongestSubstring(line);
    console.log(result);
    rl.close();
});""",
    ),
    "Longest Palindromic Substring": (
        "def longestPalindrome(s):\n    # Return the longest palindromic substring in s\n    pass",
        """if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip()
    result = longestPalindrome(s)
    print(result)""",
        "function longestPalindrome(s) {\n    // Return longest palindromic substring\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const result = longestPalindrome(line);
    console.log(result);
    rl.close();
});""",
    ),
    "Climbing Stairs": (
        "def climbStairs(n):\n    # Return number of distinct ways to climb to the top (1 or 2 steps)\n    pass",
        """if __name__ == "__main__":
    import sys
    n = int(sys.stdin.read().strip())
    result = climbStairs(n)
    print(result)""",
        "function climbStairs(n) {\n    // Return number of ways\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const n = parseInt(line);
    const result = climbStairs(n);
    console.log(result);
    rl.close();
});""",
    ),
    "House Robber": (
        "def rob(nums):\n    # Return max money without robbing two adjacent houses\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = rob(nums)
    print(result)""",
        "function rob(nums) {\n    // Return max money\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = rob(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Group Anagrams": (
        "def groupAnagrams(strs):\n    # Return list of groups (each group is list of anagram strings). Output: comma-sep per group, groups newline-sep.\n    pass",
        """if __name__ == "__main__":
    import sys
    strs = sys.stdin.read().strip().split()
    result = groupAnagrams(strs)
    print('\\n'.join([','.join(g) for g in result]))""",
        "function groupAnagrams(strs) {\n    // Return array of groups (each group is array of strings)\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const strs = line.split(' ');
    const result = groupAnagrams(strs);
    console.log(result.map(g => g.join(',')).join('\\n'));
    rl.close();
});""",
    ),
    "Single Number": (
        "def singleNumber(nums):\n    # Return the single number that appears once (others appear twice). O(1) space.\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = singleNumber(nums)
    print(result)""",
        "function singleNumber(nums) {\n    // Return the single number\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = singleNumber(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Number of 1 Bits": (
        "def hammingWeight(n):\n    # Return number of 1 bits in n (positive integer)\n    pass",
        """if __name__ == "__main__":
    import sys
    n = int(sys.stdin.read().strip())
    result = hammingWeight(n)
    print(result)""",
        "function hammingWeight(n) {\n    // Return number of 1 bits\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const n = parseInt(line);
    const result = hammingWeight(n);
    console.log(result);
    rl.close();
});""",
    ),
    "Reverse Bits": (
        "def reverseBits(n):\n    # Reverse bits of 32-bit unsigned integer. Input as decimal.\n    pass",
        """if __name__ == "__main__":
    import sys
    n = int(sys.stdin.read().strip())
    result = reverseBits(n)
    print(result)""",
        "function reverseBits(n) {\n    // Reverse bits of 32-bit unsigned\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const n = parseInt(line);
    const result = reverseBits(n);
    console.log(result);
    rl.close();
});""",
    ),
    "Missing Number": (
        "def missingNumber(nums):\n    # Return the only number in [0, n] missing from nums\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = missingNumber(nums)
    print(result)""",
        "function missingNumber(nums) {\n    // Return missing number\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = missingNumber(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Pascal's Triangle": (
        "def generate(numRows):\n    # Return first numRows of Pascal's triangle. Each row is list of ints.\n    pass",
        """if __name__ == "__main__":
    import sys
    numRows = int(sys.stdin.read().strip())
    result = generate(numRows)
    for row in result:
        print(' '.join(map(str, row)))""",
        "function generate(numRows) {\n    // Return array of rows\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const numRows = parseInt(line);
    const result = generate(numRows);
    console.log(result.map(r => r.join(' ')).join('\\n'));
    rl.close();
});""",
    ),
    "Remove Duplicates from Sorted Array": (
        "def removeDuplicates(nums):\n    # In-place remove duplicates, return count of unique elements (first k elements are result)\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    k = removeDuplicates(nums)
    print(k)""",
        "function removeDuplicates(nums) {\n    // In-place, return k\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const k = removeDuplicates(nums);
    console.log(k);
    rl.close();
});""",
    ),
    "Sort Colors": (
        "def sortColors(nums):\n    # Sort in-place (0, 1, 2). No return.\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    sortColors(nums)
    print(' '.join(map(str, nums)))""",
        "function sortColors(nums) {\n    // Sort in-place\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    sortColors(nums);
    console.log(nums.join(' '));
    rl.close();
});""",
    ),
    "Search in Rotated Sorted Array": (
        "def search(nums, target):\n    # Return index of target in rotated sorted array, or -1\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, lines[0].split()))
    target = int(lines[1])
    result = search(nums, target)
    print(result)""",
        "function search(nums, target) {\n    // Return index or -1\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = search(nums, target);
    console.log(result);
});""",
    ),
    "Find Minimum in Rotated Sorted Array": (
        "def findMin(nums):\n    # Return minimum element in rotated sorted array. O(log n).\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = findMin(nums)
    print(result)""",
        "function findMin(nums) {\n    // Return minimum\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = findMin(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Binary Search": (
        "def search(nums, target):\n    # Return index of target in sorted nums, or -1\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, lines[0].split()))
    target = int(lines[1])
    result = search(nums, target)
    print(result)""",
        "function search(nums, target) {\n    // Return index or -1\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = search(nums, target);
    console.log(result);
});""",
    ),
    "First Bad Version": (
        "def firstBadVersion(n):\n    # Given n versions, return first bad. Assume isBadVersion(version) is available.\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    n = int(lines[0])
    first_bad = int(lines[1])
    def isBadVersion(v): return v >= first_bad
    result = firstBadVersion(n)
    print(result)""",
        "function firstBadVersion(n) {\n    // isBadVersion provided\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const n = parseInt(lines[0]);
    const firstBad = parseInt(lines[1]);
    const isBadVersion = (v) => v >= firstBad;
    const result = firstBadVersion(n);
    console.log(result);
});""",
    ),
    "Search Insert Position": (
        "def searchInsert(nums, target):\n    # Return index where target would be inserted (or exists)\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, lines[0].split()))
    target = int(lines[1])
    result = searchInsert(nums, target)
    print(result)""",
        "function searchInsert(nums, target) {\n    // Return index\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = searchInsert(nums, target);
    console.log(result);
});""",
    ),
    "Squares of a Sorted Array": (
        "def sortedSquares(nums):\n    # Return array of squares sorted in non-decreasing order\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = sortedSquares(nums)
    print(' '.join(map(str, result)))""",
        "function sortedSquares(nums) {\n    // Return sorted squares\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = sortedSquares(nums);
    console.log(result.join(' '));
    rl.close();
});""",
    ),
    "Rotate Array": (
        "def rotate(nums, k):\n    # Rotate nums to the right by k steps in-place\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, lines[0].split()))
    k = int(lines[1])
    rotate(nums, k)
    print(' '.join(map(str, nums)))""",
        "function rotate(nums, k) {\n    // Rotate in-place\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const k = parseInt(lines[1]);
    rotate(nums, k);
    console.log(nums.join(' '));
});""",
    ),
    "Move Zeroes": (
        "def moveZeroes(nums):\n    # Move all 0's to the end in-place\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    moveZeroes(nums)
    print(' '.join(map(str, nums)))""",
        "function moveZeroes(nums) {\n    // Move zeroes in-place\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    moveZeroes(nums);
    console.log(nums.join(' '));
    rl.close();
});""",
    ),
    "Two Sum II - Input Array Is Sorted": (
        "def twoSum(numbers, target):\n    # 1-indexed sorted array. Return [index1, index2] (as two numbers)\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    numbers = list(map(int, lines[0].split()))
    target = int(lines[1])
    result = twoSum(numbers, target)
    print(' '.join(map(str, result)))""",
        "function twoSum(numbers, target) {\n    // Return [index1, index2] 1-indexed\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const numbers = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = twoSum(numbers, target);
    console.log(result.join(' '));
});""",
    ),
    "Reverse Words in a String": (
        "def reverseWords(s):\n    # Reverse order of words. Return single-space separated, no leading/trailing.\n    pass",
        """if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip()
    result = reverseWords(s)
    print(result)""",
        "function reverseWords(s) {\n    // Return reversed words\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const result = reverseWords(line);
    console.log(result);
    rl.close();
});""",
    ),
    "Longest Consecutive Sequence": (
        "def longestConsecutive(nums):\n    # Return length of longest consecutive elements sequence. O(n).\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = longestConsecutive(nums)
    print(result)""",
        "function longestConsecutive(nums) {\n    // Return length\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = longestConsecutive(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Isomorphic Strings": (
        "def isIsomorphic(s, t):\n    # Return True if s and t are isomorphic\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    s, t = lines[0], lines[1]
    result = isIsomorphic(s, t)
    print('true' if result else 'false')""",
        "function isIsomorphic(s, t) {\n    // Return true/false\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const [s, t] = lines;
    const result = isIsomorphic(s, t);
    console.log(result ? 'true' : 'false');
});""",
    ),
    "Happy Number": (
        "def isHappy(n):\n    # Return True if n is a happy number\n    pass",
        """if __name__ == "__main__":
    import sys
    n = int(sys.stdin.read().strip())
    result = isHappy(n)
    print('true' if result else 'false')""",
        "function isHappy(n) {\n    // Return true/false\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const n = parseInt(line);
    const result = isHappy(n);
    console.log(result ? 'true' : 'false');
    rl.close();
});""",
    ),
    "Count Primes": (
        "def countPrimes(n):\n    # Return number of primes strictly less than n\n    pass",
        """if __name__ == "__main__":
    import sys
    n = int(sys.stdin.read().strip())
    result = countPrimes(n)
    print(result)""",
        "function countPrimes(n) {\n    // Return count\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const n = parseInt(line);
    const result = countPrimes(n);
    console.log(result);
    rl.close();
});""",
    ),
    "Plus One": (
        "def plusOne(digits):\n    # digits is array (most significant first). Return array for number + 1\n    pass",
        """if __name__ == "__main__":
    import sys
    digits = list(map(int, sys.stdin.read().strip().split()))
    result = plusOne(digits)
    print(' '.join(map(str, result)))""",
        "function plusOne(digits) {\n    // Return array\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const digits = line.split(' ').map(Number);
    const result = plusOne(digits);
    console.log(result.join(' '));
    rl.close();
});""",
    ),
    "Sqrt(x)": (
        "def mySqrt(x):\n    # Return integer square root (truncated)\n    pass",
        """if __name__ == "__main__":
    import sys
    x = int(sys.stdin.read().strip())
    result = mySqrt(x)
    print(result)""",
        "function mySqrt(x) {\n    // Return integer sqrt\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const x = parseInt(line);
    const result = mySqrt(x);
    console.log(result);
    rl.close();
});""",
    ),
    "Merge Intervals": (
        "def merge(intervals):\n    # intervals: list of [start, end]. Merge overlapping. Input: pairs space-sep e.g. 1 3 2 6\n    pass",
        """if __name__ == "__main__":
    import sys
    arr = list(map(int, sys.stdin.read().strip().split()))
    intervals = [arr[i:i+2] for i in range(0, len(arr), 2)]
    result = merge(intervals)
    out = []
    for a, b in result:
        out.extend([a, b])
    print(' '.join(map(str, out)))""",
        "function merge(intervals) {\n    // Return merged intervals\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const arr = line.split(' ').map(Number);
    const intervals = [];
    for (let i = 0; i < arr.length; i += 2) intervals.push([arr[i], arr[i+1]]);
    const result = merge(intervals);
    const flat = result.flat();
    console.log(flat.join(' '));
    rl.close();
});""",
    ),
    "Insert Interval": (
        "def insert(intervals, newInterval):\n    # Insert newInterval and merge. Input: intervals then new on next line\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    arr1 = list(map(int, lines[0].split()))
    arr2 = list(map(int, lines[1].split()))
    intervals = [arr1[i:i+2] for i in range(0, len(arr1), 2)]
    newInterval = arr2
    result = insert(intervals, newInterval)
    out = []
    for a, b in result:
        out.extend([a, b])
    print(' '.join(map(str, out)))""",
        "function insert(intervals, newInterval) {\n    // Return intervals\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const arr1 = lines[0].split(' ').map(Number);
    const arr2 = lines[1].split(' ').map(Number);
    const intervals = [];
    for (let i = 0; i < arr1.length; i += 2) intervals.push([arr1[i], arr1[i+1]]);
    const result = insert(intervals, arr2);
    console.log(result.flat().join(' '));
});""",
    ),
    "Jump Game": (
        "def canJump(nums):\n    # Return True if you can reach the last index\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = canJump(nums)
    print('true' if result else 'false')""",
        "function canJump(nums) {\n    // Return true/false\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = canJump(nums);
    console.log(result ? 'true' : 'false');
    rl.close();
});""",
    ),
    "Jump Game II": (
        "def jump(nums):\n    # Return minimum number of jumps to reach last index\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = jump(nums)
    print(result)""",
        "function jump(nums) {\n    // Return min jumps\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = jump(nums);
    console.log(result);
    rl.close();
});""",
    ),
    "Unique Paths": (
        "def uniquePaths(m, n):\n    # Return number of unique paths from top-left to bottom-right (m x n grid)\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    m, n = int(lines[0]), int(lines[1])
    result = uniquePaths(m, n)
    print(result)""",
        "function uniquePaths(m, n) {\n    // Return count\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const m = parseInt(lines[0]);
    const n = parseInt(lines[1]);
    const result = uniquePaths(m, n);
    console.log(result);
});""",
    ),
    "Minimum Path Sum": (
        "def minPathSum(grid):\n    # Return minimum sum path from top-left to bottom-right\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    m, n = int(lines[0]), int(lines[1])
    grid = [list(map(int, lines[i+2].split())) for i in range(m)]
    result = minPathSum(grid)
    print(result)""",
        "function minPathSum(grid) {\n    // Return min sum\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const m = parseInt(lines[0]);
    const n = parseInt(lines[1]);
    const grid = lines.slice(2, 2+m).map(l => l.split(' ').map(Number));
    const result = minPathSum(grid);
    console.log(result);
});""",
    ),
    "Coin Change": (
        "def coinChange(coins, amount):\n    # Return fewest number of coins for amount, -1 if impossible\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    coins = list(map(int, lines[0].split()))
    amount = int(lines[1])
    result = coinChange(coins, amount)
    print(result)""",
        "function coinChange(coins, amount) {\n    // Return fewest coins or -1\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const coins = lines[0].split(' ').map(Number);
    const amount = parseInt(lines[1]);
    const result = coinChange(coins, amount);
    console.log(result);
});""",
    ),
    "Word Break": (
        "def wordBreak(s, wordDict):\n    # Return True if s can be segmented into words from wordDict\n    pass",
        """if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    s = lines[0]
    wordDict = lines[1].split()
    result = wordBreak(s, wordDict)
    print('true' if result else 'false')""",
        "function wordBreak(s, wordDict) {\n    // Return true/false\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const s = lines[0];
    const wordDict = lines[1].split(' ');
    const result = wordBreak(s, wordDict);
    console.log(result ? 'true' : 'false');
});""",
    ),
    "Maximum Subarray": (
        "def maxSubArray(nums):\n    # Return the largest sum of a contiguous subarray\n    pass",
        """if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = maxSubArray(nums)
    print(result)""",
        "function maxSubArray(nums) {\n    // Return max sum\n}",
        """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = maxSubArray(nums);
    console.log(result);
    rl.close();
});""",
    ),
}


# Generic fallback for problems not in STARTERS (LeetCode-style: user implements only the function; driver handles I/O)
DEFAULT_STARTER_PY = "def solve(data):\n    # Implement only the solution. Input is passed by the system; return result to print.\n    pass"
DEFAULT_DRIVER_PY = """if __name__ == "__main__":
    import sys
    data = sys.stdin.read().strip()
    result = solve(data)
    print(result)"""
DEFAULT_STARTER_JS = "function solve(data) {\n    // Implement only the solution. Input is passed by the system; return result to print.\n}"
DEFAULT_DRIVER_JS = """const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const data = lines.join('\\n');
    const result = solve(data);
    console.log(result);
});"""


def get_starters_for_problem(title: str):
    """Return dict with starter_code_python, driver_code_python, starter_code_javascript, driver_code_javascript."""
    if title in STARTERS:
        t = STARTERS[title]
        return {
            "starter_code_python": t[0],
            "driver_code_python": t[1],
            "starter_code_javascript": t[2],
            "driver_code_javascript": t[3],
        }
    return {
        "starter_code_python": DEFAULT_STARTER_PY,
        "driver_code_python": DEFAULT_DRIVER_PY,
        "starter_code_javascript": DEFAULT_STARTER_JS,
        "driver_code_javascript": DEFAULT_DRIVER_JS,
    }
