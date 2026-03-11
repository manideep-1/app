"""
Validates that user code contains the required function with the correct name.
Contract: problem.function_metadata is the single source of truth; submission must implement that function.
"""
import re
from typing import Optional, Tuple

from models import ProblemFunctionMetadata, Language


SIGNATURE_MISMATCH_MSG = (
    "Function signature does not match problem definition. "
    "Ensure your code defines the required function with the exact name and parameter order from the problem."
)


def _normalize_identifier(name: str) -> str:
    """Return regex-safe function name for pattern matching."""
    return re.escape(name)


def _validate_python(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    # def function_name( or (inside class) def function_name(
    pattern = rf"\bdef\s+{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_javascript(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    # function function_name( or function_name\s*\( (arrow/assignment)
    if re.search(rf"\bfunction\s+{_normalize_identifier(fn_name)}\s*\(", code):
        return True, None
    if re.search(rf"\b{_normalize_identifier(fn_name)}\s*\(", code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_java(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    # Method in class: public ... function_name( or private ... function_name(
    # Accept array/generic/qualified return types like int[], List<Integer>, Map<K,V>, String[][], etc.
    pattern = rf"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],?.\s]+\s+{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_cpp(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    # Method: return_type function_name( or inside class
    pattern = rf"\b{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_c(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    pattern = rf"\b{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_go(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    pattern = rf"\bfunc\s+{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_csharp(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    # Accept array/generic/nullable return types like int[], List<int>, Dictionary<K,V>, string?, etc.
    pattern = rf"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],?.\s]+\s+{_normalize_identifier(fn_name)}\s*\("
    if re.search(pattern, code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


def _validate_typescript(code: str, fn_name: str) -> Tuple[bool, Optional[str]]:
    if re.search(rf"\bfunction\s+{_normalize_identifier(fn_name)}\s*\(", code):
        return True, None
    if re.search(rf"\b{_normalize_identifier(fn_name)}\s*[<(]", code):
        return True, None
    return False, SIGNATURE_MISMATCH_MSG


_VALIDATORS = {
    Language.PYTHON: _validate_python,
    Language.JAVASCRIPT: _validate_javascript,
    Language.JAVA: _validate_java,
    Language.CPP: _validate_cpp,
    Language.C: _validate_c,
    Language.GO: _validate_go,
    Language.CSHARP: _validate_csharp,
    Language.TYPESCRIPT: _validate_typescript,
}


def validate_signature(
    user_code: str,
    language: Language,
    metadata: ProblemFunctionMetadata,
) -> Tuple[bool, Optional[str]]:
    """
    Verify that user code defines the required function (by name).
    Returns (True, None) if valid, (False, error_message) otherwise.
    """
    if not user_code or not metadata or not metadata.function_name:
        return True, None
    fn = metadata.function_name.strip()
    if not fn:
        return True, None
    validator = _VALIDATORS.get(language)
    if not validator:
        return True, None
    return validator(user_code, fn)
