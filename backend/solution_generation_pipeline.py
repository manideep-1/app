"""
5-stage solution generation pipeline. No single-shot AI generation.

Stage 1: Structure only (patternRecognition, approaches with title/intuition/algorithm, dryRun, edgeCases, pitfalls). NO CODE.
Stage 2: Code per approach per language. Retry per language if missing.
Stage 3: Compilation validation. Regenerate that language only on failure.
Stage 4: Content validation (≥2 approaches, all languages, dry run, complexity). Regenerate missing sections only.
Stage 5: Final merge and return. Caller saves.

Critical: Never trust raw AI output. Never save unvalidated content. Never regenerate entire solution if only one language fails.
"""
from __future__ import annotations

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple

from solution_validator import (
    REQUIRED_LANGS,
    CODE_KEY_BY_LANG,
    validate_solution,
    get_validation_errors,
    get_missing_languages_for_approach,
    is_valid_code_snippet,
    MIN_CODE_LENGTH,
)

logger = logging.getLogger(__name__)

MIN_APPROACHES_REQUIRED = 2
STAGE2_MAX_RETRIES_PER_LANG = 4
STAGE3_MAX_RETRIES_PER_LANG = 2
CODE_MAX_TOKENS_ESTIMATE = 1500  # ~4 chars per token; cap response size


