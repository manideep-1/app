#!/usr/bin/env python3
"""
Execute Solution-tab code against problem test cases.

Default scope:
- Uses MongoDB problems collection (real stored test cases).
- Runs every approach/language pair that has both:
  1) solution code in get_solutions_for_problem(title)
  2) runnable starter+driver contract on that problem
"""
from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models import Language, TestCase  # noqa: E402
from code_executor import CodeExecutor  # noqa: E402
from seed_solutions import get_solutions_for_problem  # noqa: E402
from signature_contract import LANG_CODE_KEY  # noqa: E402


REQUIRED_LANGS = ("python", "javascript", "java", "cpp", "go", "csharp", "typescript")


def _contract_ready(problem: dict, lang: str) -> bool:
    starter = (problem.get(f"starter_code_{lang}") or "").strip()
    driver = (problem.get(f"driver_code_{lang}") or "").strip()
    return bool(starter and driver)


def _compose_full_code(problem: dict, solution_code: str, lang: str) -> str:
    user_code = (solution_code or "").strip()
    driver = (problem.get(f"driver_code_{lang}") or "").strip()
    if not driver:
        return user_code
    if lang == "go" and "___USER_CODE___" in driver:
        return driver.replace("___USER_CODE___", user_code)
    return user_code + "\n\n" + driver


def _to_testcases(rows: List[dict]) -> List[TestCase]:
    out: List[TestCase] = []
    for r in rows or []:
        try:
            out.append(
                TestCase(
                    input=r.get("input", ""),
                    expected_output=r.get("expected_output", ""),
                    is_hidden=bool(r.get("is_hidden", False)),
                )
            )
        except Exception:
            continue
    return out


async def _load_problems(db) -> List[dict]:
    projection = {
        "_id": 0,
        "id": 1,
        "title": 1,
        "test_cases": 1,
    }
    for lang in REQUIRED_LANGS:
        projection[f"starter_code_{lang}"] = 1
        projection[f"driver_code_{lang}"] = 1
    return await db.problems.find({}, projection).to_list(length=None)


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--problem-limit", type=int, default=0, help="Limit number of problems (0 = all)")
    parser.add_argument(
        "--all-approaches",
        action="store_true",
        help="Run every approach code (slower). Default runs first available approach per language.",
    )
    parser.add_argument(
        "--strict-missing-contract",
        action="store_true",
        help="Treat missing language contract/code as failures.",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Missing MONGO_URL or DB_NAME in backend/.env")
        return 1

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    problems = await _load_problems(db)
    problems = sorted(problems, key=lambda p: (p.get("title") or "").lower())
    if args.problem_limit and args.problem_limit > 0:
        problems = problems[: args.problem_limit]

    executor = CodeExecutor()

    executed = 0
    passed = 0
    failed: List[str] = []
    missing: List[str] = []

    for problem in problems:
        title = problem.get("title") or ""
        solutions = get_solutions_for_problem(title, enforce_signature=True)
        approaches = (solutions or {}).get("approaches") or []
        if not approaches:
            if args.strict_missing_contract:
                missing.append(f"{title} | no approaches")
            continue
        tcs = _to_testcases(problem.get("test_cases") or [])
        if not tcs:
            if args.strict_missing_contract:
                missing.append(f"{title} | no test cases")
            continue

        run_items: List[Tuple[str, str, str]] = []
        if args.all_approaches:
            for idx, approach in enumerate(approaches):
                app_title = (approach or {}).get("title") or f"Approach {idx + 1}"
                for lang in REQUIRED_LANGS:
                    code_key = LANG_CODE_KEY[lang]
                    code = (approach or {}).get(code_key)
                    if code:
                        run_items.append((app_title, lang, code))
        else:
            # Fast path: one official code per language (first available approach).
            for lang in REQUIRED_LANGS:
                code_key = LANG_CODE_KEY[lang]
                picked = None
                picked_title = ""
                for idx, approach in enumerate(approaches):
                    code = (approach or {}).get(code_key)
                    if code:
                        picked = code
                        picked_title = (approach or {}).get("title") or f"Approach {idx + 1}"
                        break
                if picked:
                    run_items.append((picked_title, lang, picked))

        for app_title, lang, code in run_items:
            if not _contract_ready(problem, lang):
                if args.strict_missing_contract:
                    missing.append(f"{title} | {app_title} | {lang} | no starter/driver contract")
                continue

            full_code = _compose_full_code(problem, code, lang)
            try:
                result = executor.execute_code(full_code, Language(lang), tcs, visible_only=False)
            except Exception as exc:
                executed += 1
                failed.append(f"{title} | {app_title} | {lang} | exception: {exc}")
                continue

            executed += 1
            status_obj = result.get("status")
            status_val = status_obj.value if hasattr(status_obj, "value") else str(status_obj)
            if status_val == "accepted" and result.get("passed") == result.get("total"):
                passed += 1
            else:
                failed.append(
                    f"{title} | {app_title} | {lang} | status={status_val} passed={result.get('passed')}/{result.get('total')}"
                )

    print("Execution validation report")
    print(f"Problems scanned: {len(problems)}")
    print(f"Executed runs: {executed}")
    print(f"Passed runs: {passed}")
    print(f"Failed runs: {len(failed)}")
    print(f"Missing contract/code entries: {len(missing)}")
    if failed:
        print("\nSample failures:")
        for row in failed[:40]:
            print(" -", row)
    if missing:
        print("\nSample missing entries:")
        for row in missing[:40]:
            print(" -", row)

    if failed:
        return 1
    if args.strict_missing_contract and missing:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

