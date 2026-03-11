"""
Signature contract utilities.

Purpose:
- Keep a single function-contract shape per problem (metadata-driven when available).
- Parse code signatures across supported languages.
- Normalize solution snippets so copy/paste into editor uses the same callable contract.
"""
from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Dict, List, Optional, Tuple

from models import ProblemFunctionMetadata
from starter_template_generator import generate_starter


LANG_CODE_KEY: Dict[str, str] = {
    "python": "code_python",
    "javascript": "code_javascript",
    "java": "code_java",
    "cpp": "code_cpp",
    "go": "code_go",
    "csharp": "code_csharp",
    "typescript": "code_typescript",
    "c": "code_c",
}

REQUIRED_SIGNATURE_LANGS = ("python", "javascript", "java", "cpp", "go", "csharp", "typescript")


@dataclass
class ParamSig:
    name: str
    type: str = ""


@dataclass
class ParsedSignature:
    language: str
    function_name: str
    return_type: str
    params: List[ParamSig]
    header_span: Tuple[int, int]


def _split_params(params_text: str) -> List[str]:
    # Split parameters while respecting simple generic commas: List<int[]>, Map<K, V>, etc.
    out: List[str] = []
    cur: List[str] = []
    depth = 0
    for ch in params_text:
        if ch in "<([":
            depth += 1
            cur.append(ch)
            continue
        if ch in ">)]":
            depth = max(0, depth - 1)
            cur.append(ch)
            continue
        if ch == "," and depth == 0:
            token = "".join(cur).strip()
            if token:
                out.append(token)
            cur = []
            continue
        cur.append(ch)
    token = "".join(cur).strip()
    if token:
        out.append(token)
    return out


def _parse_typed_params(params_text: str, language: str) -> List[ParamSig]:
    out: List[ParamSig] = []
    for raw in _split_params(params_text):
        part = raw.strip()
        if not part:
            continue
        if language == "go":
            # Common form: "nums []int", "target int"
            toks = part.split()
            if len(toks) >= 2:
                out.append(ParamSig(name=toks[0].strip(), type=" ".join(toks[1:]).strip()))
            else:
                out.append(ParamSig(name=toks[0].strip(), type=""))
            continue
        if language in ("python", "typescript"):
            # "name: type = default" or "name: type"
            head = part.split("=")[0].strip()
            if ":" in head:
                n, t = head.split(":", 1)
                out.append(ParamSig(name=n.strip(), type=t.strip()))
            else:
                out.append(ParamSig(name=head.strip(), type=""))
            continue
        # Java/C#/C++/C/JS fallback typed-ish parse
        cleaned = part.split("=")[0].strip()
        cleaned = cleaned.replace("...", "").strip()
        if language in ("javascript",):
            out.append(ParamSig(name=cleaned.strip(), type=""))
            continue
        toks = cleaned.replace("&", " ").replace("*", " ").split()
        if not toks:
            continue
        name = toks[-1].strip()
        typ = cleaned[: cleaned.rfind(name)].strip() if name in cleaned else " ".join(toks[:-1]).strip()
        typ = typ.replace("  ", " ").strip()
        out.append(ParamSig(name=name, type=typ))
    return out


def _normalize_type_str(s: str) -> str:
    return re.sub(r"\s+", "", (s or "").strip()).lower()


