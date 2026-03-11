#!/usr/bin/env python3
"""
Parallel strict rebuild of solution content for all problems.

Targets:
- >=2 approaches per problem
- all required languages in each approach
- dry_run and complexity present

Writes generated JSON files to backend/generated_solutions/<slug>.json and can
resume by skipping already-valid files.
"""
from __future__ import annotations

import argparse
import asyncio
import concurrent.futures
import json
import os
from pathlib import Path
import re
import sys
from typing import Dict, Any, Tuple, List

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from seed_solutions import SOLUTIONS, RICH_SOLUTIONS, get_solutions_for_problem
from solution_generation_pipeline import run_pipeline_sync, stage4_validate_content
from solution_validator import get_validation_errors, REQUIRED_LANGS


def _slug(title: str) -> str:
    return re.sub(r"[^\w\-]", "_", (title or "").strip())[:80]


def _is_current_solution_strict_valid(solution: dict) -> Tuple[bool, List[str]]:
    if not solution or not (solution.get("approaches") or []):
        return False, ["No approaches"]
    approaches = solution.get("approaches") or []
    errors = list(get_validation_errors(solution, require_all_languages=True, reject_placeholders=True))
    if len(approaches) < 2:
        errors.append("Need at least 2 approaches")
    if not (solution.get("dry_run") or solution.get("dryRun") or "").strip():
        errors.append("dry_run missing or empty")
    for i, app in enumerate(approaches):
        if not (app.get("complexity") or "").strip():
            errors.append(f"Approach {i + 1}: complexity missing")
    return len(errors) == 0, errors


def _is_generated_file_strict_valid(path: Path) -> bool:
    if not path.exists():
        return False
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False
    valid, _ = stage4_validate_content(payload, require_all_languages=True)
    return bool(valid)


async def _load_problems_async():
    try:
        from dotenv import load_dotenv
        from motor.motor_asyncio import AsyncIOMotorClient

        load_dotenv(ROOT / ".env")
        mongo_url = os.environ.get("MONGO_URL")
        db_name = os.environ.get("DB_NAME")
        if not mongo_url or not db_name:
            return []
        client = AsyncIOMotorClient(mongo_url)
        db = client[db_name]
        proj = {"_id": 0, "title": 1, "description": 1, "function_metadata": 1, "test_cases": 1}
        for lang in REQUIRED_LANGS:
            proj[f"driver_code_{lang}"] = 1
        return await db.problems.find({}, proj).to_list(length=None)
    except Exception as e:
        print("DB load failed:", e)
        return []


def _rebuild_one(title: str, problem: Dict[str, Any], out_dir: Path) -> Tuple[str, str]:
    """
    Returns tuple (status, message)
    status in {"rebuilt", "failed"}
    """
    try:
        sol, errs = run_pipeline_sync(
            problem,
            None,
            skip_compilation=True,
            return_merged_on_validation_fail=False,
        )
    except Exception as e:
        return "failed", f"{title}: exception {e}"

    if errs and not sol:
        return "failed", f"{title}: {errs[:3]}"
    if not sol:
        return "failed", f"{title}: empty pipeline output"

    valid, content_errs = stage4_validate_content(sol, require_all_languages=True)
    if not valid:
        return "failed", f"{title}: {content_errs[:3]}"

    path = out_dir / f"{_slug(title)}.json"
    try:
        path.write_text(json.dumps(sol, indent=2), encoding="utf-8")
    except Exception as e:
        return "failed", f"{title}: write failed {e}"
    return "rebuilt", f"{title} -> {path}"


def main() -> int:
    parser = argparse.ArgumentParser(description="Parallel strict rebuild for all problem solutions.")
    parser.add_argument("--workers", type=int, default=4, help="Parallel workers for generation")
    parser.add_argument("--limit", type=int, default=0, help="Rebuild at most N problems (0 = all)")
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip titles with already-valid generated_solutions/<slug>.json",
    )
    args = parser.parse_args()

    all_titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    need_rebuild = []
    for title in all_titles:
        cur = get_solutions_for_problem(title, enforce_signature=False)
        valid, _ = _is_current_solution_strict_valid(cur or {})
        if not valid:
            need_rebuild.append(title)

    if args.limit and args.limit > 0:
        need_rebuild = need_rebuild[: args.limit]

    out_dir = ROOT / "generated_solutions"
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.skip_existing:
        before = len(need_rebuild)
        need_rebuild = [
            t for t in need_rebuild
            if not _is_generated_file_strict_valid(out_dir / f"{_slug(t)}.json")
        ]
        print(f"Skip-existing filtered {before - len(need_rebuild)} titles")

    problems = asyncio.run(_load_problems_async())
    by_title = {p.get("title"): p for p in problems if p.get("title")}
    queue: List[Tuple[str, Dict[str, Any]]] = [(t, by_title[t]) for t in need_rebuild if t in by_title]
    missing_from_db = [t for t in need_rebuild if t not in by_title]

    print("=" * 60)
    print("PARALLEL STRICT REBUILD")
    print("=" * 60)
    print(f"Total titles: {len(all_titles)}")
    print(f"Need rebuild: {len(need_rebuild)}")
    print(f"In DB queue: {len(queue)}")
    print(f"Missing in DB: {len(missing_from_db)}")

    rebuilt = 0
    failed = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        futures = {
            pool.submit(_rebuild_one, title, problem, out_dir): title
            for title, problem in queue
        }
        total = len(futures)
        done = 0
        for fut in concurrent.futures.as_completed(futures):
            done += 1
            status, msg = fut.result()
            if status == "rebuilt":
                rebuilt += 1
                print(f"[{done}/{total}] Rebuilt: {msg}")
            else:
                failed.append(msg)
                print(f"[{done}/{total}] Failed: {msg}")

    print("\n" + "=" * 60)
    print("REBUILD SUMMARY")
    print("=" * 60)
    print(f"Rebuilt: {rebuilt}")
    print(f"Failed: {len(failed)}")
    if missing_from_db:
        print(f"Missing in DB: {len(missing_from_db)}")
    if failed:
        for row in failed[:20]:
            print(" ", row)
        if len(failed) > 20:
            print(f" ... and {len(failed) - 20} more")
    return 0 if (len(failed) == 0 and len(missing_from_db) == 0) else 1


if __name__ == "__main__":
    raise SystemExit(main())
