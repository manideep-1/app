"""
Intelligent output comparison for judge: trim, normalize whitespace, array comparison, float tolerance.
"""
import re
from typing import Tuple

# Relative tolerance for floating-point comparison (e.g. 1e-6)
FLOAT_REL_TOL = 1e-6
FLOAT_ABS_TOL = 1e-9


def _normalize_line(s: str) -> str:
    return " ".join(s.split())


def _tokenize_for_compare(s: str) -> list:
    """Split into tokens (words/numbers) for comparison."""
    s = s.strip()
    if not s:
        return []
    return s.split()


def _try_float(x: str) -> float | None:
    try:
        return float(x)
    except ValueError:
        return None


def _tokens_match(a: str, b: str) -> bool:
    """Compare two tokens with float tolerance."""
    fa, fb = _try_float(a), _try_float(b)
    if fa is not None and fb is not None:
        if abs(fa - fb) <= FLOAT_ABS_TOL:
            return True
        if abs(fa) < 1e-300 and abs(fb) < 1e-300:
            return True
        rel = abs(fa - fb) / (max(abs(fa), abs(fb)) + 1e-300)
        return rel <= FLOAT_REL_TOL
    return a == b


def _unordered_line_match(got_lines: list[str], exp_lines: list[str]) -> bool:
    """Best-effort order-insensitive comparison for multi-line outputs."""
    if len(got_lines) <= 1 or len(got_lines) != len(exp_lines):
        return False

    # Common case: same rows, different row order (e.g. 3Sum/subsets permutations listing order).
    if sorted(got_lines) == sorted(exp_lines):
        return True

    # Group-anagram style rows where row/word order can differ and commas are used.
    has_group_like = any("," in line for line in got_lines + exp_lines)
    if not has_group_like:
        return False

    def _normalize_group_row(line: str) -> str:
        parts = [p for p in re.split(r"[,\s]+", line.strip()) if p]
        return " ".join(sorted(parts))

    got_norm = sorted(_normalize_group_row(line) for line in got_lines)
    exp_norm = sorted(_normalize_group_row(line) for line in exp_lines)
    return got_norm == exp_norm


def _semantic_tokens(s: str) -> list[str]:
    """
    Tokenize while ignoring container punctuation.
    Examples:
    - "[3] [9, 20]" -> ["3", "9", "20"]
    - "false true" -> ["false", "true"]
    """
    return re.findall(r"-?\d+(?:\.\d+)?|[A-Za-z_]+", (s or "").strip())


def _punctuation_insensitive_match(got: str, expected: str) -> bool:
    gt = _semantic_tokens(got)
    et = _semantic_tokens(expected)
    if not gt or not et or len(gt) != len(et):
        return False
    for a, b in zip(gt, et):
        aa = a.lower()
        bb = b.lower()
        if aa in {"true", "false", "none", "null"} or bb in {"true", "false", "none", "null"}:
            if aa != bb:
                return False
            continue
        if not _tokens_match(a, b):
            return False
    return True


def compare_outputs(got: str, expected: str) -> Tuple[bool, str]:
    """
    Compare judge output with expected. Returns (match, diff_message).
    - Trims and normalizes whitespace per line.
    - Compares token-by-token with float tolerance.
    - Handles single-line and multi-line; arrays as space-separated numbers.
    """
    got = (got or "").strip()
    expected = (expected or "").strip()
    if got == expected:
        return True, ""

    # Normalize: collapse internal whitespace per line, strip each line
    got_lines = [_normalize_line(l) for l in got.splitlines()]
    exp_lines = [_normalize_line(l) for l in expected.splitlines()]

    # Trim trailing empty lines
    while got_lines and not got_lines[-1]:
        got_lines.pop()
    while exp_lines and not exp_lines[-1]:
        exp_lines.pop()

    if len(got_lines) != len(exp_lines):
        if _punctuation_insensitive_match(got, expected):
            return True, ""
        return False, f"Expected {len(exp_lines)} line(s), got {len(got_lines)}"

    if _unordered_line_match(got_lines, exp_lines):
        return True, ""

    for i, (g, e) in enumerate(zip(got_lines, exp_lines)):
        g_tokens = g.split()
        e_tokens = e.split()
        if len(g_tokens) != len(e_tokens):
            if _punctuation_insensitive_match(got, expected):
                return True, ""
            return False, f"Line {i + 1}: expected {len(e_tokens)} token(s), got {len(g_tokens)}"
        for j, (gt, et) in enumerate(zip(g_tokens, e_tokens)):
            if not _tokens_match(gt, et):
                if _punctuation_insensitive_match(got, expected):
                    return True, ""
                return False, f"Line {i + 1}: expected '{et}', got '{gt}'"
    return True, ""


def normalize_output(s: str) -> str:
    """Normalize for display: trim, collapse blank lines to single newline."""
    if not s:
        return ""
    lines = [line.rstrip() for line in s.rstrip().splitlines()]
    return "\n".join(lines)
