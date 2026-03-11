"""
Derive starter (template) code from solution code so the editor shows the same
function signature as in the solutions. Used when returning a problem that has
solutions attached.
"""
import re


def _python_class_to_starter(code: str) -> str | None:
    """Extract class and method signatures; return class skeleton with pass in each method."""
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    # Match class Name: at start (optional leading import/comment lines)
    m = re.search(r"^class\s+(\w+)\s*:", code, re.MULTILINE)
    if not m:
        return None
    class_name = m.group(1)
    # Find all method definitions (def method_name(...):) inside the class (indented)
    method_pattern = re.compile(r"^(\s+)def\s+(\w+)\s*\([^)]*\)\s*(?:->[^:]+)?\s*:", re.MULTILINE)
    methods = []
    for match in method_pattern.finditer(code):
        indent, name = match.group(1), match.group(2)
        if name.startswith("_") and name != "__init__":
            continue
        sig = match.group(0).strip()
        methods.append("    " + sig + "\n        pass")
    if not methods:
        return None
    return "class " + class_name + ":\n" + "\n\n".join(methods)


def _python_solution_to_starter(code: str) -> str | None:
    """Extract first function definition and return signature + pass."""
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    # If solution is class-based, return class starter instead
    if re.match(r"^\s*class\s+\w+\s*:", code):
        return _python_class_to_starter(code)
    # Match def name(...): or def name(...) -> ...:
    m = re.search(r"^def\s+\w+\s*\([^)]*\)\s*(?:->[^:]+)?\s*:", code, re.MULTILINE)
    if not m:
        return None
    start = m.start()
    # Signature is the first line that ends with ):
    first_line_end = code.find("\n", start)
    if first_line_end == -1:
        first_line_end = len(code)
    line = code[start:first_line_end].rstrip()
    if not line.endswith(":"):
        # Multi-line signature: take until we see ):
        idx = code.find("):", start)
        if idx == -1:
            return None
        line = code[start : idx + 2].rstrip()
    return line + "\n    pass"


def _javascript_class_to_starter(code: str) -> str | None:
    """Extract class and method signatures; return class skeleton with empty bodies."""
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    m = re.search(r"class\s+(\w+)\s*\{", code)
    if not m:
        return None
    method_pattern = re.compile(r"^\s{2,}(\w+)\s*\([^)]*\)\s*\{", re.MULTILINE)
    methods = []
    for match in method_pattern.finditer(code):
        name = match.group(1)
        if name == "constructor":
            methods.append("  constructor() {\n  }")
        else:
            methods.append(f"  {name}() {{\n  }}")
    if not methods:
        return None
    return "class " + m.group(1) + " {\n" + "\n\n".join(methods) + "\n}"


def _javascript_solution_to_starter(code: str) -> str | None:
    """Extract first function or class and return signature + empty body."""
    if not code or not isinstance(code, str):
        return None
    code = code.strip()
    if re.search(r"^\s*class\s+\w+\s*\{", code):
        return _javascript_class_to_starter(code)
    m = re.search(r"function\s+(\w+)\s*\([^)]*\)\s*\{", code)
    if not m:
        return None
    start = m.start()
    brace = code.find("{", start)
    if brace == -1:
        return None
    sig = code[start : brace + 1].rstrip()
    return sig + "\n}"


def solution_code_to_starter(code: str | None, language: str) -> str | None:
    """
    Return a minimal starter (signature + empty body) for the given solution code.
    language: 'python' or 'javascript'.
    """
    if not code:
        return None
    lang = (language or "").lower()
    if lang == "python":
        return _python_solution_to_starter(code)
    if lang == "javascript":
        return _javascript_solution_to_starter(code)
    return None


def apply_starters_from_solutions(problem: dict, approaches: list) -> None:
    """
    When approaches have code_python/code_javascript, set problem['starter_code_python']
    and problem['starter_code_javascript'] to matching stubs so the editor template
    matches the solution function. Mutates problem in place.
    """
    if not approaches:
        return
    first = approaches[0] if isinstance(approaches[0], dict) else None
    if not first:
        return
    for lang_key, api_lang in [
        ("starter_code_python", "python"),
        ("starter_code_javascript", "javascript"),
    ]:
        code_key = "code_python" if "python" in lang_key else "code_javascript"
        code = first.get(code_key) or first.get("code") if code_key == "code_python" else first.get(code_key)
        if not code:
            continue
        starter = solution_code_to_starter(code, api_lang)
        if starter:
            problem[lang_key] = starter
