"""
Metadata-driven starter and driver code generation for all supported languages.
Single source of truth: function_metadata (with optional per-language types).
When return_type_by_language / type_by_language are set, exact types are used; no fallback.
"""
from typing import List, Optional
from models import ProblemFunctionMetadata, ProblemFunctionParam, Language, SUPPORTED_LANGUAGES

# Canonical type -> language-specific type (used when type_by_language not set)
TYPE_MAP = {
    "python": {
        "int": "int",
        "int[]": "List[int]",
        "integer": "int",
        "str": "str",
        "string": "str",
        "boolean": "bool",
        "bool": "bool",
        "List[int]": "List[int]",
        "List[str]": "List[str]",
        "List[List[int]]": "List[List[int]]",
        "void": "None",
        "float": "float",
        "double": "float",
    },
    "javascript": {
        "int": "number",
        "int[]": "number[]",
        "integer": "number",
        "str": "string",
        "string": "string",
        "boolean": "boolean",
        "bool": "boolean",
        "List[int]": "number[]",
        "List[str]": "string[]",
        "List[List[int]]": "number[][]",
        "void": "void",
        "float": "number",
        "double": "number",
    },
    "java": {
        "int": "int",
        "int[]": "int[]",
        "integer": "int",
        "str": "String",
        "string": "String",
        "boolean": "boolean",
        "bool": "boolean",
        "List[int]": "int[]",
        "List[str]": "String[]",
        "List[List[int]]": "int[][]",
        "void": "void",
        "float": "float",
        "double": "double",
    },
    "cpp": {
        "int": "int",
        "int[]": "vector<int>",
        "integer": "int",
        "str": "string",
        "string": "string",
        "boolean": "bool",
        "bool": "bool",
        "List[int]": "vector<int>",
        "List[str]": "vector<string>",
        "List[List[int]]": "vector<vector<int>>",
        "void": "void",
        "float": "float",
        "double": "double",
    },
    "c": {
        "int": "int",
        "int[]": "int*",
        "integer": "int",
        "str": "char*",
        "string": "char*",
        "boolean": "int",
        "bool": "int",
        "void": "void",
        "float": "float",
        "double": "double",
    },
    "go": {
        "int": "int",
        "int[]": "[]int",
        "integer": "int",
        "str": "string",
        "string": "string",
        "boolean": "bool",
        "bool": "bool",
        "List[int]": "[]int",
        "List[str]": "[]string",
        "List[List[int]]": "[][]int",
        "void": "",
        "float": "float64",
        "double": "float64",
    },
    "csharp": {
        "int": "int",
        "int[]": "int[]",
        "integer": "int",
        "str": "string",
        "string": "string",
        "boolean": "bool",
        "bool": "bool",
        "List[int]": "int[]",
        "List[str]": "string[]",
        "List[List[int]]": "int[][]",
        "void": "void",
        "float": "float",
        "double": "double",
    },
    "typescript": {
        "int": "number",
        "int[]": "number[]",
        "integer": "number",
        "str": "string",
        "string": "string",
        "boolean": "boolean",
        "bool": "boolean",
        "List[int]": "number[]",
        "List[str]": "string[]",
        "List[List[int]]": "number[][]",
        "void": "void",
        "float": "number",
        "double": "number",
    },
}


def _map_type(canonical: str, lang: str) -> str:
    c = (canonical or "int").strip()
    return TYPE_MAP.get(lang, {}).get(c) or TYPE_MAP["python"].get(c) or c


def _get_return_type(metadata: ProblemFunctionMetadata, lang: str) -> str:
    """Return type for language: use return_type_by_language if set, else map canonical."""
    if metadata.return_type_by_language and lang in metadata.return_type_by_language:
        t = (metadata.return_type_by_language or {}).get(lang)
        if t is not None and str(t).strip():
            return str(t).strip()
    return _map_type(metadata.return_type or "", lang)


def _get_param_type(param: ProblemFunctionParam, lang: str) -> str:
    """Parameter type for language: use type_by_language if set, else map canonical."""
    if param.type_by_language and lang in param.type_by_language:
        t = (param.type_by_language or {}).get(lang)
        if t is not None and str(t).strip():
            return str(t).strip()
    return _map_type(param.type or "", lang)


