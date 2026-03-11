"""
Central registry of function metadata per problem title.
Single source of truth for function name, return type, and parameters.
Use _reg_signature when exact per-language types are required (e.g. nested arrays).
"""
from typing import Dict, List, Optional, Any
from models import ProblemFunctionMetadata, ProblemFunctionParam

# Title -> (ProblemFunctionMetadata, input_spec for driver)
# input_spec: list of {"name": str, "type": str} in stdin order
REGISTRY: Dict[str, tuple] = {}

def _reg(
    title: str,
    function_name: str,
    return_type: str,
    parameters: List[dict],
    input_spec: Optional[List[dict]] = None,
) -> None:
    params = [ProblemFunctionParam(name=p["name"], type=p.get("type", "")) for p in parameters]
    meta = ProblemFunctionMetadata(function_name=function_name, return_type=return_type, parameters=params)
    spec = input_spec if input_spec is not None else [{"name": p["name"], "type": p.get("type", "str")} for p in parameters]
    REGISTRY[title] = (meta, spec)


def _reg_signature(
    title: str,
    function_name: str,
    return_type_by_language: Dict[str, str],
    parameters: List[dict],
    input_spec: Optional[List[dict]] = None,
) -> None:
    """Register problem with exact per-language types (required for nested return/params e.g. Insert Interval)."""
    params = [
        ProblemFunctionParam(
            name=p["name"],
            type=p.get("type", ""),
            type_by_language=p.get("type_by_language"),
        )
        for p in parameters
    ]
    canonical_return = list(return_type_by_language.values())[0] if return_type_by_language else ""
    meta = ProblemFunctionMetadata(
        function_name=function_name,
        return_type=canonical_return,
        return_type_by_language=return_type_by_language,
        parameters=params,
    )
    spec = input_spec if input_spec is not None else [{"name": p["name"], "type": p.get("type", "str")} for p in parameters]
    REGISTRY[title] = (meta, spec)

# Two Sum (indices 0-based, return [i, j])
_reg(
    "Two Sum",
    "twoSum",
    "int[]",
    [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
    [{"name": "nums", "type": "int[]"}, {"name": "target", "type": "int"}],
)
# Two Sum II - Input Array Is Sorted (1-indexed return)
_reg(
    "Two Sum II - Input Array Is Sorted",
    "twoSum",
    "int[]",
    [{"name": "numbers", "type": "int[]"}, {"name": "target", "type": "int"}],
    [{"name": "numbers", "type": "int[]"}, {"name": "target", "type": "int"}],
)
_reg("Contains Duplicate", "containsDuplicate", "boolean", [{"name": "nums", "type": "int[]"}])
_reg("Best Time to Buy and Sell Stock", "maxProfit", "int", [{"name": "prices", "type": "int[]"}])
_reg("Valid Anagram", "isAnagram", "boolean", [{"name": "s", "type": "str"}, {"name": "t", "type": "str"}], [{"name": "s", "type": "str"}, {"name": "t", "type": "str"}])
_reg("Product of Array Except Self", "productExceptSelf", "int[]", [{"name": "nums", "type": "int[]"}])
_reg("Maximum Product Subarray", "maxProduct", "int", [{"name": "nums", "type": "int[]"}])
_reg("Valid Palindrome", "isPalindrome", "boolean", [{"name": "s", "type": "str"}])
# 3Sum: returns list of triplets; type varies by language
_reg_signature(
    "3Sum",
    "threeSum",
    return_type_by_language={
        "python": "List[List[int]]",
        "javascript": "number[][]",
        "java": "int[][]",
        "cpp": "vector<vector<int>>",
        "c": "int**",
        "go": "[][]int",
        "csharp": "int[][]",
        "typescript": "number[][]",
    },
    parameters=[
        {
            "name": "nums",
            "type": "int[]",
            "type_by_language": {
                "python": "List[int]",
                "javascript": "number[]",
                "java": "int[]",
                "cpp": "vector<int>&",
                "c": "int*",
                "go": "[]int",
                "csharp": "int[]",
                "typescript": "number[]",
            },
        },
    ],
    input_spec=[{"name": "nums", "type": "int[]"}],
)
_reg("Maximum Subarray", "maxSubArray", "int", [{"name": "nums", "type": "int[]"}])
_reg(
    "Continuous Subarray Sum",
    "checkSubarraySum",
    "boolean",
    [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
    [{"name": "nums", "type": "int[]"}, {"name": "k", "type": "int"}],
)
_reg("Merge Two Sorted Lists", "mergeTwoLists", "int[]", [{"name": "l1", "type": "int[]"}, {"name": "l2", "type": "int[]"}], [{"name": "l1", "type": "int[]"}, {"name": "l2", "type": "int[]"}])
_reg("Reverse String", "reverseString", "void", [{"name": "s", "type": "List[str]"}], [{"name": "s", "type": "str"}])  # in-place
_reg("Valid Parentheses", "isValid", "boolean", [{"name": "s", "type": "str"}])

# Insert Interval: return and params are list of intervals (nested arrays) — exact types per language
_reg_signature(
    "Insert Interval",
    "insert",
    return_type_by_language={
        "python": "List[List[int]]",
        "javascript": "number[][]",
        "java": "int[][]",
        "cpp": "vector<vector<int>>",
        "c": "int**",
        "go": "[][]int",
        "csharp": "int[][]",
        "typescript": "number[][]",
    },
    parameters=[
        {
            "name": "intervals",
            "type": "List[List[int]]",
            "type_by_language": {
                "python": "List[List[int]]",
                "javascript": "number[][]",
                "java": "int[][]",
                "cpp": "vector<vector<int>>&",
                "c": "int**",
                "go": "[][]int",
                "csharp": "int[][]",
                "typescript": "number[][]",
            },
        },
        {
            "name": "newInterval",
            "type": "List[int]",
            "type_by_language": {
                "python": "List[int]",
                "javascript": "number[]",
                "java": "int[]",
                "cpp": "vector<int>&",
                "c": "int*",
                "go": "[]int",
                "csharp": "int[]",
                "typescript": "number[]",
            },
        },
    ],
    input_spec=[{"name": "intervals", "type": "List[List[int]]"}, {"name": "newInterval", "type": "List[int]"}],
)

# Merge Intervals: same nested return/param shape
_reg_signature(
    "Merge Intervals",
    "merge",
    return_type_by_language={
        "python": "List[List[int]]",
        "javascript": "number[][]",
        "java": "int[][]",
        "cpp": "vector<vector<int>>",
        "c": "int**",
        "go": "[][]int",
        "csharp": "int[][]",
        "typescript": "number[][]",
    },
    parameters=[
        {
            "name": "intervals",
            "type": "List[List[int]]",
            "type_by_language": {
                "python": "List[List[int]]",
                "javascript": "number[][]",
                "java": "int[][]",
                "cpp": "vector<vector<int>>&",
                "c": "int**",
                "go": "[][]int",
                "csharp": "int[][]",
                "typescript": "number[][]",
            },
        },
    ],
    input_spec=[{"name": "intervals", "type": "List[List[int]]"}],
)


def get_metadata(title: str) -> Optional[tuple]:
    """Return (ProblemFunctionMetadata, input_spec) if registered, else None."""
    return REGISTRY.get(title)
