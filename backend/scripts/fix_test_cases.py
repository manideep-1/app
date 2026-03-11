#!/usr/bin/env python3
"""
Fix test case counts: ensure every problem has at least 2 visible and 20 hidden test cases.
Uses official solution (Python) to generate expected_output for new inputs where possible.
Run from backend: python scripts/fix_test_cases.py [--dry-run]
"""
import asyncio
import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

ROOT_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv
load_dotenv(ROOT_DIR / ".env")
# Keep generation timeout tight so large backfills complete quickly.
if os.environ.get("EXECUTION_TIMEOUT_SEC", "").strip() in ("", "2"):
    os.environ["EXECUTION_TIMEOUT_SEC"] = "2"
# Batch generation uses Python only; local execution is much faster than container startup.
os.environ.setdefault("FORCE_LOCAL_PYTHON_EXECUTION", "1")

from motor.motor_asyncio import AsyncIOMotorClient

from test_case_validation import (
    validate_test_case_requirements,
    validate_no_duplicates_within_problem,
    deduplicate_test_cases,
    MIN_VISIBLE_TEST_CASES,
    MIN_HIDDEN_TEST_CASES,
)
from test_case_generator import (
    candidate_inputs_from_existing,
    build_full_code_python,
    run_solution_for_input,
)
from code_executor import CodeExecutor
from signature_contract import align_solution_code_to_metadata


def _tc_list(tcs):
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


def _to_db_tcs(tcs):
    return [{"input": t["input"], "expected_output": t["expected_output"], "is_hidden": t["is_hidden"]} for t in tcs]


def _fallback_candidate_inputs(max_candidates: int = 120):
    """Format-agnostic fallback candidates used when structured generation stalls."""
    out = []
    # 1-line numeric inputs
    for n in range(1, 10):
        out.append(" ".join(str((i % 11) - 5) for i in range(n)))
    for a in range(-3, 4):
        out.append(str(a))
        out.append(f"{a} {a + 1}")
        out.append(f"{a} {a + 1} {a + 2}")
    # 2-line numeric inputs
    for a in range(-2, 3):
        for b in range(-2, 3):
            out.append(f"{a} {b}\n{a + b}")
            out.append(f"{a}\n{b}")
    # Simple text and command-like inputs
    out.extend([
        "a",
        "ab",
        "abc",
        "()",
        "()[]{}",
        "push 1 push 2 top pop",
        "insert apple search apple startsWith app",
        "addWord bad addWord dad search .ad",
        "2\nput 1 1 put 2 2 get 1 get 2",
    ])
    # Keep insertion order and unique normalized values.
    seen = set()
    uniq = []
    for cand in out:
        key = " ".join((cand or "").strip().split())
        if key in seen:
            continue
        seen.add(key)
        uniq.append(cand)
        if len(uniq) >= max_candidates:
            break
    return uniq


def _resolve_function_metadata_for_problem(title: str, problem_doc: dict, approaches):
    """Best-effort metadata resolution so solution code can be signature-aligned."""
    try:
        from models import ProblemFunctionMetadata
    except Exception:
        return None

    meta = (problem_doc or {}).get("function_metadata")
    if isinstance(meta, dict):
        try:
            return ProblemFunctionMetadata(**meta)
        except Exception:
            pass
    try:
        from problem_metadata_registry import get_metadata
        entry = get_metadata(title or "")
        if entry is not None:
            return entry[0]
    except Exception:
        pass
    try:
        from seed_solutions import _infer_alignment_metadata
        inferred = _infer_alignment_metadata(title or "", approaches or [])
        if inferred is not None:
            return inferred
    except Exception:
        pass
    return None


