#!/usr/bin/env python3
"""
Mass audit: solution code integrity. Enforce strict validation rules.

- Scan all problems from seed_solutions.
- For each: ensure at least 1 approach, all 6 languages non-empty per approach,
  no placeholders, minimal code length.
- Optionally --compile: run each approach/language through executor with one test case.

Run from repo root: python backend/scripts/audit_solution_code_integrity.py [--compile] [--csv]
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from seed_solutions import get_solutions_for_problem, SOLUTIONS, RICH_SOLUTIONS  # noqa: E402
from solution_validator import (  # noqa: E402
    validate_solution,
    get_missing_languages_per_approach,
    get_validation_errors,
    REQUIRED_LANGS,
    CODE_KEY_BY_LANG,
)


def audit_all(
    compile_test: bool = False,
    db_problems: List[Dict[str, Any]] | None = None,
    limit: int = 0,
    lenient: bool = False,
) -> Dict[str, Any]:
    """
    Run integrity audit on every problem that has solutions.
    If compile_test and db_problems, run execution test for first approach per language.
    limit: if > 0, only audit first N problem titles (for quick runs).
    lenient: if True, only require at least one code block per approach (no verbal-only); do not require all 6 languages.
    """
    all_titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    if limit and limit > 0:
        all_titles = all_titles[:limit]
    total = len(all_titles)
    problems_missing_code: List[str] = []
    missing_languages_count: Dict[str, int] = {lang: 0 for lang in REQUIRED_LANGS}
    validation_errors_by_title: Dict[str, List[str]] = {}
    missing_per_problem: Dict[str, Dict[int, List[str]]] = {}  # title -> { approach_idx: [langs] }
    compilation_failures: List[str] = []
    passed_validation: List[str] = []
    passed_compile: List[str] = []

    if lenient:
        from solution_validator import validate_solution_verbal_only
        validator_fn = validate_solution_verbal_only
    else:
        validator_fn = validate_solution

    for title in all_titles:
        solution = get_solutions_for_problem(title, enforce_signature=False)
        if not solution:
            continue
        approaches = solution.get("approaches") or []
        if not approaches:
            problems_missing_code.append(title)
            continue

        valid, errors = validator_fn(solution)
        if not valid:
            validation_errors_by_title[title] = errors
            problems_missing_code.append(title)
            if not lenient:
                missing_per = get_missing_languages_per_approach(solution)
                missing_per_problem[title] = missing_per
                for idx, langs in missing_per.items():
                    for lang in langs:
                        missing_languages_count[lang] = missing_languages_count.get(lang, 0) + 1
        else:
            passed_validation.append(title)

        if compile_test and db_problems and valid:
            # Find problem in DB
            problem = next((p for p in db_problems if (p.get("title") or "") == title), None)
            if not problem:
                continue
            from models import Language, TestCase  # noqa: E402
            from code_executor import CodeExecutor  # noqa: E402
            from signature_contract import LANG_CODE_KEY  # noqa: E402

            tcs = problem.get("test_cases") or []
            if not tcs:
                continue
            test_cases = []
            for r in tcs[:1]:  # one test case
                try:
                    test_cases.append(TestCase(
                        input=r.get("input", ""),
                        expected_output=r.get("expected_output", ""),
                        is_hidden=bool(r.get("is_hidden", False)),
                    ))
                except Exception:
                    pass
            if not test_cases:
                continue

            executor = CodeExecutor()
            driver_by_lang = {lang: (problem.get(f"driver_code_{lang}") or "").strip() for lang in REQUIRED_LANGS}
            first_approach = approaches[0]

            for lang in REQUIRED_LANGS:
                key = CODE_KEY_BY_LANG.get(lang, f"code_{lang}")
                code = (first_approach or {}).get(key)
                if not code or not (code := (code or "").strip()):
                    continue
                driver = driver_by_lang.get(lang) or ""
                if lang == "go" and "___USER_CODE___" in driver:
                    full_code = driver.replace("___USER_CODE___", code)
                else:
                    full_code = (code + "\n\n" + driver) if driver else code
                try:
                    result = executor.execute_code(full_code, Language(lang), test_cases, visible_only=False)
                except Exception as e:
                    compilation_failures.append(f"{title} | {lang} | exception: {e}")
                    continue
                status = result.get("status")
                status_val = status.value if hasattr(status, "value") else str(status)
                if status_val not in ("accepted",) or result.get("passed", 0) < result.get("total", 0):
                    compilation_failures.append(f"{title} | {lang} | status={status_val} passed={result.get('passed')}/{result.get('total')}")
                else:
                    passed_compile.append(f"{title}|{lang}")

    return {
        "total_problems": total,
        "problems_with_solutions": len(all_titles),
        "problems_missing_code": problems_missing_code,
        "missing_languages_count": missing_languages_count,
        "validation_errors_by_title": validation_errors_by_title,
        "missing_per_problem": missing_per_problem,
        "compilation_failures": compilation_failures,
        "passed_validation": passed_validation,
        "passed_compile": passed_compile,
    }


async def _load_db_problems():
    """Load problems from MongoDB for compile test."""
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
        projection = {"_id": 0, "title": 1, "test_cases": 1}
        for lang in REQUIRED_LANGS:
            projection[f"driver_code_{lang}"] = 1
        return await db.problems.find({}, projection).to_list(length=None)
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser(description="Audit solution code integrity (strict validation)")
    parser.add_argument("--compile", action="store_true", help="Run compile/execute test (needs DB)")
    parser.add_argument("--csv", action="store_true", help="Write audit report to CSV")
    parser.add_argument("--limit", type=int, default=0, help="Limit number of problems (0 = all)")
    parser.add_argument(
        "--lenient",
        action="store_true",
        help="Only flag verbal-only (zero code blocks) and placeholders; do not require all 6 languages",
    )
    args = parser.parse_args()

    db_problems = None
    if args.compile:
        db_problems = asyncio.run(_load_db_problems())
        if not db_problems:
            print("Warning: --compile requested but no DB problems loaded (check MONGO_URL, DB_NAME)")

    result = audit_all(
        compile_test=args.compile,
        db_problems=db_problems,
        limit=args.limit,
        lenient=args.lenient,
    )

    total = result["total_problems"]
    missing_list = result["problems_missing_code"]
    missing_count = len(missing_list)
    missing_lang = result["missing_languages_count"]
    comp_fail = result["compilation_failures"]
    passed_val = result["passed_validation"]

    print("=" * 60)
    print("SOLUTION CODE INTEGRITY AUDIT (strict validation)")
    print("=" * 60)
    print(f"\nTotal problems (with solution data): {total}")
    print(f"Problems PASSING validation (all 6 langs, no placeholders): {len(passed_val)}")
    print(f"Problems FAILING (missing code / empty / placeholder): {missing_count}")
    print("\n--- Missing languages count ---")
    for lang in REQUIRED_LANGS:
        print(f"  {lang}: {missing_lang.get(lang, 0)} missing or invalid blocks")
    if comp_fail:
        print(f"\n--- Compilation / execution failures: {len(comp_fail)} ---")
        for row in comp_fail[:30]:
            print(f"  {row}")
        if len(comp_fail) > 30:
            print(f"  ... and {len(comp_fail) - 30} more")
    print("\n--- Sample problems needing fix (missing languages) ---")
    for title, per_app in list(result["missing_per_problem"].items())[:20]:
        parts = [f"{title}:"]
        for idx, langs in per_app.items():
            parts.append(f"  approach {idx} missing {', '.join(langs)}")
        print("\n".join(parts))
    if len(result["missing_per_problem"]) > 20:
        print(f"... and {len(result['missing_per_problem']) - 20} more problems")

    print("\n--- Recommendation ---")
    print("1. Run with --compile to verify execution (requires DB).")
    print("2. Fix missing languages: ensure every approach has code_java, code_python, code_cpp, code_javascript, code_go, code_csharp (non-empty, >50 chars, no ... or TODO).")
    print("3. Use solution_validator.validate_solution() before saving any solution.")
    print("4. See docs/SOLUTION_CONTENT_SCHEMA.md for mandatory structure.")

    if args.csv:
        import csv
        out_path = ROOT.parent / "solution_code_integrity_audit.csv"
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["title", "passes_validation", "missing_languages", "errors_sample"])
            for title in sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys())):
                sol = get_solutions_for_problem(title, enforce_signature=False)
                valid = False
                missing_str = ""
                err_sample = ""
                if sol and (sol.get("approaches") or []):
                    valid, errs = validate_solution(sol)
                    missing_per = get_missing_languages_per_approach(sol) if not valid else {}
                    missing_str = "; ".join(f"app{i}:{','.join(l)}" for i, l in sorted(missing_per.items()))
                    err_sample = "; ".join(errs[:3]) if errs else ""
                w.writerow([title, valid, missing_str, err_sample])
        print(f"\nWrote {out_path}")

    return 0 if missing_count == 0 and (not comp_fail or not args.compile) else 1


if __name__ == "__main__":
    sys.exit(main())
