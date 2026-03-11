"""
Generate additional test cases (edge, boundary) by running the official solution.
Used to satisfy minimum visible (2) and hidden (20) test case requirements.
Respects constraints and avoids duplicating existing (input, expected_output).

Edge case generation rules (STEP 3):
  Arrays: empty, single element, two elements, all same, negatives, zero, duplicates, reversed.
  Strings: empty, single char, two chars, all same chars, case sensitivity.
  Two-line (array + target): empty array + value, single element + target, boundary targets.
  Linked lists / trees: null/empty, single node (inferred from space-separated list format).
"""
import re
from typing import List, Tuple, Optional, Set
from models import TestCase

# Minimum we need to generate if missing
MIN_VISIBLE = 2
MIN_HIDDEN = 20


def _tc_key(tc) -> Tuple[str, str]:
    if isinstance(tc, TestCase):
        return (tc.input or "", tc.expected_output or "")
    return (tc.get("input") or "", tc.get("expected_output") or "")


def _normalize_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def _add_candidate(candidates: List[str], cand: str, existing_inputs: Set[str], max_candidates: int) -> bool:
    """Add candidate if not duplicate (normalized). Returns True if we hit max_candidates."""
    cnorm = _normalize_ws(cand)
    cstrip = cand.strip() if isinstance(cand, str) else cand
    if cnorm in existing_inputs or cstrip in existing_inputs:
        return False
    existing_inputs.add(cnorm)
    existing_inputs.add(cstrip)
    candidates.append(cand)
    return len(candidates) >= max_candidates


def _edge_candidates_arrays() -> List[str]:
    """Edge cases for arrays: empty, single, two, all same, negatives, zero, duplicates."""
    return [
        "",           # empty array
        "0",          # single element
        "1",
        "-1",
        "0 0",        # two same
        "1 1",
        "1 2",        # two different
        "2 1",        # reversed
        "-1 0 1",     # negatives and zero
        "0 1 2",
        "1 2 2",      # duplicates
        "3 3 3",      # all same values
        "1 0 -1",     # descending
    ]


def _edge_candidates_strings() -> List[str]:
    """Edge cases for strings: empty, single char, two, all same, case."""
    return [
        "",
        "a",
        "A",
        "ab",
        "aa",
        "aba",
        "aab",
        "abc",
    ]


def _edge_candidates_two_line_array_target() -> List[Tuple[str, str]]:
    """Two-line format: line1 = array (space-separated), line2 = target. Edge: empty, single, boundary."""
    return [
        ("", "0"),
        ("0", "0"),
        ("1", "1"),
        ("1 1", "2"),
        ("1 2", "3"),
        ("0", "1"),
        ("-1 1", "0"),
        ("1 2 3", "4"),
        ("2 2", "4"),
        ("0 0", "0"),
    ]


def _edge_candidates_two_line_two_arrays() -> List[Tuple[str, str]]:
    """Two lines as two arrays (e.g. merge two lists). Null head, single node, empty + single."""
    return [
        ("", ""),
        ("", "0"),
        ("0", ""),
        ("0", "0"),
        ("1", "1"),
        ("1 2", "1"),
        ("1", "1 2"),
        ("1 2", "3 4"),
        ("0", "1 2 3"),
    ]


_INT_TOKEN_RE = re.compile(r"[-+]?\d+$")


def _parse_int_tokens(line: str) -> Optional[List[int]]:
    text = (line or "").strip()
    if text == "":
        return []
    toks = text.split()
    nums: List[int] = []
    for tok in toks:
        if not _INT_TOKEN_RE.fullmatch(tok):
            return None
        nums.append(int(tok))
    return nums


