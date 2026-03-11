#!/usr/bin/env python3
"""
Test case integrity validation: scan all problems and report minimum-requirement violations.

GLOBAL RULES (MANDATORY):
  - Minimum 2 visible example test cases per problem
  - Minimum 20 hidden test cases per problem
  - No duplicate (input, expected_output) within a problem
  - If all visible outputs identical → warn (overfitting risk)

Run from backend: python scripts/validate_test_case_integrity.py [--fix]
  --fix: run the test case fix script to add missing hidden/visible cases (if solution available)
"""
import asyncio
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from test_case_validation import (
    validate_test_case_requirements,
    validate_no_duplicates_within_problem,
    validate_no_duplicate_inputs,
    all_visible_outputs_identical,
    MIN_VISIBLE_TEST_CASES,
    MIN_HIDDEN_TEST_CASES,
)

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _tc_list(tcs):
    """Normalize to list of dicts with input, expected_output, is_hidden."""
    out = []
    for tc in tcs or []:
        if isinstance(tc, dict):
            out.append({
                "input": tc.get("input") or "",
                "expected_output": tc.get("expected_output") or "",
                "is_hidden": bool(tc.get("is_hidden")),
            })
        else:
            out.append({
                "input": getattr(tc, "input", "") or "",
                "expected_output": getattr(tc, "expected_output", "") or "",
                "is_hidden": bool(getattr(tc, "is_hidden", False)),
            })
    return out


async def run_report(fix: bool = False):
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Set MONGO_URL and DB_NAME (e.g. in .env)")
        sys.exit(1)
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    problems = await db.problems.find(
        {},
        {"_id": 0, "id": 1, "title": 1, "test_cases": 1},
    ).to_list(None)

    total = len(problems)
    fewer_visible = []
    fewer_hidden = []
    duplicate_inputs = []  # (input, output) duplicate pairs
    duplicate_input_only = []  # same input appearing more than once (ambiguous for judge)
    identical_output_warn = []
    ok_count = 0

    for p in problems:
        pid = p.get("id") or p.get("title") or "?"
        title = p.get("title") or pid
        tcs = _tc_list(p.get("test_cases") or [])

        if not tcs:
            fewer_visible.append((pid, title, 0, 0))
            continue

        visible_count = sum(1 for tc in tcs if not tc.get("is_hidden"))
        hidden_count = sum(1 for tc in tcs if tc.get("is_hidden"))

        ok_here = True
        if visible_count < MIN_VISIBLE_TEST_CASES:
            fewer_visible.append((pid, title, visible_count, hidden_count))
            ok_here = False
        if hidden_count < MIN_HIDDEN_TEST_CASES:
            fewer_hidden.append((pid, title, visible_count, hidden_count))
            ok_here = False

        ok, dup_pairs = validate_no_duplicates_within_problem(tcs)
        if not ok:
            duplicate_inputs.append((pid, title, dup_pairs))
            ok_here = False
        ok_in, dup_in_pairs = validate_no_duplicate_inputs(tcs)
        if not ok_in:
            duplicate_input_only.append((pid, title, dup_in_pairs))
            ok_here = False

        if all_visible_outputs_identical(tcs):
            identical_output_warn.append((pid, title))

        if ok_here:
            ok_count += 1

    # Report (STEP 1: validation report)
    print("=" * 60)
    print("TEST CASE INTEGRITY REPORT")
    print("=" * 60)
    print()
    print("SUMMARY (mandatory minimums: 2 visible, 20 hidden)")
    print("-" * 60)
    print(f"  Total problems: {total}")
    print(f"  Problems with < {MIN_VISIBLE_TEST_CASES} visible test cases: {len(fewer_visible)}")
    print(f"  Problems with < {MIN_HIDDEN_TEST_CASES} hidden test cases: {len(fewer_hidden)}")
    print(f"  Problems with duplicate test cases: {len(duplicate_inputs)}")
    print(f"  Problems meeting all minimums (no duplicates): {ok_count}")
    print()

    print("--- Problems with fewer than 2 visible test cases (log problem ID) ---")
    if not fewer_visible:
        print("None.")
    else:
        for pid, title, vis, hid in sorted(fewer_visible, key=lambda x: (x[2], x[3])):
            print(f"  problem_id={pid}  title={title!r}  visible={vis}  hidden={hid}")
    print()

    print("--- Problems with fewer than 20 hidden test cases (log problem ID) ---")
    if not fewer_hidden:
        print("None.")
    else:
        for pid, title, vis, hid in sorted(fewer_hidden, key=lambda x: (x[3], x[2])):
            print(f"  problem_id={pid}  title={title!r}  visible={vis}  hidden={hid}")
    print()

    print("--- Problems with duplicate test cases (same input+expected_output) ---")
    if not duplicate_inputs:
        print("None.")
    else:
        for pid, title, pairs in duplicate_inputs:
            print(f"  problem_id={pid}  title={title!r}  duplicate pairs (indices): {pairs}")
    print()
    print("--- Problems with duplicate inputs (same input used in multiple test cases) ---")
    if not duplicate_input_only:
        print("None.")
    else:
        for pid, title, pairs in duplicate_input_only:
            print(f"  problem_id={pid}  title={title!r}  duplicate input pairs (indices): {pairs}")
    print()

    print("--- Warning: all visible test cases have identical expected output ---")
    if not identical_output_warn:
        print("None.")
    else:
        for pid, title in identical_output_warn[:20]:
            print(f"  id={pid}  title={title!r}")
        if len(identical_output_warn) > 20:
            print(f"  ... and {len(identical_output_warn) - 20} more.")
    print()

    print("--- Violations prevent publish (reject if any) ---")
    print(f"  visible < {MIN_VISIBLE_TEST_CASES}: {len(fewer_visible)}  |  hidden < {MIN_HIDDEN_TEST_CASES}: {len(fewer_hidden)}  |  duplicate (input,output): {len(duplicate_inputs)}  |  duplicate inputs: {len(duplicate_input_only)}")
    print(f"  Warning (overfitting risk): all visible outputs identical: {len(identical_output_warn)}")
    if fix:
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            from fix_test_cases import run_fix
            await run_fix(db, dry_run=False)
        except Exception as e:
            print(f"\n  --fix failed: {e}. Run: python scripts/fix_test_cases.py")
    client.close()
    return len(fewer_visible), len(fewer_hidden), len(duplicate_inputs), len(duplicate_input_only)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Validate test case integrity across all problems")
    parser.add_argument("--fix", action="store_true", help="Attempt to add missing test cases via generator")
    args = parser.parse_args()
    nv, nh, nd, ndup_in = asyncio.run(run_report(fix=args.fix))
    if nv > 0 or nh > 0 or nd > 0 or ndup_in > 0:
        sys.exit(1)
    sys.exit(0)
