#!/usr/bin/env python3
"""
Validate Solution/Starter/schema signature contract.

What it checks (for each problem and language):
1) Extract expected signature from schema.
2) Extract signature from starter generated from that schema.
3) Extract signature from Solution-tab code.
4) Compare function name, parameter order/names, and language types.

It prints two reports:
- BEFORE FIX: raw solution payloads (no schema alignment)
- AFTER FIX: schema-aligned solution payloads
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Allow imports when run from repo root or backend/
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from models import ProblemFunctionMetadata, ProblemFunctionParam, SUPPORTED_LANGUAGES
from seed_solutions import SOLUTIONS, RICH_SOLUTIONS, get_solutions_for_problem
from seed_starters import get_starters_for_problem
from problem_metadata_registry import get_metadata
from signature_contract import (
    REQUIRED_SIGNATURE_LANGS,
    LANG_CODE_KEY,
    extract_signature,
    metadata_signature,
    signatures_match,
)


def _first_non_empty(values: List[str], default: str = "") -> str:
    for v in values:
        if v and str(v).strip():
            return str(v).strip()
    return default


def _infer_schema_from_sources(title: str, approaches: List[dict]) -> Optional[ProblemFunctionMetadata]:
    # 1) Registry metadata is authoritative when available.
    entry = get_metadata(title)
    if entry is not None:
        return entry[0]

    starters = get_starters_for_problem(title) or {}
    signatures_by_lang: Dict[str, object] = {}
    for lang in REQUIRED_SIGNATURE_LANGS:
        skey = f"starter_code_{lang}"
        sig = extract_signature(starters.get(skey) or "", lang)
        if sig:
            signatures_by_lang[lang] = sig

    # Also use first approach code signatures as fallback signal.
    if approaches:
        first = approaches[0] if isinstance(approaches[0], dict) else {}
        for lang in REQUIRED_SIGNATURE_LANGS:
            ckey = LANG_CODE_KEY[lang]
            sig = extract_signature(first.get(ckey) or "", lang)
            if sig and lang not in signatures_by_lang:
                signatures_by_lang[lang] = sig

    if not signatures_by_lang:
        return None

    preferred = (
        signatures_by_lang.get("python")
        or signatures_by_lang.get("javascript")
        or signatures_by_lang.get("java")
        or next(iter(signatures_by_lang.values()))
    )
    if preferred is None:
        return None
    fn_name = preferred.function_name
    param_names = [p.name for p in preferred.params]

    # Build per-language return and param types from parsed signatures where available.
    return_type_by_language: Dict[str, str] = {}
    param_types_by_lang: List[Dict[str, str]] = [dict() for _ in param_names]
    for lang, sig in signatures_by_lang.items():
        if sig.return_type:
            return_type_by_language[lang] = sig.return_type
        for i, p in enumerate(sig.params):
            if i >= len(param_types_by_lang):
                break
            if p.type:
                param_types_by_lang[i][lang] = p.type

    # Canonical fallbacks.
    canonical_return = _first_non_empty(
        [
            return_type_by_language.get("python", ""),
            return_type_by_language.get("java", ""),
            return_type_by_language.get("cpp", ""),
            "int",
        ]
    )

    params: List[ProblemFunctionParam] = []
    for i, name in enumerate(param_names):
        typed = param_types_by_lang[i]
        canonical_param_type = _first_non_empty(
            [
                typed.get("python", ""),
                typed.get("java", ""),
                typed.get("cpp", ""),
                "int",
            ]
        )
        full_param_map = typed if all(lang in typed for lang in SUPPORTED_LANGUAGES) else None
        params.append(
            ProblemFunctionParam(
                name=name,
                type=canonical_param_type,
                type_by_language=full_param_map,
            )
        )

    full_return_map = return_type_by_language if all(lang in return_type_by_language for lang in SUPPORTED_LANGUAGES) else None

    return ProblemFunctionMetadata(
        function_name=fn_name,
        return_type=canonical_return,
        return_type_by_language=full_return_map,
        parameters=params,
    )


def _run_report(enforce_signature: bool) -> dict:
    titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    per_language_mismatches = {lang: 0 for lang in REQUIRED_SIGNATURE_LANGS}
    details = []
    problems_checked = 0

    for title in titles:
        data = get_solutions_for_problem(title, enforce_signature=enforce_signature)
        if not data:
            continue
        approaches = data.get("approaches") or []
        if not approaches:
            continue
        schema = _infer_schema_from_sources(title, approaches)
        if schema is None:
            continue
        problems_checked += 1

        for approach in approaches:
            for lang in REQUIRED_SIGNATURE_LANGS:
                code_key = LANG_CODE_KEY[lang]
                code = (approach or {}).get(code_key)
                if not code:
                    continue
                expected_sig = metadata_signature(schema, lang)
                starter_code = ""
                try:
                    from starter_template_generator import generate_starter

                    starter_code = generate_starter(schema, lang)
                except Exception:
                    starter_code = ""
                starter_sig = extract_signature(starter_code, lang) if starter_code else None
                solution_sig = extract_signature(code, lang)

                # Schema->starter check
                if expected_sig and starter_sig and not signatures_match(
                    expected_sig,
                    starter_sig,
                    strict_types=True,
                    strict_param_names=False,
                ):
                    per_language_mismatches[lang] += 1
                    details.append(
                        f"{title} | {approach.get('title','(untitled)')} | {lang} | starter mismatch vs schema"
                    )
                    continue

                # Schema->solution check
                if not expected_sig or not solution_sig or not signatures_match(
                    expected_sig,
                    solution_sig,
                    strict_types=True,
                    strict_param_names=False,
                ):
                    per_language_mismatches[lang] += 1
                    details.append(
                        f"{title} | {approach.get('title','(untitled)')} | {lang} | solution mismatch vs schema"
                    )

    total_mismatches = sum(per_language_mismatches.values())
    return {
        "problems_checked": problems_checked,
        "total_mismatches": total_mismatches,
        "per_language_mismatches": per_language_mismatches,
        "details": details,
    }


def _print_report(title: str, report: dict) -> None:
    print(title)
    print(f"Total problems checked: {report['problems_checked']}")
    print(f"Total mismatches: {report['total_mismatches']}")
    print("Per-language mismatch count:")
    for lang, count in report["per_language_mismatches"].items():
        print(f"  - {lang}: {count}")
    if report["details"]:
        print("Sample mismatches:")
        for row in report["details"][:30]:
            print(f"  - {row}")
    print("")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--fail-on-mismatch",
        action="store_true",
        help="Exit non-zero when AFTER report has any mismatches.",
    )
    args = parser.parse_args()

    before = _run_report(enforce_signature=False)
    after = _run_report(enforce_signature=True)

    _print_report("=== BEFORE FIX (raw solution signatures) ===", before)
    _print_report("=== AFTER FIX (schema-aligned solution signatures) ===", after)

    if args.fail_on_mismatch and after["total_mismatches"] > 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