def extract_signature(code: str, language: str) -> Optional[ParsedSignature]:
    if not code or not isinstance(code, str):
        return None
    text = code
    lang = (language or "").lower().strip()

    if lang == "python":
        m = re.search(r"^\s*def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([^:]+))?\s*:", text, flags=re.MULTILINE)
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(1).strip(),
            return_type=(m.group(3) or "").strip(),
            params=_parse_typed_params(m.group(2) or "", "python"),
            header_span=(m.start(), m.end()),
        )

    if lang == "javascript":
        m = re.search(r"\bfunction\s+(\w+)\s*\(([^)]*)\)\s*\{", text, flags=re.MULTILINE)
        if not m:
            m = re.search(r"\b(\w+)\s*=\s*\(([^)]*)\)\s*=>\s*\{", text, flags=re.MULTILINE)
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(1).strip(),
            return_type="",
            params=_parse_typed_params(m.group(2) or "", "javascript"),
            header_span=(m.start(), m.end()),
        )

    if lang == "typescript":
        m = re.search(r"\bfunction\s+(\w+)\s*\(([^)]*)\)\s*(?::\s*([^{]+))?\s*\{", text, flags=re.MULTILINE)
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(1).strip(),
            return_type=(m.group(3) or "").strip(),
            params=_parse_typed_params(m.group(2) or "", "typescript"),
            header_span=(m.start(), m.end()),
        )

    if lang == "go":
        m = re.search(r"\bfunc\s+(\w+)\s*\(([^)]*)\)\s*([^{\n]*)\{", text, flags=re.MULTILINE)
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(1).strip(),
            return_type=(m.group(3) or "").strip(),
            params=_parse_typed_params(m.group(2) or "", "go"),
            header_span=(m.start(), m.end()),
        )

    if lang == "java":
        m = re.search(
            r"(?:public|private|protected)\s+(?:static\s+)?([\w<>\[\],?.\s]+?)\s+(\w+)\s*\(([^)]*)\)\s*\{",
            text,
            flags=re.MULTILINE,
        )
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(2).strip(),
            return_type=(m.group(1) or "").strip(),
            params=_parse_typed_params(m.group(3) or "", "java"),
            header_span=(m.start(), m.end()),
        )

    if lang == "cpp":
        m = re.search(
            r"^\s*([A-Za-z_][\w:<>,\[\]&*\s]+?)\s+(\w+)\s*\(([^)]*)\)\s*\{",
            text,
            flags=re.MULTILINE,
        )
        if not m:
            return None
        ret = (m.group(1) or "").strip()
        if ret.startswith(("if ", "for ", "while ", "switch ", "class ")):
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(2).strip(),
            return_type=ret,
            params=_parse_typed_params(m.group(3) or "", "cpp"),
            header_span=(m.start(), m.end()),
        )

    if lang == "csharp":
        m = re.search(
            r"(?:public|private|protected)\s+(?:static\s+)?([\w<>\[\],?.\s]+?)\s+(\w+)\s*\(([^)]*)\)\s*\{",
            text,
            flags=re.MULTILINE,
        )
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(2).strip(),
            return_type=(m.group(1) or "").strip(),
            params=_parse_typed_params(m.group(3) or "", "csharp"),
            header_span=(m.start(), m.end()),
        )

    if lang == "c":
        m = re.search(r"^\s*([A-Za-z_][\w\s\*]+?)\s+(\w+)\s*\(([^)]*)\)\s*\{", text, flags=re.MULTILINE)
        if not m:
            return None
        return ParsedSignature(
            language=lang,
            function_name=m.group(2).strip(),
            return_type=(m.group(1) or "").strip(),
            params=_parse_typed_params(m.group(3) or "", "c"),
            header_span=(m.start(), m.end()),
        )

    return None


def metadata_signature(metadata: ProblemFunctionMetadata, language: str) -> Optional[ParsedSignature]:
    try:
        starter = generate_starter(metadata, language)
    except Exception:
        return None
    if not starter:
        return None
    return extract_signature(starter, language)


def signatures_match(
    expected: ParsedSignature,
    actual: ParsedSignature,
    strict_types: bool = True,
    strict_param_names: bool = True,
) -> bool:
    if not expected or not actual:
        return False
    if expected.function_name != actual.function_name:
        return False
    if len(expected.params) != len(actual.params):
        return False
    if strict_param_names:
        for e, a in zip(expected.params, actual.params):
            if e.name != a.name:
                return False
    if strict_types:
        # python/javascript type strings are often empty and should not fail by type.
        type_enforced = expected.language in ("java", "cpp", "go", "csharp", "typescript")
        if type_enforced:
            if _normalize_type_str(expected.return_type) != _normalize_type_str(actual.return_type):
                return False
            for e, a in zip(expected.params, actual.params):
                if _normalize_type_str(e.type) != _normalize_type_str(a.type):
                    return False
    return True