def _validate_signature_for_language(metadata: ProblemFunctionMetadata, lang: str) -> None:
    """Raise ValueError if per-language types are required but missing for this language."""
    if not metadata.return_type_by_language:
        return
    if lang not in (metadata.return_type_by_language or {}):
        raise ValueError(f"Problem signature missing return type for language: {lang}")
    rt = (metadata.return_type_by_language or {}).get(lang)
    if not rt or not str(rt).strip():
        raise ValueError(f"Problem signature has empty return type for language: {lang}")
    for i, p in enumerate(metadata.parameters or []):
        if p.type_by_language and lang not in (p.type_by_language or {}):
            raise ValueError(f"Problem signature missing parameter '{p.name}' type for language: {lang}")
        if p.type_by_language:
            pt = (p.type_by_language or {}).get(lang)
            if not pt or not str(pt).strip():
                raise ValueError(f"Problem signature has empty type for parameter '{p.name}' and language: {lang}")


def _default_return_value(return_type: str, lang: str) -> str:
    """Return a safe default for the return type (used in starter body)."""
    rt = (return_type or "").strip().lower()
    if rt in ("void", "none", ""):
        if lang == "python":
            return "pass"
        if lang in ("java", "csharp"):
            return "return;"
        if lang == "go":
            return ""
        return "return;"
    # Nested arrays: int[][], vector<vector<int>>, List[List[int]], number[][], [][]int
    is_nested = (
        "[][]" in return_type
        or "vector<vector" in return_type
        or "list[list" in rt
        or "list<list" in rt
        or "number[][]" in return_type
        or "[][]int" in return_type
    )
    if is_nested or "[]" in return_type or "list" in return_type.lower() or "vector" in return_type.lower():
        if lang == "python":
            return "return []"
        if lang in ("javascript", "typescript"):
            return "return []"
        if lang == "java":
            return "return new int[0][];" if is_nested else "return new int[0];"
        if lang == "cpp":
            return "return {};"
        if lang == "go":
            return "return nil"
        if lang == "csharp":
            return "return new int[0][];" if is_nested else "return new int[0];"
    if rt in ("bool", "boolean"):
        if lang in ("java", "csharp"):
            return "return false;"
        return "return false"
    if rt in ("str", "string"):
        if lang in ("java", "csharp"):
            return 'return "";'
        return 'return ""'
    if lang in ("java", "csharp"):
        return "return 0;"
    return "return 0"


def generate_starter(metadata: ProblemFunctionMetadata, language: str) -> str:
    """Generate starter code from signature schema. Validates per-language types when set."""
    _validate_signature_for_language(metadata, language)
    fn = metadata.function_name
    ret = _get_return_type(metadata, language)
    params = metadata.parameters or []
    # For default return value use the resolved type string (handles nested etc.)
    default_ret = _default_return_value(ret, language)

    if language == "python":
        param_str = ", ".join(f"{p.name}: {_get_param_type(p, language)}" for p in params)
        needs_list_import = "List[" in ret or any("List[" in _get_param_type(p, language) for p in params)
        prefix = "from typing import List\n\n" if needs_list_import else ""
        return f"{prefix}def {fn}({param_str}) -> {ret}:\n    # Write your code here\n    {default_ret}"

    if language == "javascript":
        param_str = ", ".join(p.name for p in params)
        return f"function {fn}({param_str}) {{\n    // Write your code here\n    {default_ret}\n}}"

    if language == "java":
        param_str = ", ".join(f"{_get_param_type(p, language)} {p.name}" for p in params)
        return (
            "class Solution {\n"
            f"    public {ret} {fn}({param_str}) {{\n"
            f"        // Write your code here\n        {default_ret}\n"
            "    }\n"
            "}"
        )

    if language == "cpp":
        def cpp_param(p: ProblemFunctionParam) -> str:
            t = _get_param_type(p, language)
            # If type already has & (from type_by_language), use as-is; else use const T& for vector/string
            if "&" in t:
                return f"{t} {p.name}"
            if "vector" in t or "string" in t:
                return f"const {t}& {p.name}"
            return f"{t} {p.name}"
        param_str = ", ".join(cpp_param(p) for p in params)
        return (
            "#include <vector>\n"
            "#include <string>\n"
            "using namespace std;\n\n"
            "class Solution {\n"
            "public:\n"
            f"    {ret} {fn}({param_str}) {{\n"
            f"        // Write your code here\n        {default_ret}\n"
            "    }\n"
            "};"
        )

    if language == "c":
        param_str = ", ".join(f"{_get_param_type(p, language)} {p.name}" for p in params)
        return f"// C: implement logic; driver may vary\n{ret} {fn}({param_str}) {{\n    {default_ret}\n}}"

    if language == "go":
        param_str = ", ".join(f"{p.name} {_get_param_type(p, language)}" for p in params)
        ret_go = ret if ret else ""
        if ret_go:
            ret_go = " " + ret_go
        return f"func {fn}({param_str}){ret_go} {{\n\t// Write your code here\n\t{default_ret}\n}}"

    if language == "csharp":
        param_str = ", ".join(f"{_get_param_type(p, language)} {p.name}" for p in params)
        return (
            "public class Solution {\n"
            f"    public {ret} {fn}({param_str}) {{\n"
            f"        // Write your code here\n        {default_ret}\n"
            "    }\n"
            "}"
        )

    if language == "typescript":
        param_str = ", ".join(f"{p.name}: {_get_param_type(p, language)}" for p in params)
        return f"function {fn}({param_str}): {ret} {{\n    // Write your code here\n    {default_ret}\n}}"

    return ""