def _call_llm_structure(system: str, user: str, timeout: int = 30) -> str:
    """Call LLM with higher token limit for structure."""
    try:
        from ai.prompts import PROMPTS
        from ai.service import _get_llm_client
        import os
        client = _get_llm_client()
        if not client:
            return ""
        response = client.chat.completions.create(
            model=os.environ.get("AI_COACH_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system[:8000]},
                {"role": "user", "content": user[:12000]},
            ],
            max_tokens=2048,
            temperature=0.3,
            timeout=timeout,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        logger.warning("LLM structure call failed: %s", e)
        return ""


def _call_llm_code(system: str, user: str, timeout: int = 25) -> str:
    """Call LLM for code only."""
    try:
        from ai.service import _get_llm_client
        import os
        client = _get_llm_client()
        if not client:
            return ""
        response = client.chat.completions.create(
            model=os.environ.get("AI_COACH_MODEL", "gpt-4o-mini"),
            messages=[
                {"role": "system", "content": system[:6000]},
                {"role": "user", "content": user[:8000]},
            ],
            max_tokens=2048,
            temperature=0.2,
            timeout=timeout,
        )
        return (response.choices[0].message.content or "").strip()
    except Exception as e:
        logger.warning("LLM code call failed: %s", e)
        return ""


def _strip_code_block(text: str) -> str:
    """Remove markdown code fence if present."""
    if not text:
        return ""
    text = text.strip()
    for pattern in [r"^```(?:\w+)?\s*\n", r"\n```\s*$"]:
        text = re.sub(pattern, "", text)
    return text.strip()


def _parse_structure_json(raw: str) -> Optional[Dict[str, Any]]:
    """Parse JSON structure; reject if it contains code keys."""
    try:
        # Try to find JSON object
        start = raw.find("{")
        if start == -1:
            return None
        depth = 0
        end = -1
        for i in range(start, len(raw)):
            if raw[i] == "{":
                depth += 1
            elif raw[i] == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end == -1:
            return None
        obj = json.loads(raw[start:end])
        # Reject if any approach has code
        approaches = obj.get("approaches") or []
        for a in approaches:
            for key in list(a.keys()):
                if "code" in key.lower() or key in CODE_KEY_BY_LANG.values():
                    return None
        return obj
    except json.JSONDecodeError:
        return None


# ---------- Stage 1: Structure only ----------
def stage1_generate_structure(
    problem_title: str,
    problem_description: str,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Generate solution structure only. No code.
    Returns (structure_dict, errors). structure has patternRecognition, approaches[{title, intuition, algorithm}], dryRun, edgeCases, pitfalls.
    """
    from ai.prompts import PROMPTS
    system = PROMPTS.get("solution_structure_system", "")
    user = PROMPTS.get("solution_structure_user", "").format(
        title=problem_title,
        description=(problem_description or "")[:8000],
    )
    raw = _call_llm_structure(system, user)
    if not raw:
        return None, ["Stage 1: LLM returned empty"]
    obj = _parse_structure_json(raw)
    if not obj:
        return None, ["Stage 1: Invalid JSON or structure contained code"]
    approaches = obj.get("approaches") or []
    if len(approaches) < MIN_APPROACHES_REQUIRED:
        return None, [f"Stage 1: Need at least {MIN_APPROACHES_REQUIRED} approaches"]
    errors = []
    if not (obj.get("dryRun") or "").strip():
        errors.append("Stage 1: dryRun empty")
    if not (obj.get("edgeCases") or "").strip():
        errors.append("Stage 1: edgeCases empty")
    if not (obj.get("pitfalls") or "").strip():
        errors.append("Stage 1: pitfalls empty")
    if errors:
        return obj, errors
    return obj, []


# ---------- Stage 2: Code per approach per language ----------
def stage2_generate_code_for_cell(
    problem_title: str,
    approach_title: str,
    intuition: str,
    algorithm: str,
    language: str,
    signature_snippet: str,
) -> str:
    """Generate code for one (approach, language). Returns code string or empty."""
    from ai.prompts import PROMPTS
    system = PROMPTS.get("solution_code_system", "")
    user = PROMPTS.get("solution_code_user", "").format(
        title=problem_title,
        approach_title=approach_title,
        intuition=(intuition or "")[:1500],
        algorithm=(algorithm or "")[:1500],
        language=language,
        signature=signature_snippet[:2000],
    )
    raw = _call_llm_code(system, user)
    code = _strip_code_block(raw)
    if not code or len(code) < MIN_CODE_LENGTH:
        return ""
    if not is_valid_code_snippet(code):
        return ""
    return code


def stage2_generate_all_code(
    structure: Dict[str, Any],
    problem_title: str,
    get_signature_for_lang,
) -> Tuple[Dict[Tuple[int, str], str], List[str]]:
    """
    get_signature_for_lang(lang) -> str (starter or signature snippet for that language).
    Returns (code_by_key, errors) where key = (approach_index, language).
    """
    code_by_key: Dict[Tuple[int, str], str] = {}
    errors = []
    approaches = structure.get("approaches") or []
    for idx, app in enumerate(approaches):
        title = app.get("title") or f"Approach {idx + 1}"
        intuition = app.get("intuition") or ""
        algorithm = app.get("algorithm") or ""
        for lang in REQUIRED_LANGS:
            sig = get_signature_for_lang(lang)
            if not sig:
                errors.append(f"No signature for {lang}")
                continue
            for attempt in range(STAGE2_MAX_RETRIES_PER_LANG + 1):
                code = stage2_generate_code_for_cell(
                    problem_title, title, intuition, algorithm, lang, sig,
                )
                if code and is_valid_code_snippet(code):
                    code_by_key[(idx, lang)] = code
                    break
                if attempt == STAGE2_MAX_RETRIES_PER_LANG:
                    errors.append(f"Approach {idx} ({title}) / {lang}: code generation failed after retries")
    return code_by_key, errors


# ---------- Stage 3: Compilation validation ----------
def stage3_validate_compilation(
    code_by_key: Dict[Tuple[int, str], str],
    problem: Dict[str, Any],
    code_executor,
) -> Tuple[Dict[Tuple[int, str], str], List[Tuple[int, str]]]:
    """
    Run each (approach_idx, lang) code with problem driver and one test case.
    Returns (code_by_key_with_fixes, list of (approach_idx, lang) that still failed).
    """
    from models import Language, TestCase
    drivers = {lang: (problem.get(f"driver_code_{lang}") or "").strip() for lang in REQUIRED_LANGS}
    test_cases = problem.get("test_cases") or []
    tcs = []
    for r in test_cases[:1]:
        try:
            tcs.append(TestCase(
                input=r.get("input", ""),
                expected_output=r.get("expected_output", ""),
                is_hidden=bool(r.get("is_hidden", False)),
            ))
        except Exception:
            pass
    if not tcs:
        return code_by_key, list(code_by_key.keys())
    failed: List[Tuple[int, str]] = []
    for (idx, lang), code in list(code_by_key.items()):
        driver = drivers.get(lang) or ""
        if lang == "go" and "___USER_CODE___" in driver:
            full = driver.replace("___USER_CODE___", code)
        else:
            full = (code + "\n\n" + driver) if driver else code
        try:
            result = code_executor.execute_code(full, Language(lang), tcs, visible_only=False)
        except Exception:
            failed.append((idx, lang))
            continue
        status = result.get("status")
        status_val = status.value if hasattr(status, "value") else str(status)
        if status_val not in ("accepted",) or result.get("passed", 0) < result.get("total", 0):
            failed.append((idx, lang))
    return code_by_key, failed


# ---------- Stage 4: Content validation ----------
def stage4_validate_content(
    merged_solution: Dict[str, Any],
    *,
    require_all_languages: bool = True,
) -> Tuple[bool, List[str]]:
    """At least 2 approaches; optionally all languages per approach; dry run; complexity. Uses solution_validator."""
    approaches = merged_solution.get("approaches") or []
    errors = list(get_validation_errors(merged_solution, require_all_languages=require_all_languages))
    if len(approaches) < MIN_APPROACHES_REQUIRED:
        errors.append(f"Need at least {MIN_APPROACHES_REQUIRED} approaches")
    if not (merged_solution.get("dry_run") or "").strip():
        errors.append("dry_run missing or empty")
    for i, app in enumerate(approaches):
        if not (app.get("complexity") or "").strip():
            errors.append(f"Approach {i + 1} ({app.get('title')}): complexity missing")
    valid = len(errors) == 0
    return valid, errors


# ---------- Stage 5: Merge ----------
def stage5_merge(
    structure: Dict[str, Any],
    code_by_key: Dict[Tuple[int, str], str],
    complexity_by_approach: Optional[Dict[int, str]] = None,
) -> Dict[str, Any]:
    """
    Combine structure + code per language + optional complexity per approach.
    structure has patternRecognition, approaches (title, intuition, algorithm), dryRun, edgeCases, pitfalls.
    """
    approaches = list(structure.get("approaches") or [])
    complexity_by_approach = complexity_by_approach or {}
    out_approaches = []
    for idx, app in enumerate(approaches):
        entry = {
            "title": app.get("title") or f"Approach {idx + 1}",
            "intuition": (app.get("intuition") or "").strip(),
            "algorithm": (app.get("algorithm") or "").strip(),
            "complexity": (complexity_by_approach.get(idx) or app.get("complexity") or "").strip() or "See approach.",
        }
        for lang in REQUIRED_LANGS:
            key = CODE_KEY_BY_LANG.get(lang, f"code_{lang}")
            entry[key] = code_by_key.get((idx, lang), "").strip()
        out_approaches.append(entry)
    return {
        "pattern_recognition": (structure.get("patternRecognition") or structure.get("pattern_recognition") or "").strip(),
        "approaches": out_approaches,
        "dry_run": (structure.get("dryRun") or structure.get("dry_run") or "").strip(),
        "edge_cases": (structure.get("edgeCases") or structure.get("edge_cases") or "").strip(),
        "common_pitfalls": (structure.get("pitfalls") or structure.get("common_pitfalls") or "").strip(),
    }


# ---------- Full pipeline ----------
def run_pipeline(
    problem: Dict[str, Any],
    code_executor,
    *,
    skip_compilation: bool = False,
    max_compilation_retries: int = 2,
    return_merged_on_validation_fail: bool = False,
) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """
    Run all 5 stages. problem must have title, description, function_metadata (or we use registry),
    test_cases, and driver_code_* (or we generate from metadata).
    Returns (final_solution_dict, errors). If errors non-empty, do not save.
    """
    errors: List[str] = []
    title = (problem.get("title") or "").strip()
    description = (problem.get("description") or "").strip()
    if not title:
        return None, ["problem.title required"]

    # Resolve metadata and drivers
    meta = problem.get("function_metadata")
    if not meta or not isinstance(meta, dict):
        try:
            from problem_metadata_registry import get_metadata
            entry = get_metadata(title)
            if entry:
                meta = entry[0].model_dump() if hasattr(entry[0], "model_dump") else entry[0]
        except Exception:
            pass
    if not meta:
        # Fallback for unregistered problems: infer metadata from starter/code signatures.
        try:
            from seed_solutions import get_solutions_for_problem, _infer_alignment_metadata
            existing = get_solutions_for_problem(title, enforce_signature=False) or {}
            inferred = _infer_alignment_metadata(title, existing.get("approaches") or [])
            if inferred is not None:
                meta = inferred.model_dump() if hasattr(inferred, "model_dump") else inferred
        except Exception:
            pass
    if not meta:
        return None, ["function_metadata not found for problem"]

    from models import ProblemFunctionMetadata
    from starter_template_generator import generate_starter, generate_starter_and_driver
    metadata = ProblemFunctionMetadata(**meta) if isinstance(meta, dict) else meta
    input_spec = [{"name": p.name, "type": p.type or ""} for p in (metadata.parameters or [])]
    generated = generate_starter_and_driver(metadata, input_spec)
    for k, v in (generated or {}).items():
        if v and not problem.get(k):
            problem[k] = v

    def get_signature_for_lang(lang: str) -> str:
        return (generate_starter(metadata, lang) or "").strip()

    # Stage 1
    structure, stage1_errs = stage1_generate_structure(title, description)
    if not structure:
        return None, ["Stage 1 failed"] + (stage1_errs or ["Unknown"])
    if stage1_errs:
        errors.extend(["Stage 1 warnings: " + "; ".join(stage1_errs)])

    # Stage 2
    code_by_key, stage2_errs = stage2_generate_all_code(structure, title, get_signature_for_lang)
    if stage2_errs:
        errors.extend(stage2_errs)
    missing = [(i, lang) for i in range(len(structure.get("approaches") or [])) for lang in REQUIRED_LANGS if (i, lang) not in code_by_key]
    if missing:
        return None, ["Stage 2: missing code for " + str(missing[:10])] + errors

    # Stage 3
    if not skip_compilation and code_executor:
        for _ in range(max_compilation_retries + 1):
            code_by_key, failed = stage3_validate_compilation(code_by_key, problem, code_executor)
            if not failed:
                break
            for (idx, lang) in failed:
                sig = get_signature_for_lang(lang)
                app = (structure.get("approaches") or [])[idx] if idx < len(structure.get("approaches") or []) else {}
                code = stage2_generate_code_for_cell(
                    title,
                    app.get("title") or f"Approach {idx + 1}",
                    app.get("intuition") or "",
                    app.get("algorithm") or "",
                    lang,
                    sig,
                )
                if code:
                    code_by_key[(idx, lang)] = code
        _, still_failed = stage3_validate_compilation(code_by_key, problem, code_executor)
        if still_failed:
            errors.append("Stage 3: compilation failed for " + str(still_failed[:5]))

    # Stage 5 merge (before Stage 4 so we validate merged)
    merged = stage5_merge(structure, code_by_key)

    # Stage 4
    valid, content_errors = stage4_validate_content(merged)
    if not valid:
        errors.extend(content_errors)
        if return_merged_on_validation_fail:
            return merged, errors
        return None, errors

    if errors:
        return merged, errors
    return merged, []


def run_pipeline_sync(problem: Dict[str, Any], code_executor, **kwargs) -> Tuple[Optional[Dict[str, Any]], List[str]]:
    """Synchronous entry point (e.g. from script)."""
    return run_pipeline(problem, code_executor, **kwargs)
