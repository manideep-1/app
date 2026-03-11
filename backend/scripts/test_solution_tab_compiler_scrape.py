#!/usr/bin/env python3
"""
Simulate "copy from Solution tab -> paste in compiler Run" for all problems.

What this script does:
1) Loads every problem from MongoDB.
2) Fetches Solution-tab approaches via get_solutions_for_problem(title).
3) Picks solution code per UI language (first available approach by default).
4) Applies the same metadata+driver path used by Run endpoint.
5) Executes against visible test cases only (same as compiler Run behavior).

Run:
  python scripts/test_solution_tab_compiler_scrape.py
  python scripts/test_solution_tab_compiler_scrape.py --languages python,java
  python scripts/test_solution_tab_compiler_scrape.py --all-approaches
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from code_executor import CodeExecutor  # noqa: E402
from models import Language, ProblemFunctionMetadata, TestCase  # noqa: E402
from seed_solutions import get_solutions_for_problem  # noqa: E402
from server import _ensure_problem_execution_metadata, build_full_code  # noqa: E402
from signature_validator import validate_signature  # noqa: E402


UI_LANG_ORDER = ["python", "java", "cpp", "javascript", "go", "csharp"]
LANG_TO_CODE_KEY = {
    "python": "code_python",
    "java": "code_java",
    "cpp": "code_cpp",
    "javascript": "code_javascript",
    "go": "code_go",
    "csharp": "code_csharp",
}


def _parse_langs(raw: str) -> List[str]:
    out = []
    for part in (raw or "").split(","):
        lang = part.strip().lower()
        if lang and lang in LANG_TO_CODE_KEY and lang not in out:
            out.append(lang)
    return out


def _to_visible_tcs(rows: List[dict]) -> List[TestCase]:
    out: List[TestCase] = []
    for row in rows or []:
        if row.get("is_hidden"):
            continue
        try:
            out.append(
                TestCase(
                    input=row.get("input", ""),
                    expected_output=row.get("expected_output", ""),
                    is_hidden=False,
                )
            )
        except Exception:
            continue
    return out


def _status_value(status_obj) -> str:
    return status_obj.value if hasattr(status_obj, "value") else str(status_obj)


def _pick_run_items(approaches: List[dict], lang: str, all_approaches: bool) -> List[Tuple[str, str]]:
    key = LANG_TO_CODE_KEY[lang]
    out: List[Tuple[str, str]] = []
    for idx, app in enumerate(approaches):
        if not isinstance(app, dict):
            continue
        if lang == "python":
            code = (app.get("code_python") or app.get("code") or "").strip()
        else:
            code = (app.get(key) or "").strip()
        if not code:
            continue
        title = (app.get("title") or f"Approach {idx + 1}").strip()
        out.append((title, code))
        if not all_approaches:
            break
    return out


async def _load_problems(db, limit: int) -> List[dict]:
    projection = {
        "_id": 0,
        "id": 1,
        "title": 1,
        "test_cases": 1,
        "function_metadata": 1,
        "starter_code_python": 1,
        "starter_code_javascript": 1,
        "starter_code_java": 1,
        "starter_code_cpp": 1,
        "starter_code_c": 1,
        "starter_code_go": 1,
        "starter_code_csharp": 1,
        "starter_code_typescript": 1,
        "driver_code_python": 1,
        "driver_code_javascript": 1,
        "driver_code_java": 1,
        "driver_code_cpp": 1,
        "driver_code_c": 1,
        "driver_code_go": 1,
        "driver_code_csharp": 1,
        "driver_code_typescript": 1,
    }
    rows = await db.problems.find({}, projection).to_list(length=None)
    rows = sorted(rows, key=lambda p: (p.get("title") or "").lower())
    if limit > 0:
        rows = rows[:limit]
    return rows


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--languages", default="python,java,cpp,javascript,go,csharp")
    parser.add_argument("--problem-limit", type=int, default=0, help="0 = all")
    parser.add_argument("--all-approaches", action="store_true")
    parser.add_argument(
        "--report-json",
        default="",
        help="Optional path to write machine-readable report JSON.",
    )
    args = parser.parse_args()

    langs = _parse_langs(args.languages)
    if not langs:
        print("No valid languages selected. Choose from: " + ", ".join(UI_LANG_ORDER))
        return 1

    load_dotenv(ROOT / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Missing MONGO_URL or DB_NAME in backend/.env")
        return 1

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    problems = await _load_problems(db, args.problem_limit)

    executor = CodeExecutor()
    runs_total = 0
    runs_passed = 0
    missing_code = 0
    signature_rejected = 0
    no_visible_tests = 0
    failures: List[Dict[str, str]] = []

    for idx, problem in enumerate(problems, start=1):
        title = problem.get("title") or ""
        pid = problem.get("id") or ""
        approaches = (get_solutions_for_problem(title, enforce_signature=True) or {}).get("approaches") or []
        if not isinstance(approaches, list):
            approaches = []
        _ensure_problem_execution_metadata(problem)
        visible_tcs = _to_visible_tcs(problem.get("test_cases") or [])
        if not visible_tcs:
            no_visible_tests += 1
            failures.append(
                {
                    "problem_id": pid,
                    "title": title,
                    "approach": "",
                    "language": "",
                    "reason": "no visible test cases",
                }
            )
            continue

        metadata_obj = None
        meta = problem.get("function_metadata")
        if isinstance(meta, dict):
            try:
                metadata_obj = ProblemFunctionMetadata(**meta)
            except Exception:
                metadata_obj = None

        for lang in langs:
            run_items = _pick_run_items(approaches, lang, args.all_approaches)
            if not run_items:
                missing_code += 1
                failures.append(
                    {
                        "problem_id": pid,
                        "title": title,
                        "approach": "",
                        "language": lang,
                        "reason": "no solution code in selected language",
                    }
                )
                continue

            for approach_title, code in run_items:
                runs_total += 1

                if metadata_obj is not None:
                    ok, err = validate_signature(code, Language(lang), metadata_obj)
                    if not ok:
                        signature_rejected += 1
                        failures.append(
                            {
                                "problem_id": pid,
                                "title": title,
                                "approach": approach_title,
                                "language": lang,
                                "reason": f"signature rejected: {err or 'invalid signature'}",
                            }
                        )
                        continue

                full_code = build_full_code(problem, code, lang)
                try:
                    result = executor.execute_code(full_code, Language(lang), visible_tcs, visible_only=False)
                except Exception as exc:
                    failures.append(
                        {
                            "problem_id": pid,
                            "title": title,
                            "approach": approach_title,
                            "language": lang,
                            "reason": f"execution exception: {exc}",
                        }
                    )
                    continue

                status_val = _status_value(result.get("status"))
                if status_val == "accepted" and result.get("passed") == result.get("total"):
                    runs_passed += 1
                else:
                    failures.append(
                        {
                            "problem_id": pid,
                            "title": title,
                            "approach": approach_title,
                            "language": lang,
                            "reason": f"status={status_val} passed={result.get('passed')}/{result.get('total')}",
                        }
                    )

        if idx % 10 == 0:
            print(f"[{idx}/{len(problems)}] scanned | runs={runs_total} passed={runs_passed} failures={len(failures)}")

    report = {
        "problems_scanned": len(problems),
        "languages": langs,
        "all_approaches": bool(args.all_approaches),
        "runs_total": runs_total,
        "runs_passed": runs_passed,
        "runs_failed": max(0, runs_total - runs_passed),
        "missing_code_entries": missing_code,
        "signature_rejected": signature_rejected,
        "problems_with_no_visible_tests": no_visible_tests,
        "failures": failures,
    }

    print("\nSolution-tab -> Compiler run report")
    print(f"Problems scanned: {report['problems_scanned']}")
    print(f"Languages: {', '.join(langs)}")
    print(f"Total runs: {runs_total}")
    print(f"Passed runs: {runs_passed}")
    print(f"Failed runs: {report['runs_failed']}")
    print(f"Missing language code entries: {missing_code}")
    print(f"Signature rejected: {signature_rejected}")
    print(f"Problems with no visible tests: {no_visible_tests}")
    if failures:
        print("\nSample failures:")
        for f in failures[:60]:
            print(
                f" - {f.get('title')} | {f.get('approach') or '-'} | "
                f"{f.get('language') or '-'} | {f.get('reason')}"
            )

    if args.report_json:
        out_path = Path(args.report_json).resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        print(f"\nReport written: {out_path}")

    # Non-zero when we have any failed runs (user asked to test everything).
    return 1 if (runs_total == 0 or report["runs_failed"] > 0) else 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