def _is_nested_array_return(metadata: ProblemFunctionMetadata, language: str) -> bool:
    """True if return type is nested array (e.g. int[][], vector<vector<int>>, List[List[int]])."""
    rt = _get_return_type(metadata, language)
    if not rt:
        return False
    rt_lower = rt.lower()
    return (
        "[][]" in rt
        or "vector<vector" in rt_lower
        or "list[list" in rt_lower
        or "list<list" in rt_lower
        or "number[][]" in rt
        or "[][]int" in rt
    )


def _is_string_array_type(type_text: str) -> bool:
    t = (type_text or "").strip().lower()
    if ("[]" not in t) and ("list" not in t):
        return False
    return ("str" in t) or ("string" in t) or ("char" in t)


def generate_driver(
    metadata: ProblemFunctionMetadata,
    language: str,
    input_spec: List[dict],
) -> str:
    """
    Generate driver code that: parses stdin, calls the solution function, prints result.
    input_spec: list of {"name": str, "type": str} in order of stdin (e.g. [{"name": "numbers", "type": "int[]"}, {"name": "target", "type": "int"}]).
    """
    fn = metadata.function_name
    params = metadata.parameters or []
    if not params and input_spec:
        params = [ProblemFunctionParam(name=s.get("name", "x"), type=s.get("type", "str")) for s in input_spec]
    if not params:
        params = [ProblemFunctionParam(name="input", type="str")]

    if language == "python":
        lines = ["import sys", "data = sys.stdin.read().splitlines()"]
        parse_lines = []
        for i, p in enumerate(params):
            pt = (p.type or "").strip().lower()
            src = f"_line_{i}"
            parse_lines.append(f"{src} = data[{i}] if {i} < len(data) else ''")
            if "[][]" in pt or "list[list" in pt or "list<list" in pt:
                parse_lines.append(f"{p.name} = list(map(int, {src}.split())) if {src}.strip() else []")
            elif "[]" in pt or "list" in pt:
                if _is_string_array_type(p.type or ""):
                    parse_lines.append(f"{p.name} = {src}.split() if {src}.strip() else []")
                else:
                    parse_lines.append(f"{p.name} = list(map(int, {src}.split())) if {src}.strip() else []")
            elif pt in ("int", "integer"):
                parse_lines.append(f"{p.name} = int({src}) if {src}.strip() else 0")
            elif pt in ("str", "string"):
                parse_lines.append(f"{p.name} = {src}")
            elif pt in ("bool", "boolean"):
                parse_lines.append(f"{p.name} = {src}.strip().lower() == 'true'")
            else:
                parse_lines.append(f"{p.name} = {src}")
        lines.extend(parse_lines)
        args = ", ".join(p.name for p in params)
        lines.append(f"result = {fn}({args})")
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            first_param = params[0] if params else None
            first_pt = ((first_param.type if first_param else "") or "").strip().lower()
            first_name = first_param.name if first_param else ""
            if "[][]" in first_pt or "list[list" in first_pt or "list<list" in first_pt:
                lines.append(f"if {first_name}: [print(' '.join(map(str, row))) for row in {first_name}]")
            elif "[]" in first_pt or "list" in first_pt:
                lines.append(f"print(' '.join(map(str, {first_name})) if {first_name} else '')")
            elif first_pt in ("bool", "boolean"):
                lines.append(f"print('true' if {first_name} else 'false')")
            elif first_name:
                lines.append(f"print({first_name})")
            else:
                lines.append("# no return to print")
        elif _is_nested_array_return(metadata, "python"):
            lines.append("if result: [print(' '.join(map(str, row))) for row in result]")
        elif "[]" in metadata.return_type or "list" in metadata.return_type.lower():
            lines.append("print(' '.join(map(str, result)) if result else '')")
        elif rt in ("bool", "boolean"):
            lines.append("print('true' if result else 'false')")
        else:
            lines.append("print(result)")
        return "if __name__ == \"__main__\":\n    " + "\n    ".join(lines)

    if language == "javascript":
        parts = [
            "const readline = require('readline');",
            "const rl = readline.createInterface({ input: process.stdin });",
            "const lines = [];",
            "rl.on('line', (line) => lines.push(line));",
            "rl.on('close', () => {",
        ]
        for i, p in enumerate(params):
            pt = (p.type or "").strip().lower()
            parts.append(f"    const _line{i} = (lines[{i}] !== undefined ? lines[{i}] : '');")
            if "[][]" in pt or "list[list" in pt or "list<list" in pt:
                parts.append(f"    const {p.name} = _line{i}.trim() ? _line{i}.trim().split(/\\s+/).map(Number) : [];")
            elif "[]" in pt or "list" in pt:
                if _is_string_array_type(p.type or ""):
                    parts.append(f"    const {p.name} = _line{i}.trim() ? _line{i}.trim().split(/\\s+/) : [];")
                else:
                    parts.append(f"    const {p.name} = _line{i}.trim() ? _line{i}.trim().split(/\\s+/).map(Number) : [];")
            elif pt in ("int", "integer"):
                parts.append(f"    const {p.name} = _line{i}.trim() ? parseInt(_line{i}.trim(), 10) : 0;")
            else:
                parts.append(f"    const {p.name} = _line{i};")
        args = ", ".join(p.name for p in params)
        parts.append(f"    const result = {fn}({args});")
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            first_param = params[0] if params else None
            first_pt = ((first_param.type if first_param else "") or "").strip().lower()
            first_name = first_param.name if first_param else ""
            if "[][]" in first_pt or "list[list" in first_pt or "list<list" in first_pt:
                parts.append(f"    if ({first_name} && {first_name}.length) {{ {first_name}.forEach(row => console.log(row.join(' '))); }}")
            elif "[]" in first_pt or "list" in first_pt:
                parts.append(f"    console.log({first_name} && {first_name}.length ? {first_name}.join(' ') : '');")
            elif first_pt in ("bool", "boolean"):
                parts.append(f"    console.log({first_name} ? 'true' : 'false');")
        elif _is_nested_array_return(metadata, "javascript"):
            parts.append("    if (result && result.length) { result.forEach(row => console.log(row.join(' '))); }")
        elif "[]" in metadata.return_type or "list" in metadata.return_type.lower():
            parts.append("    console.log(result && result.length ? result.join(' ') : '');")
        elif rt in ("bool", "boolean"):
            parts.append("    console.log(result ? 'true' : 'false');")
        else:
            parts.append("    console.log(result);")
        parts.append("});")
        return "\n".join(parts)

    if language == "java":
        # Main class: read line-by-line, parse, call Solution, print. One line per parameter in order.
        first_param = params[0] if params else None
        first_pt = ((first_param.type if first_param else "") or "").strip().lower()
        parts = [
            "import java.util.*;",
            "public class Main {",
            "    public static void main(String[] args) {",
            "        Scanner sc = new Scanner(System.in);",
        ]
        for p in params:
            ptype = (p.type or "")
            pt = ptype.strip().lower()
            if "[][]" in pt or "list<list" in pt:
                parts.append(f"        String _dims_line_{p.name} = (sc.hasNextLine() ? sc.nextLine() : \"\").trim();")
                parts.append(f"        String[] _dims_{p.name} = _dims_line_{p.name}.isEmpty() ? new String[0] : _dims_line_{p.name}.split(\"\\\\s+\");")
                parts.append(f"        int _rows_{p.name} = _dims_{p.name}.length > 0 && !_dims_{p.name}[0].isEmpty() ? Integer.parseInt(_dims_{p.name}[0]) : 0;")
                parts.append(f"        int _cols_{p.name} = _dims_{p.name}.length > 1 && !_dims_{p.name}[1].isEmpty() ? Integer.parseInt(_dims_{p.name}[1]) : 0;")
                parts.append(f"        int[][] {p.name} = new int[_rows_{p.name}][_cols_{p.name}];")
                parts.append(f"        for (int i = 0; i < _rows_{p.name}; i++) {{")
                parts.append(f"            String _row_line_{p.name} = (sc.hasNextLine() ? sc.nextLine() : \"\").trim();")
                parts.append(f"            String[] _row_{p.name} = _row_line_{p.name}.isEmpty() ? new String[0] : _row_line_{p.name}.split(\"\\\\s+\");")
                parts.append(f"            for (int j = 0; j < _cols_{p.name} && j < _row_{p.name}.length; j++) {p.name}[i][j] = Integer.parseInt(_row_{p.name}[j]);")
                parts.append("        }")
            elif "[]" in pt or "list" in pt or "int[]" in ptype:
                parts.append(f"        String _line_{p.name} = (sc.hasNextLine() ? sc.nextLine() : \"\").trim();")
                parts.append(f"        String[] _a_{p.name} = _line_{p.name}.isEmpty() ? new String[0] : _line_{p.name}.split(\"\\\\s+\");")
                parts.append(f"        int[] {p.name} = new int[_a_{p.name}.length];")
                parts.append(f"        for (int i = 0; i < _a_{p.name}.length; i++) {p.name}[i] = Integer.parseInt(_a_{p.name}[i]);")
            elif pt in ("int", "integer"):
                parts.append(f"        String _line_{p.name} = sc.hasNextLine() ? sc.nextLine().trim() : \"\";")
                parts.append(f"        int {p.name} = _line_{p.name}.isEmpty() ? 0 : Integer.parseInt(_line_{p.name});")
            elif "string" in pt or "str" in pt:
                parts.append(f"        String {p.name} = sc.hasNextLine() ? sc.nextLine().trim() : \"\";")
            else:
                parts.append(f"        String {p.name} = sc.hasNextLine() ? sc.nextLine() : \"\";")
        parts.append("        Solution sol = new Solution();")
        args = ", ".join(p.name for p in params)
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            parts.append(f"        sol.{fn}({args});")
            # In-place problems usually mutate the first array/matrix argument.
            if "[][]" in first_pt or "list<list" in first_pt:
                first_name = first_param.name if first_param else "result"
                parts.append(f"        if ({first_name} != null) {{")
                parts.append(f"            for (int[] row : {first_name}) {{")
                parts.append("                if (row == null) { System.out.println(); continue; }")
                parts.append("                for (int i = 0; i < row.length; i++) { if (i > 0) System.out.print(\" \"); System.out.print(row[i]); }")
                parts.append("                System.out.println();")
                parts.append("            }")
                parts.append("        }")
            elif "[]" in first_pt or "list" in first_pt:
                first_name = first_param.name if first_param else "result"
                parts.append(f"        if ({first_name} != null) {{ for (int i = 0; i < {first_name}.length; i++) {{ if (i > 0) System.out.print(\" \"); System.out.print({first_name}[i]); }} }}")
                parts.append("        System.out.println();")
            else:
                parts.append("        // no output")
        else:
            parts.append(f"        {_get_return_type(metadata, 'java')} result = sol.{fn}({args});")
        if rt in ("void", "none"):
            pass
        elif _is_nested_array_return(metadata, "java"):
            parts.append("        if (result != null) { for (int[] row : result) { if (row != null && row.length > 0) { for (int i = 0; i < row.length; i++) { if (i > 0) System.out.print(\" \"); System.out.print(row[i]); } System.out.println(); } } }")
        elif "[]" in metadata.return_type or "int[]" in metadata.return_type:
            parts.append("        if (result != null) { for (int i = 0; i < result.length; i++) { if (i > 0) System.out.print(\" \"); System.out.print(result[i]); } }")
            parts.append("        System.out.println();")
        elif rt in ("bool", "boolean"):
            parts.append("        System.out.println(result ? \"true\" : \"false\");")
        else:
            parts.append("        System.out.println(result);")
        parts.append("        sc.close();")
        parts.append("    }")
        parts.append("}")
        return "\n".join(parts)

    if language == "cpp":
        parts = [
            "#include <iostream>",
            "#include <sstream>",
            "#include <vector>",
            "#include <string>",
            "using namespace std;",
            "",
            "int main() {",
        ]
        for p in params:
            pt = (p.type or "").strip().lower()
            if "[]" in pt or "vector" in _map_type(p.type, "cpp"):
                parts.append(f"    string line; getline(cin, line);")
                parts.append(f"    istringstream iss(line);")
                parts.append(f"    vector<int> {p.name}; int x; while (iss >> x) {p.name}.push_back(x);")
            elif pt in ("int", "integer"):
                parts.append(f"    int {p.name}; cin >> {p.name};")
            else:
                parts.append(f"    string {p.name}; getline(cin, {p.name});")
        parts.append("    Solution sol;")
        args = ", ".join(p.name for p in params)
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            parts.append(f"    sol.{fn}({args});")
        else:
            parts.append(f"    auto result = sol.{fn}({args});")
        if _is_nested_array_return(metadata, "cpp"):
            parts.append("    for (const auto& row : result) { for (size_t i = 0; i < row.size(); i++) { if (i) cout << ' '; cout << row[i]; } cout << endl; }")
        elif "[]" in metadata.return_type or "vector" in metadata.return_type:
            parts.append("    for (size_t i = 0; i < result.size(); i++) { if (i) cout << ' '; cout << result[i]; }")
            parts.append("    cout << endl;")
        elif rt not in ("void", "none"):
            parts.append("    cout << result << endl;")
        parts.append("    return 0;")
        parts.append("}")
        return "\n".join(parts)

    if language == "go":
        # Go requires package main first; driver is a full file with ___USER_CODE___ placeholder for build_full_code to inject user code.
        parts = [
            "package main",
            "",
            "import (",
            '\t"bufio"',
            '\t"fmt"',
            '\t"os"',
            '\t"strconv"',
            '\t"strings"',
            ")",
            "",
            "___USER_CODE___",
            "",
            "func main() {",
            "\tscanner := bufio.NewScanner(os.Stdin)",
            "\tlines := []string{}",
            "\tfor scanner.Scan() { lines = append(lines, scanner.Text()) }",
            f"\tif len(lines) < {len(params)} {{ return }}",
            "",
        ]
        for i, p in enumerate(params):
            pt = (p.type or "").strip().lower()
            if "[]" in pt or "int[]" in pt or "list" in pt:
                parts.append(f"\t_a := strings.Fields(lines[{i}])")
                parts.append(f"\t{p.name} := make([]int, len(_a))")
                parts.append(f"\tfor ii, s := range _a {{ v, _ := strconv.Atoi(s); {p.name}[ii] = v }}")
            elif pt in ("int", "integer"):
                parts.append(f"\t{p.name}, _ := strconv.Atoi(strings.TrimSpace(lines[{i}]))")
            else:
                parts.append(f"\t{p.name} := strings.TrimSpace(lines[{i}])")
        args = ", ".join(p.name for p in params)
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            parts.append(f"\t{fn}({args})")
        else:
            parts.append(f"\tresult := {fn}({args})")
        if rt in ("void", "none"):
            pass
        elif _is_nested_array_return(metadata, "go"):
            parts.append("\tfor _, row := range result { for i, v := range row { if i > 0 { fmt.Print(\" \") }; fmt.Print(v) }; fmt.Println() }")
        elif "[]" in metadata.return_type or "int[]" in metadata.return_type.lower():
            parts.append("\tif len(result) > 0 { for i, v := range result { if i > 0 { fmt.Print(\" \") }; fmt.Print(v) } }")
            parts.append("\tfmt.Println()")
        elif rt in ("bool", "boolean"):
            parts.append("\tif result { fmt.Println(\"true\") } else { fmt.Println(\"false\") }")
        else:
            parts.append("\tfmt.Println(result)")
        parts.append("}")
        return "\n".join(parts)

    if language == "csharp":
        parts = [
            "using System;",
            "using System.Collections.Generic;",
            "using System.Linq;",
            "",
            "class Program {",
            "    static void Main() {",
            "        var lines = new List<string>();",
            "        string line;",
            "        while ((line = Console.ReadLine()) != null) lines.Add(line);",
            "        int idx = 0;",
            "",
        ]
        for p in params:
            pt = (p.type or "").strip().lower()
            if "[]" in pt or "list" in pt or "int[]" in pt:
                parts.append(f"        var _a = (lines.Count > idx ? lines[idx++] : \"\").Split();")
                parts.append(f"        int[] {p.name} = Array.ConvertAll(_a, int.Parse);")
            elif pt in ("int", "integer"):
                parts.append(f"        int {p.name} = lines.Count > idx ? int.Parse(lines[idx++].Trim()) : 0;")
            else:
                parts.append(f"        string {p.name} = lines.Count > idx ? lines[idx++].Trim() : \"\";")
        parts.append("        var sol = new Solution();")
        args = ", ".join(p.name for p in params)
        rt = (metadata.return_type or "").strip().lower()
        if rt in ("void", "none"):
            parts.append(f"        sol.{fn}({args});")
            parts.append("        // no output")
        else:
            parts.append(f"        var result = sol.{fn}({args});")
        if rt in ("void", "none"):
            pass
        elif _is_nested_array_return(metadata, "csharp"):
            parts.append("        if (result != null) foreach (var row in result) Console.WriteLine(string.Join(\" \", row));")
        elif "[]" in metadata.return_type or "int[]" in metadata.return_type.lower():
            parts.append("        if (result != null) Console.WriteLine(string.Join(\" \", result));")
            parts.append("        else Console.WriteLine();")
        elif rt in ("bool", "boolean"):
            parts.append("        Console.WriteLine(result ? \"true\" : \"false\");")
        else:
            parts.append("        Console.WriteLine(result);")
        parts.append("    }")
        parts.append("}")
        return "\n".join(parts)

    if language == "typescript":
        parts = [
            "const readline = require('readline');",
            "const rl = readline.createInterface({ input: process.stdin });",
            "const lines: string[] = [];",
            "rl.on('line', (line: string) => lines.push(line));",
            "rl.on('close', () => {",
        ]
        for i, p in enumerate(params):
            pt = (p.type or "").strip().lower()
            if "[]" in pt or "list" in pt:
                parts.append(f"    const {p.name} = lines[{i}] ? lines[{i}].split(' ').map(Number) : [];")
            elif pt in ("int", "integer"):
                parts.append(f"    const {p.name} = parseInt(lines[{i}] || '0');")
            else:
                parts.append(f"    const {p.name} = lines[{i}] || '';")
        args = ", ".join(p.name for p in params)
        parts.append(f"    const result = {fn}({args});")
        rt = (metadata.return_type or "").strip().lower()
        if _is_nested_array_return(metadata, "typescript"):
            parts.append("    if (result && result.length) { result.forEach((row: number[]) => console.log(row.join(' '))); }")
        elif "[]" in metadata.return_type or "list" in metadata.return_type.lower():
            parts.append("    console.log(result && result.length ? result.join(' ') : '');")
        elif rt in ("bool", "boolean"):
            parts.append("    console.log(result ? 'true' : 'false');")
        else:
            parts.append("    console.log(result);")
        parts.append("});")
        return "\n".join(parts)

    return ""


def generate_starter_and_driver(
    metadata: ProblemFunctionMetadata,
    input_spec: Optional[List[dict]] = None,
) -> dict:
    """Return dict with starter_code_* and driver_code_* for all supported languages."""
    input_spec = input_spec or [{"name": p.name, "type": p.type} for p in (metadata.parameters or [])]
    out = {}
    for lang in ("python", "javascript", "java", "cpp", "c", "go", "csharp", "typescript"):
        out[f"starter_code_{lang}"] = generate_starter(metadata, lang)
        out[f"driver_code_{lang}"] = generate_driver(metadata, lang, input_spec)
    return out
