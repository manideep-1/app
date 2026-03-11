#!/usr/bin/env python3
"""
Repair failing Solution-tab -> Compiler entries by regenerating failing code cells.

Targets:
- Python failures from a full all-approaches report.
- JavaScript failures from a first-approach report.

The script:
1) Loads failing (title, approach, language) cells from reports.
2) Re-validates each current cell against visible test cases.
3) Tries fast fallback (reuse a passing sibling approach in same language).
4) Uses the LLM to regenerate code for unresolved cells with strict contract context.
5) Writes per-problem overrides to backend/generated_solutions/<slug>.json.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
from pathlib import Path
import re
import sys
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import seed_solutions
from ai.service import _get_llm_client
from code_executor import CodeExecutor
from models import Language, ProblemFunctionMetadata, TestCase
from seed_solutions import get_solutions_for_problem
from server import _ensure_problem_execution_metadata, build_full_code
from signature_contract import align_solution_code_to_metadata
from signature_validator import validate_signature


LANG_TO_CODE_KEY = {
    "python": "code_python",
    "javascript": "code_javascript",
}


def _slug(title: str) -> str:
    return re.sub(r"[^\w\-]", "_", (title or "").strip())[:80]


def _strip_code_block(text: str) -> str:
    raw = (text or "").strip()
    if not raw:
        return ""
    if "```" not in raw:
        return raw
    # Keep first fenced block body if present.
    m = re.search(r"```(?:\w+)?\s*\n([\s\S]*?)\n```", raw)
    if m:
        return (m.group(1) or "").strip()
    return raw.replace("```", "").strip()


def _status_value(status_obj) -> str:
    return status_obj.value if hasattr(status_obj, "value") else str(status_obj)


def _visible_test_cases(problem: dict) -> List[TestCase]:
    out: List[TestCase] = []
    for row in problem.get("test_cases") or []:
        if row.get("is_hidden"):
            continue
        out.append(
            TestCase(
                input=row.get("input", ""),
                expected_output=row.get("expected_output", ""),
                is_hidden=False,
            )
        )
    return out


def _metadata_obj(problem: dict) -> Optional[ProblemFunctionMetadata]:
    meta = problem.get("function_metadata")
    if not isinstance(meta, dict):
        return None
    try:
        return ProblemFunctionMetadata(**meta)
    except Exception:
        return None


def _load_report_failures(path: Path, expected_lang: str) -> List[Tuple[str, str, str]]:
    if not path.exists():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    out: List[Tuple[str, str, str]] = []
    for row in payload.get("failures") or []:
        title = (row.get("title") or "").strip()
        approach = (row.get("approach") or "").strip()
        lang = (row.get("language") or "").strip().lower()
        if not title or lang != expected_lang:
            continue
        if not approach:
            continue
        out.append((title, approach, lang))
    return out


def _find_approach_index(approaches: List[dict], approach_title: str) -> int:
    target = (approach_title or "").strip().lower()
    for i, app in enumerate(approaches):
        if ((app.get("title") or "").strip().lower()) == target:
            return i
    return -1


def _first_failure_detail(result: dict) -> str:
    tests = result.get("test_results") or []
    for row in tests:
        if row.get("passed"):
            continue
        inp = (row.get("input") or "")[:180]
        exp = (row.get("expected") or "")[:180]
        got = (row.get("output") or "")[:300]
        return f"input={inp!r} expected={exp!r} got={got!r}"
    return ""


def _contains_forbidden_io(code: str, lang: str) -> bool:
    src = (code or "").lower()
    if not src:
        return True
    if lang == "python":
        blocked = (
            "if __name__",
            "sys.stdin",
            "input(",
            "print(",
        )
    else:
        blocked = (
            "process.stdin",
            "readline",
            "console.log",
            "require('fs')",
            'require("fs")',
        )
    return any(token in src for token in blocked)


def _evaluate_cell(
    executor: CodeExecutor,
    problem: dict,
    metadata: Optional[ProblemFunctionMetadata],
    visible_tcs: List[TestCase],
    lang: str,
    code: str,
) -> Tuple[bool, str, str]:
    raw = (code or "").strip()
    if not raw:
        return False, "", "empty code"

    aligned = raw
    if metadata is not None:
        try:
            aligned = align_solution_code_to_metadata(raw, lang, metadata) or raw
        except Exception:
            aligned = raw

    if metadata is not None:
        ok, err = validate_signature(aligned, Language(lang), metadata)
        if not ok:
            return False, aligned, f"signature rejected: {err or 'invalid signature'}"

    full = build_full_code(problem, aligned, lang)
    try:
        result = executor.execute_code(full, Language(lang), visible_tcs, visible_only=False)
    except Exception as exc:
        return False, aligned, f"execution exception: {exc}"

    status_val = _status_value(result.get("status"))
    passed = result.get("passed", 0)
    total = result.get("total", 0)
    if status_val == "accepted" and passed == total:
        return True, aligned, "accepted"

    detail = _first_failure_detail(result)
    if detail:
        return False, aligned, f"status={status_val} passed={passed}/{total}; {detail}"
    return False, aligned, f"status={status_val} passed={passed}/{total}"


def _llm_generate_code(
    llm_client,
    model: str,
    lang: str,
    problem: dict,
    approach: dict,
    starter: str,
    driver: str,
    current_code: str,
    last_failure: str,
    visible_tcs: List[TestCase],
    temperature: float,
) -> str:
    lang_label = "Python" if lang == "python" else "JavaScript"
    required_callable = ""
    meta = _metadata_obj(problem)
    if meta and getattr(meta, "function_name", None):
        required_callable = str(meta.function_name).strip()

    tests_preview = []
    for i, tc in enumerate(visible_tcs[:2], start=1):
        tests_preview.append(
            f"Test {i} input:\n{tc.input}\nExpected output:\n{tc.expected_output}\n"
        )
    tests_blob = "\n".join(tests_preview)

    system = (
        "You fix coding-problem solution snippets.\n"
        "Return ONLY runnable code in the target language.\n"
        "Do not include markdown fences or explanations.\n"
        "Return ONLY the solution callable (function/class) with helpers.\n"
        "Never include top-level execution code.\n"
        "Never read from stdin and never print/log.\n"
        "Do not use process.stdin/readline/console.log/input()/sys.stdin/print().\n"
        "Define the exact callable expected by the starter signature.\n"
        "The starter signature is the ONLY contract of truth; ignore usual LeetCode signatures when they differ."
    )

    user = (
        f"Language: {lang_label}\n"
        f"Problem title: {problem.get('title')}\n\n"
        "IMPORTANT CONTRACT RULES:\n"
        "1) Follow the starter callable exactly.\n"
        "2) No stdin/stdout usage.\n"
        "3) Return values only; the platform prints them.\n"
        "4) Handle empty/edge input safely.\n\n"
        f"Problem description (context only):\n{(problem.get('description') or '')[:1800]}\n\n"
        f"Approach title: {(approach.get('title') or '').strip()}\n"
        f"Approach intuition:\n{(approach.get('intuition') or '')[:700]}\n\n"
        f"Approach algorithm:\n{(approach.get('algorithm') or '')[:700]}\n\n"
        f"Required callable name: {required_callable or '(infer from starter)'}\n"
        f"Starter contract (must match):\n{starter[:1800]}\n\n"
        f"Driver behavior (for input/output understanding):\n{driver[:2200]}\n\n"
        f"Visible tests:\n{tests_blob[:2200]}\n"
        f"Previous failure:\n{last_failure[:1200]}\n\n"
        f"Current failing code:\n{current_code[:3500]}\n\n"
        "Return corrected code now. Again: no stdin, no prints/logs, no main block.\n"
        "If starter has a single `data` parameter, parse inputs from that `data` value inside the function."
    )

    resp = llm_client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        max_tokens=2200,
        temperature=max(0.0, min(1.0, temperature)),
        timeout=45,
    )
    return _strip_code_block((resp.choices[0].message.content or "").strip())


def _save_override(title: str, solution_payload: dict) -> Path:
    out_dir = ROOT / "generated_solutions"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{_slug(title)}.json"
    path.write_text(json.dumps(solution_payload, indent=2), encoding="utf-8")
    # Invalidate in-process cache so subsequent lookups reflect edits.
    try:
        seed_solutions._GENERATED_SOLUTIONS_CACHE.pop(title, None)
    except Exception:
        pass
    return path


async def _load_problem_map(db) -> Dict[str, dict]:
    projection = {
        "_id": 0,
        "id": 1,
        "title": 1,
        "description": 1,
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
    return {row.get("title"): row for row in rows if row.get("title")}


async def main() -> int:
    parser = argparse.ArgumentParser(description="Repair failing solution-tab compiler cells.")
    parser.add_argument(
        "--python-report",
        default=str(ROOT / "generated_solutions" / "solution_tab_compiler_test_python_all_approaches_after_contract_fix.json"),
    )
    parser.add_argument(
        "--javascript-report",
        default=str(ROOT / "generated_solutions" / "solution_tab_compiler_test_javascript_after_contract_fix.json"),
    )
    parser.add_argument("--attempts", type=int, default=4, help="LLM attempts per failing cell")
    parser.add_argument(
        "--temperature",
        type=float,
        default=0.2,
        help="Base LLM temperature for regeneration (increases slightly per attempt).",
    )
    parser.add_argument("--max-cells", type=int, default=0, help="Limit repaired cells (0=all)")
    parser.add_argument("--titles", type=str, default="", help="Comma-separated title allowlist")
    parser.add_argument(
        "--report-out",
        default=str(ROOT / "generated_solutions" / "repair_solution_tab_failures_report.json"),
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    mongo_url = os.environ.get("MONGO_URL")
    db_name = os.environ.get("DB_NAME")
    if not mongo_url or not db_name:
        print("Missing MONGO_URL or DB_NAME in backend/.env")
        return 1

    llm_client = _get_llm_client()
    if llm_client is None:
        print("OpenAI client unavailable (set OPENAI_API_KEY).")
        return 1
    model = os.environ.get("AI_COACH_MODEL", "gpt-4o-mini")

    py_failures = _load_report_failures(Path(args.python_report), "python")
    js_failures = _load_report_failures(Path(args.javascript_report), "javascript")
    targets = sorted(set(py_failures + js_failures), key=lambda x: (x[0].lower(), x[2], x[1].lower()))

    if args.titles.strip():
        allowed = {t.strip() for t in args.titles.split(",") if t.strip()}
        targets = [row for row in targets if row[0] in allowed]

    if args.max_cells and args.max_cells > 0:
        targets = targets[: args.max_cells]

    print(f"[repair] target cells: {len(targets)}")

    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    problems = await _load_problem_map(db)
    executor = CodeExecutor()

    fixed = 0
    already_passing = 0
    unresolved: List[dict] = []
    modified_titles: set[str] = set()
    solution_cache: Dict[str, dict] = {}
    solved_by_title_lang: Dict[Tuple[str, str], str] = {}

    for idx, (title, approach_title, lang) in enumerate(targets, start=1):
        problem = problems.get(title)
        if not problem:
            unresolved.append(
                {
                    "title": title,
                    "approach": approach_title,
                    "language": lang,
                    "reason": "problem_not_found",
                }
            )
            continue

        _ensure_problem_execution_metadata(problem)
        metadata = _metadata_obj(problem)
        visible_tcs = _visible_test_cases(problem)
        if not visible_tcs:
            unresolved.append(
                {
                    "title": title,
                    "approach": approach_title,
                    "language": lang,
                    "reason": "no_visible_tests",
                }
            )
            continue

        solution_payload = solution_cache.get(title)
        if solution_payload is None:
            solution_payload = get_solutions_for_problem(title, enforce_signature=False) or {}
            solution_cache[title] = solution_payload

        approaches = solution_payload.get("approaches") or []
        if not approaches:
            unresolved.append(
                {
                    "title": title,
                    "approach": approach_title,
                    "language": lang,
                    "reason": "no_approaches",
                }
            )
            continue

        app_idx = _find_approach_index(approaches, approach_title)
        if app_idx < 0:
            unresolved.append(
                {
                    "title": title,
                    "approach": approach_title,
                    "language": lang,
                    "reason": "approach_not_found",
                }
            )
            continue

        code_key = LANG_TO_CODE_KEY[lang]
        app = approaches[app_idx]
        title_lang_key = (title, lang)
        previous_code = (app.get(code_key) or (app.get("code") if lang == "python" else "") or "")

        if title_lang_key in solved_by_title_lang:
            shared_code = solved_by_title_lang[title_lang_key]
            app[code_key] = shared_code
            if lang == "python":
                app["code"] = shared_code
            ok_shared, _, reason_shared = _evaluate_cell(
                executor, problem, metadata, visible_tcs, lang, shared_code
            )
            if ok_shared:
                fixed += 1
                modified_titles.add(title)
                _save_override(title, solution_payload)
                print(f"[{idx}/{len(targets)}] fixed(shared) {title} | {approach_title} | {lang}")
                continue
            # If shared code unexpectedly fails here, discard and continue with normal flow.
            solved_by_title_lang.pop(title_lang_key, None)
            app[code_key] = previous_code
            if lang == "python":
                app["code"] = previous_code
            print(f"[{idx}/{len(targets)}] shared-invalid {title} | {approach_title} | {lang} | {reason_shared[:120]}")

        current_code = (app.get(code_key) or (app.get("code") if lang == "python" else "") or "").strip()

        ok, aligned, reason = _evaluate_cell(executor, problem, metadata, visible_tcs, lang, current_code)
        if ok:
            already_passing += 1
            print(f"[{idx}/{len(targets)}] pass {title} | {approach_title} | {lang}")
            continue

        # Fast fallback: reuse a passing sibling approach in same language.
        sibling_fixed = False
        for j, sibling in enumerate(approaches):
            if j == app_idx:
                continue
            cand = (sibling.get(code_key) or (sibling.get("code") if lang == "python" else "") or "").strip()
            if not cand:
                continue
            cand_ok, cand_aligned, _ = _evaluate_cell(executor, problem, metadata, visible_tcs, lang, cand)
            if not cand_ok:
                continue
            app[code_key] = cand_aligned
            if lang == "python":
                app["code"] = cand_aligned
            solved_by_title_lang[title_lang_key] = cand_aligned
            for ap in approaches:
                ap[code_key] = cand_aligned
                if lang == "python":
                    ap["code"] = cand_aligned
            fixed += 1
            sibling_fixed = True
            modified_titles.add(title)
            _save_override(title, solution_payload)
            print(f"[{idx}/{len(targets)}] fixed(sibling) {title} | {approach_title} | {lang}")
            break

        if sibling_fixed:
            continue

        starter = (problem.get(f"starter_code_{lang}") or "").strip()
        driver = (problem.get(f"driver_code_{lang}") or "").strip()
        last_failure = reason
        cell_fixed = False

        for attempt in range(1, max(1, args.attempts) + 1):
            try:
                attempt_temp = min(0.8, max(0.0, args.temperature + (attempt - 1) * 0.1))
                generated = _llm_generate_code(
                    llm_client=llm_client,
                    model=model,
                    lang=lang,
                    problem=problem,
                    approach=app,
                    starter=starter,
                    driver=driver,
                    current_code=current_code,
                    last_failure=last_failure,
                    visible_tcs=visible_tcs,
                    temperature=attempt_temp,
                )
            except Exception as exc:
                generated = ""
                last_failure = f"llm_exception: {exc}"

            if not generated:
                continue

            if _contains_forbidden_io(generated, lang):
                last_failure = "generated_code_contains_forbidden_io_or_top_level_execution"
                current_code = generated
                continue

            ok2, aligned2, reason2 = _evaluate_cell(executor, problem, metadata, visible_tcs, lang, generated)
            if ok2:
                app[code_key] = aligned2
                if lang == "python":
                    app["code"] = aligned2
                solved_by_title_lang[title_lang_key] = aligned2
                for ap in approaches:
                    ap[code_key] = aligned2
                    if lang == "python":
                        ap["code"] = aligned2
                fixed += 1
                cell_fixed = True
                modified_titles.add(title)
                _save_override(title, solution_payload)
                print(f"[{idx}/{len(targets)}] fixed(llm:{attempt}) {title} | {approach_title} | {lang}")
                break
            last_failure = reason2
            current_code = generated

        if not cell_fixed:
            unresolved.append(
                {
                    "title": title,
                    "approach": approach_title,
                    "language": lang,
                    "reason": last_failure,
                }
            )
            print(f"[{idx}/{len(targets)}] fail {title} | {approach_title} | {lang} | {last_failure[:120]}")

    report = {
        "targets": len(targets),
        "fixed": fixed,
        "already_passing": already_passing,
        "unresolved_count": len(unresolved),
        "modified_titles": sorted(modified_titles),
        "unresolved": unresolved,
    }
    report_path = Path(args.report_out)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    print("\n[repair] summary")
    print(json.dumps({k: v for k, v in report.items() if k not in {"unresolved", "modified_titles"}}, indent=2))
    print(f"[repair] report: {report_path}")
    return 0 if len(unresolved) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

