"""
Test case integrity: normalize, hash, validate uniqueness within and across problems.
Enforces: no duplicate (input, expected_output) within a problem; optional global uniqueness.
Global rules: minimum 2 visible, minimum 20 hidden test cases per problem.
"""
import hashlib
import re
from typing import List, Tuple, Optional, Set
from models import TestCase

# Mandatory minimums for publish (global rules)
MIN_VISIBLE_TEST_CASES = 2
MIN_HIDDEN_TEST_CASES = 20


def normalize_tc_input_output(input_val: str, expected_output: str) -> Tuple[str, str]:
    """Normalize for comparison: strip, collapse whitespace/newlines to single space."""
    def norm(s: str) -> str:
        if s is None:
            return ""
        s = str(s).strip()
        # Collapse any run of whitespace (including newlines) to a single space
        s = re.sub(r"\s+", " ", s)
        return s
    return norm(input_val), norm(expected_output)


def tc_hash(input_val: str, expected_output: str) -> str:
    """SHA256 hash of normalized (input | expected_output) for duplicate detection."""
    inp_n, out_n = normalize_tc_input_output(input_val or "", expected_output or "")
    payload = f"{inp_n}|{out_n}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _tc_key(tc) -> Tuple[str, str]:
    """Get (input, expected_output) from TestCase or dict."""
    if isinstance(tc, TestCase):
        return (tc.input or "", tc.expected_output or "")
    return (tc.get("input") or "", tc.get("expected_output") or "")


def validate_no_duplicates_within_problem(
    test_cases: List,
) -> Tuple[bool, List[Tuple[int, int]]]:
    """
    Check that no two test cases in the list have the same (normalized input, expected_output).
    Returns (True, []) if valid; (False, [(i, j), ...]) for duplicate pairs (i, j) with i < j.
    """
    seen: dict = {}  # normalized key -> first index
    duplicates: List[Tuple[int, int]] = []
    for idx, tc in enumerate(test_cases):
        inp, out = _tc_key(tc)
        key = normalize_tc_input_output(inp, out)
        key_str = f"{key[0]}|{key[1]}"
        if key_str in seen:
            duplicates.append((seen[key_str], idx))
        else:
            seen[key_str] = idx
    return (len(duplicates) == 0, duplicates)


def validate_no_duplicate_inputs(test_cases: List) -> Tuple[bool, List[Tuple[int, int]]]:
    """
    Check that no two test cases have the same normalized input (would be ambiguous for judge).
    Returns (True, []) if valid; (False, [(i, j), ...]) for pairs with same input, i < j.
    """
    seen: dict = {}  # normalized input -> first index
    duplicates: List[Tuple[int, int]] = []
    for idx, tc in enumerate(test_cases):
        inp, _ = _tc_key(tc)
        n_inp, _ = normalize_tc_input_output(inp, "")
        if n_inp in seen:
            duplicates.append((seen[n_inp], idx))
        else:
            seen[n_inp] = idx
    return (len(duplicates) == 0, duplicates)


def deduplicate_test_cases(test_cases: List, preserve_order: bool = True) -> List:
    """
    Remove duplicate test cases (same normalized input + expected_output). Keeps first occurrence.
    Works with both TestCase objects and dicts.
    """
    if not test_cases:
        return test_cases
    seen_keys: Set[str] = set()
    out = []
    for tc in test_cases:
        inp, out_val = _tc_key(tc)
        n_inp, n_out = normalize_tc_input_output(inp, out_val)
        key_str = f"{n_inp}|{n_out}"
        if key_str in seen_keys:
            continue
        seen_keys.add(key_str)
        out.append(tc)
    return out


def get_all_hashes_for_problem(test_cases: List) -> List[Tuple[int, str]]:
    """Return list of (index, hash) for each test case. Used by duplicate detection script."""
    result = []
    for idx, tc in enumerate(test_cases):
        inp, out = _tc_key(tc)
        h = tc_hash(inp, out)
        result.append((idx, h))
    return result


def _is_hidden(tc) -> bool:
    """Return True if test case is hidden (works with TestCase or dict)."""
    if isinstance(tc, TestCase):
        return tc.is_hidden
    return bool(tc.get("is_hidden"))


def validate_test_case_requirements(
    test_cases: List,
    min_visible: int = MIN_VISIBLE_TEST_CASES,
    min_hidden: int = MIN_HIDDEN_TEST_CASES,
) -> Tuple[bool, List[str]]:
    """
    Validate that test cases meet minimum visible and hidden counts.
    Returns (True, []) if valid; (False, list of error messages) otherwise.
    """
    errors: List[str] = []
    if not test_cases:
        return (False, ["At least one test case is required."])
    visible_count = sum(1 for tc in test_cases if not _is_hidden(tc))
    hidden_count = sum(1 for tc in test_cases if _is_hidden(tc))
    if visible_count < min_visible:
        errors.append(
            f"Visible test cases: {visible_count} (minimum required: {min_visible}). "
            "Each problem must have at least 2 visible example test cases."
        )
    if hidden_count < min_hidden:
        errors.append(
            f"Hidden test cases: {hidden_count} (minimum required: {min_hidden}). "
            "Each problem must have at least 20 hidden test cases."
        )
    return (len(errors) == 0, errors)


def all_visible_outputs_identical(test_cases: List) -> bool:
    """
    Return True if all visible test cases have the same expected_output (normalized).
    Used to warn about overfitting to a single outcome.
    """
    visible = [tc for tc in test_cases if not _is_hidden(tc)]
    if len(visible) < 2:
        return False
    inp0, out0 = _tc_key(visible[0])
    _, first_out = normalize_tc_input_output(inp0, out0)
    for tc in visible[1:]:
        inp, out = _tc_key(tc)
        _, norm_out = normalize_tc_input_output(inp, out)
        if norm_out != first_out:
            return False
    return True
