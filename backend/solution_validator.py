"""
Strict validation for solution content. No verbal-only or incomplete solutions.

A solution MUST NOT be saved or published unless validate_solution() returns valid=True.
See docs/SOLUTION_CONTENT_SCHEMA.md.
"""
import re
from typing import Any, Callable, Dict, List, Optional, Tuple

# All 6 supported languages required per approach (no empty code blocks)
REQUIRED_LANGS = ("java", "python", "cpp", "javascript", "go", "csharp")
CODE_KEY_BY_LANG = {
    "java": "code_java",
    "python": "code_python",
    "cpp": "code_cpp",
    "javascript": "code_javascript",
    "go": "code_go",
    "csharp": "code_csharp",
}

MIN_CODE_LENGTH = 50  # minimum characters per code block (reject stub/placeholder)
MIN_APPROACHES = 1
PLACEHOLDER_PATTERNS = [
    r"^\s*\.\.\.\s*$",   # line that is only "..."
    r"\bTODO\b",
    r"#\s*\.\.\.",       # # ...
    r"//\s*\.\.\.",      # // ...
    r"\.\.\.\s*$",       # ... at end of line
]
# Heuristic: code should contain at least one of these (real implementation)
SIGNATURE_PATTERNS = [
    r"\bdef\s+\w+\s*\(",       # Python
    r"\bfunction\s+\w+\s*\(",  # JavaScript
    r"\bpublic\s+\w+.*\s+\w+\s*\(",  # Java
    r"\w+\s+\w+\s*\([^)]*\)\s*\{",   # C++/JS/C# function
    r"\bfunc\s+\w+\s*\(",      # Go
    r"\bclass\s+\w+",          # Class-based (e.g. MinStack, Trie)
]


def _normalize_solution(solution: Dict[str, Any]) -> Dict[str, Any]:
    """Accept either full solution dict (with 'approaches') or list of approaches."""
    if isinstance(solution.get("approaches"), list):
        return solution
    if isinstance(solution, list):
        return {"approaches": solution}
    return {"approaches": []}


def _code_looks_like_placeholder(code: str) -> bool:
    """True if code is placeholder / pseudo-code only."""
    if not code or len(code.strip()) < MIN_CODE_LENGTH:
        return True
    for pat in PLACEHOLDER_PATTERNS:
        if re.search(pat, code, re.IGNORECASE):
            return True
    # Should look like real code (function/class)
    return not any(re.search(p, code) for p in SIGNATURE_PATTERNS)


def is_valid_code_snippet(code: str) -> bool:
    """True if code has minimum length and does not look like placeholder. Use in pipelines to accept only valid output."""
    if not code or len((code or "").strip()) < MIN_CODE_LENGTH:
        return False
    return not _code_looks_like_placeholder(code)


def get_missing_languages_for_approach(approach: Dict[str, Any]) -> List[str]:
    """Return list of language keys (e.g. 'java', 'python') missing or invalid for this approach."""
    missing = []
    for lang in REQUIRED_LANGS:
        key = CODE_KEY_BY_LANG[lang]
        raw = approach.get(key)
        if (not raw) and isinstance(approach.get("code"), dict):
            raw = approach.get("code", {}).get(lang)
        val = (raw or "").strip()
        if not val or len(val) < MIN_CODE_LENGTH:
            missing.append(lang)
        elif _code_looks_like_placeholder(val):
            missing.append(lang)
    return missing


def get_validation_errors(
    solution: Dict[str, Any],
    *,
    require_all_languages: bool = True,
    min_code_length: int = MIN_CODE_LENGTH,
    reject_placeholders: bool = True,
) -> List[str]:
    """
    Run all validation checks. Returns list of error messages (empty if valid).
    """
    errors: List[str] = []
    data = _normalize_solution(solution)
    approaches = data.get("approaches") or []

    if len(approaches) < MIN_APPROACHES:
        errors.append("Solution must have at least 1 approach")
        return errors

    for i, approach in enumerate(approaches):
        title = approach.get("title") or f"Approach {i + 1}"
        if require_all_languages:
            missing = get_missing_languages_for_approach(approach)
            if missing:
                langs_str = ", ".join(m.upper() for m in missing)
                errors.append(f"'{title}': missing or invalid code for: {langs_str}")

        for lang in REQUIRED_LANGS:
            key = CODE_KEY_BY_LANG[lang]
            raw = approach.get(key)
            if isinstance(approach.get("code"), dict):
                raw = approach["code"].get(lang) or raw
            val = (raw or "").strip()
            if not val:
                continue
            if len(val) < min_code_length:
                errors.append(f"'{title}' / {lang}: code block too short (min {min_code_length} chars)")
            if reject_placeholders and _code_looks_like_placeholder(val):
                errors.append(f"'{title}' / {lang}: code appears to be placeholder or pseudo-code")

    return errors


def validate_solution(
    solution: Dict[str, Any],
    *,
    require_all_languages: bool = True,
    min_code_length: int = MIN_CODE_LENGTH,
    reject_placeholders: bool = True,
) -> Tuple[bool, List[str]]:
    """
    Validate solution against mandatory schema.
    Returns (valid: bool, errors: list of messages).
    Solution cannot be saved or published unless valid is True.
    """
    errors = get_validation_errors(
        solution,
        require_all_languages=require_all_languages,
        min_code_length=min_code_length,
        reject_placeholders=reject_placeholders,
    )
    return (len(errors) == 0, errors)