def _indent_block(code: str, spaces: int = 4) -> str:
    pad = " " * spaces
    lines = (code or "").splitlines()
    return "\n".join((pad + ln if ln.strip() else ln) for ln in lines)


def _upsert_python_alias(code: str, expected: ParsedSignature) -> str:
    if not code:
        return code
    if re.search(rf"^\s*def\s+{re.escape(expected.function_name)}\s*\(", code, flags=re.MULTILINE):
        return code
    actual = extract_signature(code, "python")
    if not actual or len(actual.params) != len(expected.params):
        return code
    call_args = ", ".join(p.name for p in expected.params)
    old_args = ", ".join(p.name for p in expected.params)
    # Since parameter names may differ, use alias parameters and pass through positionally.
    header = f"def {expected.function_name}({', '.join(p.name + (': ' + p.type if p.type else '') for p in expected.params)})"
    if expected.return_type:
        header += f" -> {expected.return_type}"
    body = (
        f"{header}:\n"
        f"    return {actual.function_name}({old_args})"
    )
    if code.endswith("\n"):
        return code + "\n" + body + "\n"
    return code + "\n\n" + body + "\n"


def _upsert_js_alias(code: str, expected: ParsedSignature, typescript: bool = False) -> str:
    if not code:
        return code
    sig = extract_signature(code, "typescript" if typescript else "javascript")
    if re.search(rf"\bfunction\s+{re.escape(expected.function_name)}\s*\(", code):
        return code
    if not sig or len(sig.params) != len(expected.params):
        return code
    if typescript:
        param_sig = ", ".join(f"{p.name}: {p.type}" if p.type else p.name for p in expected.params)
        ret_sig = f": {expected.return_type}" if expected.return_type else ""
        alias = (
            f"function {expected.function_name}({param_sig}){ret_sig} {{\n"
            f"    return {sig.function_name}({', '.join(p.name for p in expected.params)});\n"
            "}"
        )
    else:
        param_sig = ", ".join(p.name for p in expected.params)
        alias = (
            f"function {expected.function_name}({param_sig}) {{\n"
            f"    return {sig.function_name}({', '.join(p.name for p in expected.params)});\n"
            "}"
        )
    if code.endswith("\n"):
        return code + "\n" + alias + "\n"
    return code + "\n\n" + alias + "\n"


def _upsert_go_alias(code: str, expected: ParsedSignature) -> str:
    if not code:
        return code
    if re.search(rf"\bfunc\s+{re.escape(expected.function_name)}\s*\(", code):
        return code
    actual = extract_signature(code, "go")
    if not actual or len(actual.params) != len(expected.params):
        return code
    params = ", ".join(f"{p.name} {p.type}".strip() for p in expected.params)
    ret = f" {expected.return_type}" if expected.return_type else ""
    call = f"{actual.function_name}({', '.join(p.name for p in expected.params)})"
    if _normalize_type_str(expected.return_type) in ("", "void"):
        body = f"{call}\n"
    else:
        body = f"return {call}\n"
    alias = f"func {expected.function_name}({params}){ret} {{\n\t{body.rstrip()}\n}}"
    if code.endswith("\n"):
        return code + "\n" + alias + "\n"
    return code + "\n\n" + alias + "\n"