def _dedupe_keep_order(values: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for v in values:
        key = _normalize_ws(v)
        if key in seen:
            continue
        seen.add(key)
        out.append(v)
    return out


def _numeric_line_variations(base_line: str, max_items: int = 48) -> List[str]:
    nums = _parse_int_tokens(base_line)
    if nums is None:
        return []
    out: List[str] = []
    out.extend(_edge_candidates_arrays())
    if nums:
        out.append(" ".join(str(x) for x in nums))
        out.append(" ".join(str(x) for x in reversed(nums)))
        out.append(" ".join(str(x) for x in sorted(nums)))
        out.append(" ".join(str(x) for x in sorted(nums, reverse=True)))
        for delta in (-3, -2, -1, 1, 2, 3):
            out.append(" ".join(str(x + delta) for x in nums))
        if len(nums) > 1:
            out.append(" ".join(str(x) for x in (nums[1:] + nums[:1])))
            out.append(" ".join(str(x) for x in (nums[-1:] + nums[:-1])))
        for take in range(1, min(6, len(nums) + 1)):
            out.append(" ".join(str(x) for x in nums[:take]))
        out.append(" ".join(str(nums[0]) for _ in range(min(8, max(1, len(nums))))))
        out.append(" ".join(str((i % 9) - 4) for i in range(min(10, max(1, len(nums) + 2)))))
        out.append(" ".join(str(i) for i in range(min(10, max(1, len(nums) + 1)))))
    else:
        out.extend(["0", "1", "-1", "0 0", "1 2", "-1 0 1"])
    return _dedupe_keep_order(out)[:max_items]


def _text_line_variations(base_line: str, max_items: int = 48) -> List[str]:
    text = (base_line or "").strip()
    toks = text.split()
    out: List[str] = []
    out.extend(_edge_candidates_strings())
    if text:
        out.extend([
            text.lower(),
            text.upper(),
            text[::-1],
        ])
    if toks:
        out.extend([
            toks[0],
            " ".join(toks[::-1]),
            " ".join(toks[: max(1, len(toks) // 2)]),
            " ".join(toks + toks[:1]),
        ])
    lower_tokens = {t.lower() for t in toks}
    if any(ch in text for ch in "()[]{}"):
        out.extend(["()", "()[]{}", "([{}])", "([)]", "(]", "((()))"])
    if "push" in lower_tokens:
        out.extend([
            "push 1 push 2 top pop",
            "push -1 push -2 pop top",
            "push 5 pop",
        ])
    if "put" in lower_tokens and "get" in lower_tokens:
        out.extend([
            "2\nput 1 1 put 2 2 get 1 put 3 3 get 2 get 3",
            "1\nput 1 10 get 1 get 2",
        ])
    if "insert" in lower_tokens and "search" in lower_tokens:
        out.extend([
            "insert apple search apple startsWith app",
            "insert cat insert car search cap startsWith ca",
        ])
    if "addword" in lower_tokens:
        out.extend([
            "addWord bad addWord dad addWord mad search .ad search b..",
            "addWord a addWord ab search . search a.",
        ])
    if not out:
        out.extend(["a", "ab", "abc"])
    return _dedupe_keep_order(out)[:max_items]


def _nullable_numeric_line_variations(base_line: str, max_items: int = 40) -> List[str]:
    """For serialized tree-like lines (numbers + null), keep shape and mutate numeric values."""
    toks = (base_line or "").strip().split()
    if not toks:
        return []
    has_null = False
    numeric_positions = []
    for i, tok in enumerate(toks):
        if _INT_TOKEN_RE.fullmatch(tok):
            numeric_positions.append(i)
            continue
        if tok.lower() in {"null", "nil", "none"}:
            has_null = True
            continue
        return []
    if not has_null:
        return []
    out: List[str] = []
    for delta in (-3, -2, -1, 1, 2, 3):
        new_toks = list(toks)
        for j, pos in enumerate(numeric_positions):
            base = int(toks[pos])
            new_toks[pos] = str(base + delta + (j % 2))
        out.append(" ".join(new_toks))
    out.extend([
        "null",
        "1 null 2",
        "1 2 2 3 null null 3",
        "4 2 7 1 3 6 9",
    ])
    return _dedupe_keep_order(out)[:max_items]


def _rpn_line_variations(base_line: str, max_items: int = 30) -> List[str]:
    toks = (base_line or "").strip().split()
    ops = {"+", "-", "*", "/"}
    if not toks or not any(tok in ops for tok in toks):
        return []
    out = [
        "2 1 +",
        "2 1 + 3 *",
        "4 13 5 / +",
        "5 1 2 + 4 * + 3 -",
        "10 6 9 3 + -11 * / * 17 + 5 +",
    ]
    return _dedupe_keep_order(out)[:max_items]


def _matrix_with_dims_candidates(lines: List[str], max_candidates: int) -> List[str]:
    if not lines:
        return []
    first = _parse_int_tokens(lines[0])
    if first is None or len(first) != 2:
        return []
    rows, cols = first
    if rows <= 0 or cols <= 0 or len(lines) < 1 + rows:
        return []
    body = lines[1 : 1 + rows]
    if any(_parse_int_tokens(ln) is None for ln in body):
        return []
    extras = lines[1 + rows :]
    out: List[str] = []
    dim_opts = [(1, 1), (1, 2), (2, 2), (2, 3), (3, 3), (3, 4), (4, 4), (5, 5)]
    for r, c in dim_opts:
        mat_lines = []
        for i in range(r):
            row_vals = [((i * c + j) % 11) - 5 for j in range(c)]
            mat_lines.append(" ".join(str(v) for v in row_vals))
        cand_lines = [f"{r} {c}"] + mat_lines
        for idx, ex in enumerate(extras):
            ex_nums = _parse_int_tokens(ex)
            if ex_nums is not None and len(ex_nums) == 1:
                cand_lines.append(str(ex_nums[0] + ((r + c + idx) % 5) - 2))
            else:
                cand_lines.append(ex)
        out.append("\n".join(cand_lines))
        if len(out) >= max_candidates:
            break
    return out[:max_candidates]


def _count_prefixed_rows_candidates(lines: List[str], max_candidates: int) -> List[str]:
    if not lines:
        return []
    first = _parse_int_tokens(lines[0])
    if first is None or len(first) != 1:
        return []
    k = first[0]
    if k <= 0 or len(lines) < 2:
        return []
    out: List[str] = []
    for kk in (1, 2, 3, 4, 5):
        cand_lines = [str(kk)]
        for i in range(kk):
            row_len = (i % 4) + 1
            row = [((i + j) % 9) - 4 for j in range(row_len)]
            cand_lines.append(" ".join(str(v) for v in row))
        out.append("\n".join(cand_lines))
        if len(out) >= max_candidates:
            break
    return out[:max_candidates]


def _matrix_plus_target_candidates(lines: List[str], max_candidates: int) -> List[str]:
    if len(lines) < 3:
        return []
    parsed = [_parse_int_tokens(ln) for ln in lines]
    if any(p is None for p in parsed):
        return []
    parsed = [p or [] for p in parsed]
    if len(parsed[-1]) != 1:
        return []
    matrix_rows = parsed[:-1]
    if not matrix_rows or any(len(r) == 0 for r in matrix_rows):
        return []
    row_count = len(matrix_rows)
    col_count = min(len(r) for r in matrix_rows)
    out: List[str] = []
    targets = [parsed[-1][0], parsed[-1][0] + 1, parsed[-1][0] - 1, 0, 1, -1]
    for t in targets:
        cand_lines = []
        for i in range(row_count):
            row = [((i + j + t) % 13) - 6 for j in range(col_count)]
            cand_lines.append(" ".join(str(v) for v in row))
        cand_lines.append(str(t))
        out.append("\n".join(cand_lines))
        if len(out) >= max_candidates:
            break
    return out[:max_candidates]


def _linewise_mutation_candidates(lines: List[str], max_candidates: int) -> List[str]:
    if not lines:
        return []
    per_line_vars: List[List[str]] = []
    for line in lines:
        if _parse_int_tokens(line) is not None:
            per_line_vars.append(_numeric_line_variations(line, max_items=18))
        else:
            per_line_vars.append(_text_line_variations(line, max_items=18))
    out: List[str] = []
    # Mutate one line at a time.
    for i, vars_i in enumerate(per_line_vars):
        for v in vars_i:
            new_lines = list(lines)
            new_lines[i] = v
            out.append("\n".join(new_lines))
            if len(out) >= max_candidates:
                return out
    # Mutate first two lines together for extra diversity.
    if len(lines) >= 2:
        for v0 in per_line_vars[0][:8]:
            for v1 in per_line_vars[1][:8]:
                new_lines = list(lines)
                new_lines[0] = v0
                new_lines[1] = v1
                out.append("\n".join(new_lines))
                if len(out) >= max_candidates:
                    return out
    return out[:max_candidates]


def candidate_inputs_from_existing(
    existing_tcs: List,
    tags: Optional[List[str]] = None,
    max_candidates: int = 32,
) -> List[str]:
    """
    Generate candidate input strings from existing test cases.
    Infers format from first test case; produces edge/boundary variations per STEP 3 rules.
    Does NOT return inputs that already exist (by normalized input).
    Must NOT duplicate existing; must NOT be trivial variation; must respect constraints.
    """
    if not existing_tcs:
        return []
    existing_inputs: Set[str] = set()
    seed_inputs: List[str] = []
    for tc in existing_tcs:
        inp = (tc.get("input") if isinstance(tc, dict) else getattr(tc, "input", "")) or ""
        existing_inputs.add(_normalize_ws(inp))
        existing_inputs.add(inp.strip())
        if inp not in seed_inputs:
            seed_inputs.append(inp)

    candidates: List[str] = []
    tag_set = {str(t).lower() for t in (tags or [])}

    for seed in seed_inputs[:5]:
        lines = seed.strip().split("\n")
        if not lines:
            continue
        local_pool: List[str] = []
        if len(lines) == 1:
            local_pool.extend(_nullable_numeric_line_variations(lines[0], max_items=max_candidates))
            local_pool.extend(_rpn_line_variations(lines[0], max_items=max_candidates))
            if _parse_int_tokens(lines[0]) is not None:
                local_pool.extend(_numeric_line_variations(lines[0], max_items=max_candidates))
            else:
                local_pool.extend(_text_line_variations(lines[0], max_items=max_candidates))
        elif len(lines) == 2:
            l1_nums = _parse_int_tokens(lines[1])
            if l1_nums is not None and len(l1_nums) == 1:
                for a, b in _edge_candidates_two_line_array_target():
                    local_pool.append(f"{a}\n{b}")
            for a, b in _edge_candidates_two_line_two_arrays():
                local_pool.append(f"{a}\n{b}")
            local_pool.extend(_linewise_mutation_candidates(lines, max_candidates=max_candidates))
        else:
            local_pool.extend(_matrix_with_dims_candidates(lines, max_candidates=max_candidates))
            local_pool.extend(_count_prefixed_rows_candidates(lines, max_candidates=max_candidates))
            local_pool.extend(_matrix_plus_target_candidates(lines, max_candidates=max_candidates))
            local_pool.extend(_linewise_mutation_candidates(lines, max_candidates=max_candidates))
        for cand in _dedupe_keep_order(local_pool):
            if _add_candidate(candidates, cand, existing_inputs, max_candidates):
                return candidates

    # Global fallback pool to ensure we can still add enough hidden tests.
    fallback_pool = [
        "",
        "0",
        "1",
        "-1",
        "1 2 3",
        "3 2 1",
        "1 1 1 1",
        "a",
        "ab",
        "abc",
        "()",
        "()[]{}",
        "a\nb",
        "1\n0",
        "1 2\n3",
        "2\n1 2",
        "2 2\n1 0\n0 1",
        "3\n1 2 3\n4 5 6\n7 8 9",
    ]
    if "design" in tag_set:
        fallback_pool.extend([
            "push 1 push 2 top pop",
            "push -1 pop top",
            "insert apple search apple startsWith app",
            "addWord bad search b..",
            "2\nput 1 1 put 2 2 get 1 get 2",
        ])
    for cand in fallback_pool:
        if _add_candidate(candidates, cand, existing_inputs, max_candidates):
            break
    return candidates[:max_candidates]


def build_full_code_python(solution_code: str, driver_code: str) -> str:
    """Combine solution and driver for Python (driver reads stdin, calls solution)."""
    sol = (solution_code or "").strip()
    drv = (driver_code or "").strip()
    if not drv:
        return sol
    return sol + "\n\n" + drv


def run_solution_for_input(
    full_code: str,
    language: str,
    input_str: str,
    executor,
) -> Optional[str]:
    """
    Run solution with one input; return actual output or None on error/timeout.
    executor has execute_code(code, language, test_cases, visible_only=False).
    """
    from models import Language
    tc = TestCase(input=input_str, expected_output="", is_hidden=True)
    try:
        result = executor.execute_code(
            full_code,
            Language(language),
            [tc],
            visible_only=False,
        )
        if not result or not result.get("test_results"):
            return None
        out = result["test_results"][0].get("output")
        if out is None:
            return None
        status = result.get("status")
        if status:
            status_val = status.value if hasattr(status, "value") else str(status)
            if status_val in ("runtime_error", "compile_error", "time_limit_exceeded", "memory_limit_exceeded"):
                return None
        return out.strip() if isinstance(out, str) else str(out).strip()
    except Exception:
        return None


def generate_hidden_cases(
    existing_tcs: List,
    solution_code_python: str,
    driver_code_python: str,
    executor,
    tags: Optional[List[str]] = None,
    min_hidden: int = MIN_HIDDEN,
    max_new: int = 30,
) -> List[dict]:
    """
    Generate new hidden test cases by running the official solution on candidate inputs.
    Returns list of {"input": str, "expected_output": str, "is_hidden": True}.
    Only adds cases that don't duplicate existing (input, output).
    """
    existing_keys = {_tc_key(tc) for tc in existing_tcs}
    existing_inputs_norm = {_normalize_ws(_tc_key(tc)[0]) for tc in existing_tcs}
    hidden_count = sum(1 for tc in existing_tcs if (tc.get("is_hidden") if isinstance(tc, dict) else getattr(tc, "is_hidden", False)))
    need = min(max_new, min_hidden - hidden_count)
    if need <= 0:
        return []

    full_code = build_full_code_python(solution_code_python, driver_code_python)
    if not full_code or "def " not in full_code:
        return []

    candidates = candidate_inputs_from_existing(existing_tcs, tags=tags, max_candidates=max(need + 2, 5))
    new_cases = []
    for inp in candidates:
        if len(new_cases) >= need:
            break
        if _normalize_ws(inp) in existing_inputs_norm:
            continue
        out = run_solution_for_input(full_code, "python", inp, executor)
        if out is None:
            continue
        key = (inp.strip(), out)
        if key in existing_keys:
            continue
        existing_keys.add(key)
        existing_inputs_norm.add(_normalize_ws(inp))
        new_cases.append({"input": inp, "expected_output": out, "is_hidden": True})
    return new_cases