async def run_fix(
    db,
    dry_run: bool = False,
    limit: int = 0,
    worker_index: int = 0,
    worker_count: int = 1,
):
    """For each problem with insufficient test cases, try to add hidden (and visible if needed) by running solution.
    limit: max number of problems to update (0 = no limit)."""
    try:
        from seed_solutions import get_solutions_for_problem
    except ImportError:
        print("seed_solutions not available; cannot fetch solution code.")
        return

    executor = CodeExecutor()
    problems = await db.problems.find(
        {},
        {"_id": 0, "id": 1, "title": 1, "test_cases": 1, "driver_code_python": 1, "tags": 1},
    ).to_list(None)

    fixed = 0
    skipped_no_solution = 0
    skipped_no_driver = 0
    failed = 0
    need_fix = []
    for p in problems:
        tcs = _tc_list(p.get("test_cases") or [])
        vis = sum(1 for t in tcs if not t["is_hidden"])
        hid = sum(1 for t in tcs if t["is_hidden"])
        if vis < MIN_VISIBLE_TEST_CASES or hid < MIN_HIDDEN_TEST_CASES:
            need_fix.append(p)
    need_fix = sorted(need_fix, key=lambda p: (p.get("title") or ""))
    if worker_count > 1:
        need_fix = [p for i, p in enumerate(need_fix) if i % worker_count == worker_index]
        print(
            f"Worker shard {worker_index + 1}/{worker_count}: assigned {len(need_fix)} problems.",
            flush=True,
        )
    if limit > 0:
        need_fix = need_fix[:limit]
        print(f"Processing up to {len(need_fix)} problems with insufficient test cases (limit={limit}).")
    problems = need_fix

    for p in problems:
        title = p.get("title") or p.get("id") or "?"
        tcs = _tc_list(p.get("test_cases") or [])
        visible_count = sum(1 for t in tcs if not t["is_hidden"])
        hidden_count = sum(1 for t in tcs if t["is_hidden"])

        if visible_count >= MIN_VISIBLE_TEST_CASES and hidden_count >= MIN_HIDDEN_TEST_CASES:
            continue

        # Prefer signature-aligned solutions; fall back to raw so we can still fix test cases when code exists but other langs are missing
        solutions = get_solutions_for_problem(title, enforce_signature=True)
        if not solutions or not (solutions.get("approaches")):
            solutions = get_solutions_for_problem(title, enforce_signature=False)
        if not solutions or not (solutions.get("approaches")):
            skipped_no_solution += 1
            continue
        approaches = solutions.get("approaches") or []
        code_py = None
        for approach in approaches:
            if isinstance(approach, dict):
                code_py = (approach.get("code_python") or "").strip()
            else:
                code_py = (getattr(approach, "code_python", None) or "").strip()
            if code_py:
                break
        if not code_py:
            skipped_no_solution += 1
            continue
        try:
            metadata_obj = _resolve_function_metadata_for_problem(title, p, approaches)
            if metadata_obj is not None:
                code_py = align_solution_code_to_metadata(code_py, "python", metadata_obj)
        except Exception:
            pass

        # Prefer driver from seed_starters/registry (correct I/O) when available; fall back to DB
        starters = None
        try:
            from seed_starters import get_starters_for_problem
            starters = get_starters_for_problem(title)
            driver = (starters.get("driver_code_python") or "").strip() if starters else ""
        except ImportError:
            driver = ""
        if not driver:
            driver = (p.get("driver_code_python") or "").strip()
        if not driver:
            skipped_no_driver += 1
            continue

        full_code = build_full_code_python(code_py, driver)
        need_hidden = max(0, MIN_HIDDEN_TEST_CASES - hidden_count)
        need_visible = max(0, MIN_VISIBLE_TEST_CASES - visible_count)
        existing_keys = {(t["input"].strip(), t["expected_output"].strip()) for t in tcs}
        existing_inputs_norm = set()
        for t in tcs:
            inp = (t["input"] or "").strip()
            existing_inputs_norm.add(" ".join(inp.split()))
            existing_inputs_norm.add(inp)

        new_hidden = []
        need_total_new = need_hidden + need_visible
        print(f"Processing {title!r}: visible={visible_count}, hidden={hidden_count}, need_new={need_total_new}", flush=True)
        # Request enough candidates across multiple passes until we fill required visible+hidden.
        attempts_without_progress = 0
        while len(new_hidden) < need_total_new and attempts_without_progress < 2:
            missing = need_total_new - len(new_hidden)
            candidates = candidate_inputs_from_existing(
                tcs + new_hidden,
                tags=p.get("tags"),
                max_candidates=max(missing * 2, 24),
            )
            if not candidates:
                candidates = []
            added_this_round = 0
            for inp in candidates:
                if len(new_hidden) >= need_total_new:
                    break
                inp_stripped = inp.strip()
                norm = " ".join(inp_stripped.split())
                if norm in existing_inputs_norm:
                    continue
                out = run_solution_for_input(full_code, "python", inp, executor)
                if out is None:
                    continue
                if (inp_stripped, out) in existing_keys:
                    continue
                existing_keys.add((inp_stripped, out))
                existing_inputs_norm.add(norm)
                new_hidden.append({"input": inp_stripped, "expected_output": out, "is_hidden": True})
                added_this_round += 1
            if added_this_round > 0:
                attempts_without_progress = 0
                continue
            # If structured generation stalls, try generic fallback candidates.
            for inp in _fallback_candidate_inputs(max_candidates=max(missing * 2, 24)):
                if len(new_hidden) >= need_total_new:
                    break
                inp_stripped = inp.strip()
                norm = " ".join(inp_stripped.split())
                if norm in existing_inputs_norm:
                    continue
                out = run_solution_for_input(full_code, "python", inp, executor)
                if out is None:
                    continue
                if (inp_stripped, out) in existing_keys:
                    continue
                existing_keys.add((inp_stripped, out))
                existing_inputs_norm.add(norm)
                new_hidden.append({"input": inp_stripped, "expected_output": out, "is_hidden": True})
                added_this_round += 1
            if added_this_round == 0:
                attempts_without_progress += 1
            else:
                attempts_without_progress = 0

        # Build visible list: existing visible + promoted hidden + some of new_hidden as visible
        visible_part = [{"input": t["input"], "expected_output": t["expected_output"], "is_hidden": False} for t in tcs if not t["is_hidden"]]
        hidden_part = [{"input": t["input"], "expected_output": t["expected_output"], "is_hidden": True} for t in tcs if t["is_hidden"]]
        need_visible_more = max(0, MIN_VISIBLE_TEST_CASES - len(visible_part))
        # Promote existing hidden to visible first (so we keep more generated as hidden)
        promoted = 0
        promoted_indices = set()
        for i, t in enumerate(hidden_part):
            if promoted >= need_visible_more:
                break
            visible_part.append({"input": t["input"], "expected_output": t["expected_output"], "is_hidden": False})
            promoted_indices.add(i)
            promoted += 1
        hidden_part = [t for i, t in enumerate(hidden_part) if i not in promoted_indices]
        need_visible_more = max(0, MIN_VISIBLE_TEST_CASES - len(visible_part))
        take = 0
        if need_visible_more > 0 and new_hidden:
            take = min(need_visible_more, len(new_hidden))
            for i in range(take):
                visible_part.append({"input": new_hidden[i]["input"], "expected_output": new_hidden[i]["expected_output"], "is_hidden": False})
            new_hidden = new_hidden[take:]
        # Final list: all visible then all hidden (no duplicate input+output; promoted removed from hidden)
        updated = visible_part + hidden_part + new_hidden
        updated = deduplicate_test_cases(updated)
        ok, errs = validate_test_case_requirements(updated)
        if not ok:
            failed += 1
            # Log why: still short on visible/hidden after adding what we could
            vis_after = sum(1 for t in updated if not t.get("is_hidden"))
            hid_after = sum(1 for t in updated if t.get("is_hidden"))
            print(f"  [FAIL] {title!r}: after update visible={vis_after} hidden={hid_after} (need 2 visible, 20 hidden). {errs}")
            continue
        added_hidden = len(new_hidden)
        added_visible = promoted + take
        if added_hidden == 0 and added_visible == 0 and promoted == 0:
            continue
        if dry_run:
            print(f"[DRY-RUN] Would update {title!r}: +{added_hidden} hidden, +{added_visible} visible (promoted {promoted} hidden→visible)")
            fixed += 1
            continue
        set_payload = {"test_cases": _to_db_tcs(updated)}
        if starters and starters.get("driver_code_python"):
            set_payload["driver_code_python"] = starters["driver_code_python"]
            if starters.get("starter_code_python"):
                set_payload["starter_code_python"] = starters["starter_code_python"]
        await db.problems.update_one(
            {"title": title},
            {"$set": set_payload},
        )
        print(f"Updated {title!r}: +{added_hidden} hidden, +{added_visible} visible (promoted {promoted} hidden→visible)")
        fixed += 1

    print(f"\nFixed: {fixed}, Skipped (no solution): {skipped_no_solution}, Skipped (no driver): {skipped_no_driver}, Failed: {failed}")


async def main():
    parser = argparse.ArgumentParser(description="Fix test case counts (min 2 visible, 20 hidden)")
    parser.add_argument("--dry-run", action="store_true", help="Only report what would be updated")
    parser.add_argument("--limit", type=int, default=0, help="Max number of problems to fix (0 = all)")
    parser.add_argument("--worker-index", type=int, default=0, help="0-based worker index for sharded parallel runs")
    parser.add_argument("--worker-count", type=int, default=1, help="Total worker shards for parallel runs")
    args = parser.parse_args()
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Set MONGO_URL and DB_NAME")
        sys.exit(1)
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    worker_count = max(1, int(args.worker_count or 1))
    worker_index = int(args.worker_index or 0)
    if worker_index < 0 or worker_index >= worker_count:
        print(f"Invalid --worker-index={worker_index} for --worker-count={worker_count}")
        sys.exit(1)
    await run_fix(
        db,
        dry_run=args.dry_run,
        limit=args.limit,
        worker_index=worker_index,
        worker_count=worker_count,
    )
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