def _ensure_java_solution_wrapper(code: str) -> str:
    text = (code or "").strip()
    if not text:
        return text
    # Keep existing imports outside class.
    imports = []
    body_lines = []
    for ln in text.splitlines():
        if ln.strip().startswith("import ") and ln.strip().endswith(";"):
            imports.append(ln.strip())
        elif not ln.strip().startswith("package "):
            body_lines.append(ln)
    body = "\n".join(body_lines).strip()
    if "class Solution" not in body:
        body = "class Solution {\n" + _indent_block(body, 4) + "\n}"
    if not any(ln.strip() == "import java.util.*;" for ln in imports):
        imports.insert(0, "import java.util.*;")
    return ("\n".join(imports).strip() + "\n" + body).strip() + "\n"


def _ensure_cpp_solution_wrapper(code: str) -> str:
    text = (code or "").strip()
    if not text:
        return text
    includes = []
    body_lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("#include ") or s == "using namespace std;":
            includes.append(ln.strip())
        else:
            body_lines.append(ln)
    body = "\n".join(body_lines).strip()
    if "class Solution" not in body:
        body = "class Solution {\npublic:\n" + _indent_block(body, 4) + "\n};"
    if not any(ln.startswith("#include") for ln in includes):
        includes.insert(0, "#include <bits/stdc++.h>")
    if "using namespace std;" not in includes:
        includes.append("using namespace std;")
    return ("\n".join(includes).strip() + "\n\n" + body).strip() + "\n"


def _ensure_csharp_solution_wrapper(code: str) -> str:
    text = (code or "").strip()
    if not text:
        return text
    usings = []
    body_lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if s.startswith("using ") and s.endswith(";"):
            usings.append(s)
        else:
            body_lines.append(ln)
    body = "\n".join(body_lines).strip()
    if "class Solution" not in body:
        body = "public class Solution {\n" + _indent_block(body, 4) + "\n}"
    default_usings = ["using System;", "using System.Collections.Generic;", "using System.Linq;"]
    for u in reversed(default_usings):
        if u not in usings:
            usings.insert(0, u)
    return ("\n".join(usings).strip() + "\n\n" + body).strip() + "\n"


def _insert_method_before_class_end(code: str, method_snippet: str, cxx: bool = False) -> str:
    text = code.rstrip()
    if cxx:
        idx = text.rfind("};")
        if idx != -1:
            return text[:idx].rstrip() + "\n\n" + _indent_block(method_snippet, 4) + "\n" + text[idx:] + "\n"
    idx = text.rfind("}")
    if idx != -1:
        return text[:idx].rstrip() + "\n\n" + _indent_block(method_snippet, 4) + "\n" + text[idx:] + "\n"
    return text + "\n\n" + method_snippet + "\n"


def _replace_java_method_signature(text: str, fn_name: str, expected: ParsedSignature) -> str:
    """Replace the first line (signature) of the method fn_name with the expected signature; keep body."""
    pattern = (
        rf"^(\s*)((?:public|private|protected)\s+(?:static\s+)?)([\w<>\[\],?.\s]+?)\s+({re.escape(fn_name)})\s*\(([^)]*)\)\s*\{{"
    )
    match = re.search(pattern, text, flags=re.MULTILINE)
    if not match:
        # Fallback: direct replace wrong return type for common int[] -> int[][] (e.g. Merge Intervals).
        expected_ret = (expected.return_type or "").strip()
        if expected_ret == "int[][]":
            for wrong in (f"int[] {fn_name}(", f"int [] {fn_name}("):
                if wrong in text:
                    text = text.replace(wrong, f"int[][] {fn_name}(", 1)
                    break
        return text
    indent, vis, _old_ret, _name, _params = match.group(1), match.group(2), match.group(3), match.group(4), match.group(5)
    ret = (expected.return_type or "void").strip()
    params = ", ".join(f"{p.type} {p.name}".strip() for p in expected.params)
    new_sig = f"{indent}{vis}{ret} {fn_name}({params}) {{"
    return text[: match.start()] + new_sig + text[match.end() :]


