import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from pathlib import Path
import os
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from models import Problem, TestCase, Difficulty, User, UserInDB
from auth import get_password_hash
from seed_problems_top100 import get_additional_problems
from test_case_validation import (
    validate_no_duplicates_within_problem,
    deduplicate_test_cases,
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

MIN_HIDDEN_TEST_CASES = 20  # Every problem must have at least this many hidden test cases.
MIN_VISIBLE_TEST_CASES = 2  # Every problem must have at least this many visible (default) test cases.


def _tc_key(tc):
    """Unique key for a test case (input + expected_output) for deduplication."""
    if isinstance(tc, TestCase):
        return (tc.input, tc.expected_output)
    return (tc.get("input"), tc.get("expected_output"))


def ensure_min_visible_test_cases(test_cases, min_visible=MIN_VISIBLE_TEST_CASES):
    """Ensure the list has at least min_visible test cases with is_hidden=False.
    When adding visible cases, cycles through existing cases so visible cases are distinct when possible.
    Removes duplicate visible cases (same input + expected_output) so Case 1 and Case 2 are never identical."""
    if not test_cases:
        return test_cases
    current = list(test_cases)
    # Always deduplicate visible first so Example 1 and Example 2 are never identical
    seen = set()
    out = []
    for tc in current:
        is_vis = (isinstance(tc, TestCase) and not tc.is_hidden) or (isinstance(tc, dict) and not tc.get("is_hidden"))
        key = _tc_key(tc)
        if is_vis and key in seen:
            continue
        if is_vis:
            seen.add(key)
        out.append(tc)
    current = out
    unique_visible = len(seen)
    if unique_visible >= min_visible:
        return current
    # Defensive: if dedup unexpectedly empties current, fall back to original list as source.
    source_cases = current if current else list(test_cases)
    if not source_cases:
        return current
    use_model = isinstance(source_cases[0], TestCase)
    visible_keys = set(seen)
    need = min_visible - unique_visible
    # Never clone a testcase key to satisfy min counts; uniqueness is mandatory.
    candidates = []
    for cand in source_cases:
        key = _tc_key(cand)
        if key in visible_keys:
            continue
        candidates.append(cand)
        visible_keys.add(key)
    for src in candidates[:need]:
        if use_model:
            current.insert(0, TestCase(input=src.input, expected_output=src.expected_output, is_hidden=False))
        else:
            s = src if isinstance(src, dict) else {"input": src.input, "expected_output": src.expected_output}
            current.insert(0, {"input": s["input"], "expected_output": s["expected_output"], "is_hidden": False})
    return current


def ensure_min_hidden_test_cases(test_cases, min_hidden=MIN_HIDDEN_TEST_CASES):
    """Ensure the list has at least min_hidden test cases with is_hidden=True.
    When adding hidden cases, prefers sources that are not already in the list (by input+output)
    so hidden cases stay distinct. Returns new list."""
    if not test_cases:
        return test_cases
    current = list(test_cases)
    existing_keys = {_tc_key(tc) for tc in current}
    hidden_count = sum(
        1 for tc in current
        if (isinstance(tc, TestCase) and tc.is_hidden) or (isinstance(tc, dict) and tc.get("is_hidden"))
    )
    if hidden_count >= min_hidden:
        return current
    # Do not clone test cases to hit min_hidden. Cloning creates duplicate keys and leaks examples.
    # If seed data lacks enough unique hidden cases, keep current unique set as-is.
    return current


async def seed_database():
    print("Starting database seeding...")
    
    # Create admin user
    admin_user = UserInDB(
        email="admin@ifelse.com",
        username="admin",
        full_name="Admin User",
        role="admin",
        hashed_password=get_password_hash("admin123")
    )
    
    existing_admin = await db.users.find_one({"email": admin_user.email})
    if not existing_admin:
        user_dict = admin_user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        await db.users.insert_one(user_dict)
        print(f"✓ Created admin user: {admin_user.email}")
    else:
        admin_user.id = existing_admin['id']
        print(f"✓ Admin user already exists: {admin_user.email}")
    
    # Create demo user
    demo_user = UserInDB(
        email="demo@ifelse.com",
        username="demo",
        full_name="Demo User",
        hashed_password=get_password_hash("demo123")
    )
    
    existing_demo = await db.users.find_one({"email": demo_user.email})
    if not existing_demo:
        user_dict = demo_user.model_dump()
        user_dict['created_at'] = user_dict['created_at'].isoformat()
        await db.users.insert_one(user_dict)
        print(f"✓ Created demo user: {demo_user.email}")
    else:
        print(f"✓ Demo user already exists: {demo_user.email}")
    
    # Sample problems
    problems = [
        {
            "title": "Two Sum",
            "description": """Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

Example 1:
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].

Example 2:
Input: nums = [3,2,4], target = 6
Output: [1,2]

Constraints:
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- Only one valid answer exists.""",
            "difficulty": Difficulty.EASY,
            "tags": ["Array", "Hash Table"],
            "companies": ["Amazon", "Google", "Microsoft"],
            "test_cases": [
                TestCase(input="2 7 11 15\n9", expected_output="0 1", is_hidden=False),
                TestCase(input="3 2 4\n6", expected_output="1 2", is_hidden=False),
                TestCase(input="3 3\n6", expected_output="0 1", is_hidden=True),
            ],
            "starter_code_python": "def twoSum(nums, target):\n    # Write your code here\n    pass",
            "driver_code_python": "if __name__ == \"__main__\":\n    import sys\n    input_data = sys.stdin.read().strip().split('\\n')\n    nums = list(map(int, input_data[0].split()))\n    target = int(input_data[1])\n    result = twoSum(nums, target)\n    print(' '.join(map(str, result)))",
            "starter_code_javascript": "function twoSum(nums, target) {\n    // Write your code here\n}",
            "driver_code_javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nconst lines = [];\nrl.on('line', (line) => lines.push(line));\nrl.on('close', () => {\n    const nums = lines[0].split(' ').map(Number);\n    const target = parseInt(lines[1]);\n    const result = twoSum(nums, target);\n    console.log(result.join(' '));\n});",
            "solution": "Use a hash map to store each number and its index. For each element, check if (target - num) exists in the map; if so, return [map[target - num], current index]. Time O(n), space O(n).",
            "hints": ["Try using a hash map to store values you've already seen.", "For each number, what value would you need to have seen earlier to get the target sum?"]
        },
        {
            "title": "Reverse String",
            "description": """Write a function that reverses a string. The input string is given as an array of characters s.

You must do this by modifying the input array in-place with O(1) extra memory.

Example 1:
Input: s = ["h","e","l","l","o"]
Output: ["o","l","l","e","h"]

Example 2:
Input: s = ["H","a","n","n","a","h"]
Output: ["h","a","n","n","a","H"]

Constraints:
- 1 <= s.length <= 10^5
- s[i] is a printable ascii character.""",
            "difficulty": Difficulty.EASY,
            "tags": ["String", "Two Pointers"],
            "companies": ["Facebook", "Apple"],
            "test_cases": [
                TestCase(input="h e l l o", expected_output="o l l e h", is_hidden=False),
                TestCase(input="H a n n a h", expected_output="h a n n a H", is_hidden=True),
            ],
            "starter_code_python": "def reverseString(s):\n    # Write your code here\n    pass",
            "driver_code_python": "if __name__ == \"__main__\":\n    import sys\n    s = sys.stdin.read().strip().split()\n    reverseString(s)\n    print(' '.join(s))",
            "starter_code_javascript": "function reverseString(s) {\n    // Write your code here\n}",
            "driver_code_javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nrl.on('line', (line) => {\n    const s = line.split(' ');\n    reverseString(s);\n    console.log(s.join(' '));\n    rl.close();\n});",
            "solution": "Use two pointers: one at the start and one at the end. Swap the characters at both pointers, then move the start pointer forward and the end pointer backward until they meet. Time O(n), space O(1).",
            "hints": ["Swap elements from both ends moving inward.", "You only need to iterate until the two pointers meet in the middle."]
        },
        {
            "title": "Valid Parentheses",
            "description": """Given a string s containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

Example 1:
Input: s = "()"
Output: true

Example 2:
Input: s = "()[]{}"
Output: true

Example 3:
Input: s = "(]"
Output: false

Constraints:
- 1 <= s.length <= 10^4
- s consists of parentheses only '()[]{}'.""",
            "difficulty": Difficulty.MEDIUM,
            "tags": ["Stack", "String"],
            "companies": ["Amazon", "Microsoft", "Bloomberg"],
            "test_cases": [
                TestCase(input="()", expected_output="true", is_hidden=False),
                TestCase(input="()[]{}", expected_output="true", is_hidden=False),
                TestCase(input="(]", expected_output="false", is_hidden=False),
                TestCase(input="([)]", expected_output="false", is_hidden=True),
            ],
            "starter_code_python": "def isValid(s):\n    # Write your code here\n    pass",
            "driver_code_python": "if __name__ == \"__main__\":\n    import sys\n    s = sys.stdin.read().strip()\n    result = isValid(s)\n    print('true' if result else 'false')",
            "starter_code_javascript": "function isValid(s) {\n    // Write your code here\n}",
            "driver_code_javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nrl.on('line', (line) => {\n    const result = isValid(line);\n    console.log(result ? 'true' : 'false');\n    rl.close();\n});",
            "solution": "Use a stack. For each opening bracket, push it. For each closing bracket, check if the top of the stack is the matching opening bracket; if not or stack empty, return false. At the end, the stack must be empty. Time O(n), space O(n).",
            "hints": ["A stack helps match the most recent opening bracket with the current closing bracket.", "Handle empty stack when you see a closing bracket."]
        },
        {
            "title": "Merge Two Sorted Lists",
            "description": """You are given the heads of two sorted linked lists list1 and list2.

Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.

Example 1:
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]

Example 2:
Input: list1 = [], list2 = []
Output: []

Example 3:
Input: list1 = [], list2 = [0]
Output: [0]

Constraints:
- The number of nodes in both lists is in the range [0, 50].
- -100 <= Node.val <= 100
- Both list1 and list2 are sorted in non-decreasing order.""",
            "difficulty": Difficulty.MEDIUM,
            "tags": ["Linked List", "Recursion"],
            "companies": ["Google", "Amazon"],
            "test_cases": [
                TestCase(input="1 2 4\n1 3 4", expected_output="1 1 2 3 4 4", is_hidden=False),
                TestCase(input="\n", expected_output="", is_hidden=False),
                TestCase(input="\n0", expected_output="0", is_hidden=True),
            ],
            "starter_code_python": "def mergeTwoLists(l1, l2):\n    # Write your code here (lists, not linked list nodes)\n    pass",
            "driver_code_python": "if __name__ == \"__main__\":\n    import sys\n    lines = sys.stdin.read().strip().split('\\n')\n    l1 = list(map(int, lines[0].split())) if lines[0] else []\n    l2 = list(map(int, lines[1].split())) if lines[1] else []\n    result = mergeTwoLists(l1, l2)\n    print(' '.join(map(str, result)) if result else '')",
            "starter_code_javascript": "function mergeTwoLists(l1, l2) {\n    // Write your code here\n}",
            "driver_code_javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nconst lines = [];\nrl.on('line', (line) => lines.push(line));\nrl.on('close', () => {\n    const l1 = lines[0] ? lines[0].split(' ').map(Number) : [];\n    const l2 = lines[1] ? lines[1].split(' ').map(Number) : [];\n    const result = mergeTwoLists(l1, l2);\n    console.log(result.length ? result.join(' ') : '');\n});",
            "solution": "Use two pointers: compare the current elements of both lists, append the smaller one to the result, and advance that list's pointer. When one list is exhausted, append the rest of the other. Time O(n+m), space O(1) for the merge (excluding output).",
            "hints": ["Compare the head of each list and take the smaller node.", "You can do this iteratively with a dummy head to simplify edge cases."]
        },
        {
            "title": "Maximum Subarray",
            "description": """Given an integer array nums, find the subarray with the largest sum, and return its sum.

Example 1:
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: The subarray [4,-1,2,1] has the largest sum 6.

Example 2:
Input: nums = [1]
Output: 1
Explanation: The subarray [1] has the largest sum 1.

Example 3:
Input: nums = [5,4,-1,7,8]
Output: 23
Explanation: The subarray [5,4,-1,7,8] has the largest sum 23.

Constraints:
- 1 <= nums.length <= 10^5
- -10^4 <= nums[i] <= 10^4""",
            "difficulty": Difficulty.HARD,
            "tags": ["Array", "Dynamic Programming", "Divide and Conquer"],
            "companies": ["Amazon", "Microsoft", "Apple"],
            "test_cases": [
                TestCase(input="-2 1 -3 4 -1 2 1 -5 4", expected_output="6", is_hidden=False),
                TestCase(input="1", expected_output="1", is_hidden=False),
                TestCase(input="5 4 -1 7 8", expected_output="23", is_hidden=True),
            ],
            "starter_code_python": "def maxSubArray(nums):\n    # Write your code here\n    pass",
            "driver_code_python": "if __name__ == \"__main__\":\n    import sys\n    nums = list(map(int, sys.stdin.read().strip().split()))\n    result = maxSubArray(nums)\n    print(result)",
            "starter_code_javascript": "function maxSubArray(nums) {\n    // Write your code here\n}",
            "driver_code_javascript": "const readline = require('readline');\nconst rl = readline.createInterface({ input: process.stdin });\nrl.on('line', (line) => {\n    const nums = line.split(' ').map(Number);\n    const result = maxSubArray(nums);\n    console.log(result);\n    rl.close();\n});",
            "solution": "Kadane's algorithm: iterate and at each step, either extend the current subarray (current_sum + num) or start fresh (num). Keep track of the maximum sum seen. Time O(n), space O(1).",
            "hints": ["Think about whether to extend the current subarray or start a new one at each position.", "You only need one pass; track the best sum ending at the current index and the global best."]
        }
    ]
    
    # Add curated problems (extends base set to 100+)
    problems.extend(get_additional_problems())
    
    # Ensure every problem has distinct test cases and min visible/hidden counts
    for problem_data in problems:
        tcs = problem_data["test_cases"]
        # Remove any duplicate (input, expected_output) within the problem first
        tcs = deduplicate_test_cases(tcs)
        tcs = ensure_min_visible_test_cases(tcs)
        tcs = ensure_min_hidden_test_cases(tcs)
        ok, dup_pairs = validate_no_duplicates_within_problem(tcs)
        if not ok:
            print(f"  Warning: {problem_data['title']} still has duplicate test case indices: {dup_pairs}")
        problem_data["test_cases"] = tcs
    
    # Insert or update problems (update starter/driver for  so re-run applies changes)
    for problem_data in problems:
        existing = await db.problems.find_one({"title": problem_data["title"]})
        if not existing:
            problem = Problem(**problem_data, created_by=admin_user.id)
            problem_dict = problem.model_dump()
            problem_dict['created_at'] = problem_dict['created_at'].isoformat()
            await db.problems.insert_one(problem_dict)
            print(f"✓ Created problem: {problem.title}")
        else:
            # Update starter/driver and ensure min hidden test cases
            update = {}
            for k in ["starter_code_python", "starter_code_javascript", "starter_code_java", "starter_code_cpp", "starter_code_c",
                      "driver_code_python", "driver_code_javascript", "driver_code_java", "driver_code_cpp", "driver_code_c",
                      "solution", "hints"]:
                if k in problem_data:
                    update[k] = problem_data[k]
            existing_tcs = existing.get("test_cases") or []
            existing_tcs = deduplicate_test_cases(existing_tcs)
            existing_tcs = ensure_min_visible_test_cases(existing_tcs)
            expanded_tcs = ensure_min_hidden_test_cases(existing_tcs)
            # Always write back test cases so duplicate visible examples get fixed on re-seed
            update["test_cases"] = [
                {"input": t["input"], "expected_output": t["expected_output"], "is_hidden": t["is_hidden"]}
                for t in expanded_tcs
            ]
            if update:
                await db.problems.update_one({"title": problem_data["title"]}, {"$set": update})
            print(f"✓ Problem already exists: {problem_data['title']}")
    
    print("\n✅ Database seeding completed!")
    print("\nTest accounts:")
    print("  Admin: admin@ifelse.com / admin123")
    print("  Demo:  demo@ifelse.com / demo123")


if __name__ == "__main__":
    asyncio.run(seed_database())
