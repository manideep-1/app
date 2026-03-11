#!/usr/bin/env python3
"""
Duplicate test case detection for ifelse platform.
Scans all problems in the database and reports:
- Within-problem duplicates (same input+expected_output in one problem)
- Across-problem duplicates (same test case in multiple problems)
Run from backend: python scripts/detect_duplicate_test_cases.py
"""
import asyncio
import os
import sys
from pathlib import Path
from collections import defaultdict

# Add backend root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from test_case_validation import (
    tc_hash,
    validate_no_duplicates_within_problem,
    normalize_tc_input_output,
)


ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")


def _tc_key(tc):
    inp = (tc.get("input") or "").strip()
    out = (tc.get("expected_output") or "").strip()
    return inp, out


async def run_detection():
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Set MONGO_URL and DB_NAME (e.g. in .env)")
        sys.exit(1)
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]

    problems = await db.problems.find({}, {"_id": 0, "id": 1, "title": 1, "test_cases": 1}).to_list(None)
    print(f"Scanned {len(problems)} problems.\n")

    # Global: hash -> [(problem_id, title, case_index, is_hidden)]
    global_hashes = defaultdict(list)
    within_duplicates = []
    across_duplicates = []

    for p in problems:
        pid = p.get("id") or p.get("title") or "?"
        title = p.get("title") or pid
        tcs = p.get("test_cases") or []
        # Convert to list of dicts for validation
        list_of_dicts = [
            {"input": tc.get("input"), "expected_output": tc.get("expected_output"), "is_hidden": tc.get("is_hidden")}
            for tc in tcs
        ]
        ok, pairs = validate_no_duplicates_within_problem(list_of_dicts)
        if not ok:
            within_duplicates.append((pid, title, pairs))
        for idx, tc in enumerate(tcs):
            inp, out = _tc_key(tc)
            h = tc_hash(inp, out)
            global_hashes[h].append((pid, title, idx, tc.get("is_hidden")))

    # Report within-problem duplicates
    print("=== WITHIN-PROBLEM DUPLICATES (same test case repeated in one problem) ===")
    if not within_duplicates:
        print("None found.\n")
    else:
        for pid, title, pairs in within_duplicates:
            print(f"  {title} (id={pid}): duplicate pairs (index i, j): {pairs}")
        print()

    # Report across-problem duplicates (hash appears in more than one problem, or more than once in one problem)
    print("=== ACROSS-PROBLEM / GLOBAL DUPLICATES (same input+output in multiple problems or twice in one) ===")
    seen_hashes_reported = set()
    for h, locations in global_hashes.items():
        if len(locations) <= 1:
            continue
        # Dedupe by (pid, index)
        by_problem = defaultdict(set)
        for pid, title, idx, is_hidden in locations:
            by_problem[(pid, title)].add((idx, is_hidden))
        if len(by_problem) <= 1 and all(len(v) <= 1 for v in by_problem.values()):
            continue
        if h in seen_hashes_reported:
            continue
        seen_hashes_reported.add(h)
        across_duplicates.append((h, locations))
        print(f"  Hash {h[:16]}... appears in:")
        for pid, title, idx, is_hidden in locations:
            vis = "hidden" if is_hidden else "visible"
            print(f"    - {title} (id={pid}) case index {idx} ({vis})")
        print()

    # Summary
    print("=== SUMMARY ===")
    print(f"  Within-problem duplicate groups: {len(within_duplicates)}")
    print(f"  Across-problem duplicate hashes: {len(across_duplicates)}")
    if within_duplicates or across_duplicates:
        print("\n  Fix: Re-run seed_db.py (it deduplicates visible and now hidden cases), or fix seed data and re-seed.")
    else:
        print("  All test cases are unique within each problem and no cross-problem duplicates reported.")
    client.close()


if __name__ == "__main__":
    asyncio.run(run_detection())