def _upsert_java_adapter(code: str, expected: ParsedSignature) -> str:
    text = _ensure_java_solution_wrapper(code)
    actual = extract_signature(text, "java")
    has_method = bool(
        re.search(
            rf"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],?.\s]+\s+{re.escape(expected.function_name)}\s*\(",
            text,
        )
    )
    if has_method and actual:
        # If return type (or param types) don't match metadata, replace the method signature so driver compiles.
        ret_match = _normalize_type_str(actual.return_type or "") == _normalize_type_str(expected.return_type or "")
        if not ret_match:
            text = _replace_java_method_signature(text, expected.function_name, expected)
        return text
    if has_method:
        return text
    if not actual or len(actual.params) != len(expected.params):
        return text
    ret = expected.return_type or "void"
    params = ", ".join(f"{p.type} {p.name}".strip() for p in expected.params)
    call = f"{actual.function_name}({', '.join(p.name for p in expected.params)})"
    if _normalize_type_str(ret) == "void":
        method = f"public {ret} {expected.function_name}({params}) {{\n    {call};\n}}"
    else:
        method = f"public {ret} {expected.function_name}({params}) {{\n    return {call};\n}}"
    return _insert_method_before_class_end(text, method, cxx=False)


def _upsert_cpp_adapter(code: str, expected: ParsedSignature) -> str:
    text = _ensure_cpp_solution_wrapper(code)
    if re.search(rf"\b{re.escape(expected.function_name)}\s*\(", text):
        # If already present, treat as aligned enough for call contract.
        return text
    actual = extract_signature(text, "cpp")
    if not actual or len(actual.params) != len(expected.params):
        return text
    ret = expected.return_type or "void"
    params = ", ".join(f"{p.type} {p.name}".strip() for p in expected.params)
    call = f"{actual.function_name}({', '.join(p.name for p in expected.params)})"
    if _normalize_type_str(ret) == "void":
        method = f"{ret} {expected.function_name}({params}) {{\n    {call};\n}}"
    else:
        method = f"{ret} {expected.function_name}({params}) {{\n    return {call};\n}}"
    return _insert_method_before_class_end(text, method, cxx=True)


def _upsert_csharp_adapter(code: str, expected: ParsedSignature) -> str:
    text = _ensure_csharp_solution_wrapper(code)
    if re.search(
        rf"(?:public|private|protected)\s+(?:static\s+)?[\w<>\[\],?.\s]+\s+{re.escape(expected.function_name)}\s*\(",
        text,
    ):
        return text
    actual = extract_signature(text, "csharp")
    if not actual or len(actual.params) != len(expected.params):
        return text
    ret = expected.return_type or "void"
    params = ", ".join(f"{p.type} {p.name}".strip() for p in expected.params)
    call = f"{actual.function_name}({', '.join(p.name for p in expected.params)})"
    if _normalize_type_str(ret) == "void":
        method = f"public {ret} {expected.function_name}({params}) {{\n    {call};\n}}"
    else:
        method = f"public {ret} {expected.function_name}({params}) {{\n    return {call};\n}}"
    return _insert_method_before_class_end(text, method, cxx=False)


def align_solution_code_to_metadata(code: str, language: str, metadata: Optional[ProblemFunctionMetadata]) -> str:
    """Return schema-aligned solution code. Non-destructive where possible (adds adapters/wrappers)."""
    if not code or not metadata:
        return code
    lang = (language or "").lower().strip()
    expected = metadata_signature(metadata, lang)
    if not expected:
        return code

    if lang == "python":
        return _upsert_python_alias(code, expected)
    if lang == "javascript":
        return _upsert_js_alias(code, expected, typescript=False)
    if lang == "typescript":
        return _upsert_js_alias(code, expected, typescript=True)
    if lang == "go":
        return _upsert_go_alias(code, expected)
    if lang == "java":
        return _upsert_java_adapter(code, expected)
    if lang == "cpp":
        return _upsert_cpp_adapter(code, expected)
    if lang == "csharp":
        return _upsert_csharp_adapter(code, expected)
    return code

