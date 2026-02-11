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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]


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
                TestCase(input="3 3\n6", expected_output="0 1", is_hidden=False),
            ],
            "starter_code_python": """def twoSum(nums, target):
    # Write your code here
    pass

if __name__ == "__main__":
    import sys
    input_data = sys.stdin.read().strip().split('\\n')
    nums = list(map(int, input_data[0].split()))
    target = int(input_data[1])
    result = twoSum(nums, target)
    print(' '.join(map(str, result)))""",
            "starter_code_javascript": """function twoSum(nums, target) {
    // Write your code here
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const nums = lines[0].split(' ').map(Number);
    const target = parseInt(lines[1]);
    const result = twoSum(nums, target);
    console.log(result.join(' '));
});"""
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
                TestCase(input="H a n n a h", expected_output="h a n n a H", is_hidden=False),
            ],
            "starter_code_python": """def reverseString(s):
    # Write your code here
    pass

if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip().split()
    reverseString(s)
    print(' '.join(s))""",
            "starter_code_javascript": """function reverseString(s) {
    // Write your code here
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const s = line.split(' ');
    reverseString(s);
    console.log(s.join(' '));
    rl.close();
});"""
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
            "starter_code_python": """def isValid(s):
    # Write your code here
    pass

if __name__ == "__main__":
    import sys
    s = sys.stdin.read().strip()
    result = isValid(s)
    print('true' if result else 'false')""",
            "starter_code_javascript": """function isValid(s) {
    // Write your code here
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const result = isValid(line);
    console.log(result ? 'true' : 'false');
    rl.close();
});"""
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
                TestCase(input="\n0", expected_output="0", is_hidden=False),
            ],
            "starter_code_python": """def mergeTwoLists(l1, l2):
    # Write your code here
    # For this problem, work with lists instead of linked list nodes
    pass

if __name__ == "__main__":
    import sys
    lines = sys.stdin.read().strip().split('\\n')
    l1 = list(map(int, lines[0].split())) if lines[0] else []
    l2 = list(map(int, lines[1].split())) if lines[1] else []
    result = mergeTwoLists(l1, l2)
    print(' '.join(map(str, result)) if result else '')""",
            "starter_code_javascript": """function mergeTwoLists(l1, l2) {
    // Write your code here
    // For this problem, work with arrays instead of linked list nodes
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
const lines = [];
rl.on('line', (line) => lines.push(line));
rl.on('close', () => {
    const l1 = lines[0] ? lines[0].split(' ').map(Number) : [];
    const l2 = lines[1] ? lines[1].split(' ').map(Number) : [];
    const result = mergeTwoLists(l1, l2);
    console.log(result.length ? result.join(' ') : '');
});"""
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
                TestCase(input="5 4 -1 7 8", expected_output="23", is_hidden=False),
            ],
            "starter_code_python": """def maxSubArray(nums):
    # Write your code here
    pass

if __name__ == "__main__":
    import sys
    nums = list(map(int, sys.stdin.read().strip().split()))
    result = maxSubArray(nums)
    print(result)""",
            "starter_code_javascript": """function maxSubArray(nums) {
    // Write your code here
}

const readline = require('readline');
const rl = readline.createInterface({ input: process.stdin });
rl.on('line', (line) => {
    const nums = line.split(' ').map(Number);
    const result = maxSubArray(nums);
    console.log(result);
    rl.close();
});"""
        }
    ]
    
    # Insert problems
    for problem_data in problems:
        existing = await db.problems.find_one({"title": problem_data["title"]})
        if not existing:
            problem = Problem(**problem_data, created_by=admin_user.id)
            problem_dict = problem.model_dump()
            problem_dict['created_at'] = problem_dict['created_at'].isoformat()
            await db.problems.insert_one(problem_dict)
            print(f"✓ Created problem: {problem.title}")
        else:
            print(f"✓ Problem already exists: {problem_data['title']}")
    
    print("\n✅ Database seeding completed!")
    print("\nTest accounts:")
    print("  Admin: admin@ifelse.com / admin123")
    print("  Demo:  demo@ifelse.com / demo123")


if __name__ == "__main__":
    asyncio.run(seed_database())
