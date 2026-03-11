#!/usr/bin/env python3
"""
Audit all problems against the 5-stage pipeline rules. Optionally rebuild using the pipeline.

- Re-run validation (Stage 4: ≥2 approaches, all languages, dry run, complexity).
- Report: total problems, passed, need rebuild, compilation failures.
- With --rebuild: for each problem that fails validation, run the full pipeline and write
  generated solution to backend/generated_solutions/<slug>.json (review before merging into seed_solutions).

Run from repo root:
  python backend/scripts/audit_and_rebuild_solutions.py
  python backend/scripts/audit_and_rebuild_solutions.py --rebuild
  python backend/scripts/audit_and_rebuild_solutions.py --rebuild --limit 2
"""
from __future__ import annotations

import asyncio
import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from solution_validator import validate_solution, get_validation_errors, REQUIRED_LANGS, MIN_CODE_LENGTH
from solution_generation_pipeline import run_pipeline_sync, stage4_validate_content, MIN_APPROACHES_REQUIRED


def _slug(title: str) -> str:
    return re.sub(r"[^\w\-]", "_", (title or "").strip())[:80]


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


def _validate_current_solution(problem_title: str, solution: dict, strict: bool = False) -> tuple:
    """Validate current solution (seed data). strict=False: allow missing languages/dry_run; strict=True: full pipeline bar."""
    if not solution or not (solution.get("approaches") or []):
        return False, ["No approaches"]
    approaches = solution.get("approaches") or []
    # When auditing seed data, don't require all 6 languages (many only have Python/JS)
    errors = list(get_validation_errors(
        solution,
        require_all_languages=strict,
        reject_placeholders=True,
    ))
    if len(approaches) < MIN_APPROACHES_REQUIRED:
        errors.append(f"Need at least {MIN_APPROACHES_REQUIRED} approaches")
    if strict:
        dry_run = (solution.get("dry_run") or solution.get("dryRun") or "").strip()
        if not dry_run:
            errors.append("dry_run missing or empty")
    if strict:
        for i, app in enumerate(approaches):
            if not (app.get("complexity") or "").strip():
                errors.append(f"Approach {i + 1}: complexity missing")
    return (len(errors) == 0, errors)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Audit solutions; optionally rebuild with 5-stage pipeline")
    parser.add_argument("--rebuild", action="store_true", help="Run pipeline for failed problems and write JSON")
    parser.add_argument("--limit", type=int, default=0, help="Limit rebuild to N problems (0 = all failed)")
    parser.add_argument("--skip-compilation", action="store_true", help="Skip Stage 3 compilation when rebuilding")
    parser.add_argument("--accept-partial", action="store_true", help="Accept pipeline output with fewer than 6 languages; write to <slug>.json and count as rebuilt")
    parser.add_argument("--debug", action="store_true", help="On validation failure, write merged solution to <slug>_partial.json for inspection")
    parser.add_argument("--strict", action="store_true", help="Require all 6 languages and dry_run (default: lenient for seed data)")
    args = parser.parse_args()

    from seed_solutions import get_solutions_for_problem, SOLUTIONS, RICH_SOLUTIONS

    all_titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    total = len(all_titles)
    passed = []
    need_rebuild = []
    validation_errors_by_title = {}
    compilation_failures = []

    for title in all_titles:
        solution = get_solutions_for_problem(title, enforce_signature=False)
        valid, errs = _validate_current_solution(title, solution or {}, strict=args.strict)
        if valid:
            passed.append(title)
        else:
            need_rebuild.append(title)
            validation_errors_by_title[title] = errs

    print("=" * 60)
    print("SOLUTION PIPELINE AUDIT")
    print("=" * 60)
    print(f"Total problems: {total}")
    print(f"Passed validation: {len(passed)}")
    print(f"Need rebuild: {len(need_rebuild)}")
    if need_rebuild:
        print("\n--- Problems needing rebuild (sample) ---")
        for t in need_rebuild[:15]:
            print(f"  {t}: {validation_errors_by_title.get(t, [])[:3]}")
        if len(need_rebuild) > 15:
            print(f"  ... and {len(need_rebuild) - 15} more")

    if not args.rebuild:
        print("\nRun with --rebuild to regenerate solutions using the 5-stage pipeline.")
        return 0 if not need_rebuild else 1

    problems = asyncio.run(_load_problems_async())
    by_title = {p.get("title"): p for p in problems if p.get("title")}
    if not by_title:
        print("No problems loaded from DB. Set MONGO_URL and DB_NAME. Rebuild skipped.")
        return 1

    from code_executor import CodeExecutor
    executor = CodeExecutor()
    out_dir = ROOT / "generated_solutions"
    out_dir.mkdir(parents=True, exist_ok=True)
    to_rebuild = need_rebuild if not args.limit else need_rebuild[: args.limit]
    rebuilt = 0
    failed_rebuild = []

    for title in to_rebuild:
        problem = by_title.get(title)
        if not problem:
            failed_rebuild.append((title, "Problem not in DB"))
            continue
        sol, errs = run_pipeline_sync(
            problem,
            executor,
            skip_compilation=args.skip_compilation,
            return_merged_on_validation_fail=args.debug,
        )
        if errs and not sol:
            failed_rebuild.append((title, errs[:5]))
            continue
        if sol:
            # When --accept-partial, allow output that doesn't have all 6 languages (for review)
            valid, content_errs = stage4_validate_content(sol, require_all_languages=not args.accept_partial)
            if not valid:
                failed_rebuild.append((title, content_errs[:5]))
                slug = _slug(title)
                partial_path = out_dir / f"{slug}_partial.json"
                with open(partial_path, "w", encoding="utf-8") as f:
                    json.dump(sol, f, indent=2)
                print(f"  (wrote partial: {partial_path})")
                continue
            slug = _slug(title)
            path = out_dir / f"{slug}.json"
            with open(path, "w", encoding="utf-8") as f:
                json.dump(sol, f, indent=2)
            rebuilt += 1
            print(f"Rebuilt: {title} -> {path}")

    print(f"\nRebuilt: {rebuilt}")
    if failed_rebuild:
        print("Rebuild failed for:")
        for t, e in failed_rebuild[:10]:
            print(f"  {t}: {e}")
    print(f"Generated solutions written to {out_dir}. Review before merging into seed_solutions.")
    return 0 if rebuilt else 1


if __name__ == "__main__":
    sys.exit(main())
