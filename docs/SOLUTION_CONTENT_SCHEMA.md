# Mandatory Solution Content Schema (Strict)

**A solution CANNOT be saved or published unless it satisfies this schema and passes `validate_solution()`.**

No verbal-only or incomplete solutions. Every approach must have **complete, non-empty code in all supported languages**.

---

## Required structure

```json
{
  "pattern_recognition": "string (required, non-empty)",
  "approaches": [
    {
      "title": "string (required)",
      "intuition": "string (required, non-empty)",
      "algorithm": "string (required, non-empty)",
      "code": {
        "java": "string (required, non-empty, compilable)",
        "python": "string (required, non-empty, runnable)",
        "cpp": "string (required, non-empty, compilable)",
        "javascript": "string (required, non-empty, runnable)",
        "go": "string (required, non-empty, compilable)",
        "csharp": "string (required, non-empty, compilable)"
      },
      "complexity": {
        "time": "string (e.g. O(n))",
        "space": "string (e.g. O(1))"
      }
    }
  ],
  "dry_run": "string (required, non-empty)",
  "edge_cases": "string (required, non-empty)",
  "pitfalls": "string or array (required)"
}
```

**Backend field names** (snake_case in seed_solutions / API):

- `pattern_recognition` (or `patternRecognition` in JSON from clients)
- `approaches[].code_java`, `code_python`, `code_cpp`, `code_javascript`, `code_go`, `code_csharp` (each **required** per approach)
- `dry_run`, `edge_cases`, `pitfalls` / `common_pitfalls`

---

## Validation rules (enforced by `validate_solution()`)

| Rule | Reject if |
|------|-----------|
| Approaches | Fewer than 1 approach |
| Code per language | **Any** of java, python, cpp, javascript, go, csharp is missing or empty for **any** approach |
| Code length | Any code block shorter than `MIN_CODE_LENGTH` (e.g. 50 characters) |
| Placeholders | Any code contains `...`, `TODO`, `# ...`, `// ...` (ellipsis/placeholder) |
| Pseudo-code only | Code has no function/class definition (e.g. no `def `, `function `, `public `, etc.) |
| Empty sections | Any required text field (intuition, algorithm, complexity) is empty |

If **any** language code is empty → **reject**. Do not publish.

---

## Compile test (mandatory before publish)

For each generated language solution:

1. Inject into execution environment (with problem driver/starter contract).
2. Compile (or parse for interpreted languages).
3. Run at least one example test case.
4. If compile or run fails → regenerate that language only; revalidate.

---

## Auto-retry (for AI generation pipelines)

If validation fails after generation:

1. Call `get_validation_errors(result)` → get list of missing languages / errors.
2. Send corrective instruction: e.g. *"Code blocks missing for languages: Java, C++. Generate complete, compilable code for these languages only."*
3. Regenerate only the missing sections.
4. Merge into solution; call `validate_solution()` again.
5. Retry up to **3 times**. If still failing → log error and do not save.

---

## Rejected content

- Solutions with **no code blocks** (only prose).
- **Only explanation text** without code.
- **Pseudo-code only** (e.g. "for i in array: do something" with no real syntax).
- **Incomplete code** (missing return, missing closing brace, etc.).
- **Non-compilable** snippets (fails compile test).

Use `solution_validator.validate_solution(solution)` before any save or publish. Use `audit_solution_code_integrity.py` to mass-audit existing problems and generate a missing-languages report.

---

## Strict vs lenient

- **Strict (default):** Every approach must have non-empty code for all 6 languages (Java, Python, C++, JavaScript, Go, C#). Used for **publish/save** and for the default audit.
- **Lenient:** Only reject verbal-only (no code at all). Use `validate_solution_verbal_only(solution)` or run the audit with `--lenient` to find approaches with zero code blocks while migrating to full 6-language coverage.