def validate_solution_verbal_only(solution: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Weaker check: reject solutions that are verbal-only (no code at all).
    At least one approach must have at least one non-empty code block (any language).
    Use for backward compatibility while migrating to full 6-language requirement.
    """
    errors: List[str] = []
    data = _normalize_solution(solution)
    approaches = data.get("approaches") or []
    if not approaches:
        errors.append("Solution must have at least 1 approach")
        return (False, errors)
    for i, approach in enumerate(approaches):
        title = approach.get("title") or f"Approach {i + 1}"
        has_any = False
        for lang in REQUIRED_LANGS:
            key = CODE_KEY_BY_LANG[lang]
            raw = approach.get(key)
            if isinstance(approach.get("code"), dict):
                raw = approach.get("code", {}).get(lang) or raw
            if (raw or "").strip() and len((raw or "").strip()) >= MIN_CODE_LENGTH:
                has_any = True
                break
        if not has_any:
            errors.append(f"'{title}': at least one complete code block (any language) required; no verbal-only approaches")
    return (len(errors) == 0, errors)


def get_missing_languages_per_approach(solution: Dict[str, Any]) -> Dict[int, List[str]]:
    """Return { approach_index: [lang, ...] } for corrective regeneration."""
    data = _normalize_solution(solution)
    approaches = data.get("approaches") or []
    out = {}
    for i, approach in enumerate(approaches):
        missing = get_missing_languages_for_approach(approach)
        if missing:
            out[i] = missing
    return out


def get_corrective_instruction(
    errors: List[str],
    missing_per_approach: Optional[Dict[int, List[str]]] = None,
) -> str:
    """
    Build a message to send back to AI (or human) to fix missing/invalid code.
    Use after validate_solution fails; then regenerate only missing sections.
    """
    parts = ["Solution validation failed. Fix the following:\n"]
    if errors:
        parts.append("\n".join(f"- {e}" for e in errors))
    if missing_per_approach:
        parts.append("\n\nMissing code blocks by approach (generate complete, compilable code for these languages only):")
        for idx, langs in sorted(missing_per_approach.items()):
            parts.append(f"\n- Approach index {idx}: {', '.join(l.upper() for l in langs)}")
    parts.append("\n\nDo not use placeholders (..., TODO). Each code block must be complete and compilable.")
    return "".join(parts)


def merge_missing_into_solution(
    solution: Dict[str, Any],
    new_code_by_approach_lang: Dict[int, Dict[str, str]],
) -> Dict[str, Any]:
    """
    Merge newly generated code into solution. new_code_by_approach_lang: { approach_index: { "java": "...", "python": "..." } }.
    Returns a new solution dict with merged code (does not mutate input).
    """
    import copy
    data = copy.deepcopy(_normalize_solution(solution))
    approaches = data.get("approaches") or []
    for idx, lang_code in new_code_by_approach_lang.items():
        if idx < 0 or idx >= len(approaches):
            continue
        for lang, code in lang_code.items():
            if lang not in REQUIRED_LANGS:
                continue
            key = CODE_KEY_BY_LANG[lang]
            if code and (code := (code or "").strip()):
                approaches[idx][key] = code
    return data


def get_required_languages() -> Tuple[str, ...]:
    """Return tuple of required language keys for use in scripts."""
    return REQUIRED_LANGS


def get_code_key_for_language(lang: str) -> Optional[str]:
    """Return the approach dict key for a language (e.g. 'java' -> 'code_java')."""
    return CODE_KEY_BY_LANG.get(lang)


def validate_with_retry(
    solution: Dict[str, Any],
    regenerate_fn: Optional[Callable[..., Optional[Dict[str, Any]]]] = None,
    max_retries: int = 3,
    **validate_kwargs: Any,
) -> Tuple[bool, Dict[str, Any], List[str]]:
    """
    Validate solution; if invalid and regenerate_fn is provided, call it with corrective
    instruction and merge result, then revalidate. Retry up to max_retries times.
    regenerate_fn(success, solution_dict, errors, corrective_message) -> new_solution_dict or None.
    Returns (valid, final_solution, errors).
    """
    current = _normalize_solution(solution)
    errors: List[str] = []
    for attempt in range(max_retries + 1):
        valid, errors = validate_solution(current, **validate_kwargs)
        if valid:
            return (True, current, [])
        if not regenerate_fn or attempt >= max_retries:
            return (False, current, errors)
        missing_per = get_missing_languages_per_approach(current)
        corrective = get_corrective_instruction(errors, missing_per)
        try:
            new_part = regenerate_fn(False, current, errors, corrective)
        except Exception:
            return (False, current, errors)
        if not new_part or not isinstance(new_part, dict):
            return (False, current, errors)
        # Merge: new_part has "approaches" list with (possibly partial) approach dicts.
        approaches = current.get("approaches") or []
        for i, app in enumerate((new_part.get("approaches") or [])[: len(approaches)]):
            for lang in REQUIRED_LANGS:
                key = CODE_KEY_BY_LANG[lang]
                val = (app.get(key) or "").strip()
                if val:
                    approaches[i][key] = val
    return (False, current, errors)
