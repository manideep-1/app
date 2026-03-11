"""
Validate problem content against the learning-first schema.
Run from backend: python scripts/validate_problem_content.py

Checks:
- No problem uses a single "Solution" that is optimal-only (solutions must be from get_solutions_for_problem in learning order).
- Problems with solutions have at least 2 approaches (Brute Force then Better/Optimal).
- Approaches have intuition, algorithm, code in as many languages as possible.
- Prerequisites and common_pitfalls are present where expected.
"""
import sys
from pathlib import Path

# Add parent so we can import seed_solutions
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from seed_solutions import get_solutions_for_problem, SOLUTIONS, RICH_SOLUTIONS


def main():
    errors = []
    warnings = []
    all_titles = set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys())

    for title in sorted(all_titles):
        data = get_solutions_for_problem(title)
        if not data:
            errors.append(f"{title}: get_solutions_for_problem returned None")
            continue

        approaches = data.get("approaches") or []
        if len(approaches) < 2:
            warnings.append(f"{title}: has only {len(approaches)} approach(es); recommend at least 2 (Brute Force + Optimal/Better)")

        # Check first approach is Brute Force (or similar)
        if approaches:
            first_title = (approaches[0].get("title") or "").lower()
            if "brute" not in first_title and "1." not in first_title:
                warnings.append(f"{title}: first approach is '{approaches[0].get('title')}'; expected Brute Force first")

        for i, app in enumerate(approaches):
            has_intuition = bool((app.get("intuition") or "").strip())
            has_algorithm = bool((app.get("algorithm") or "").strip())
            has_complexity = bool((app.get("complexity") or "").strip())
            code_langs = [k for k in ("code_python", "code_java", "code_cpp", "code_javascript", "code_go", "code_csharp", "code_c") if app.get(k)]
            if not has_intuition:
                warnings.append(f"{title} / {app.get('title')}: missing intuition")
            if not has_algorithm:
                warnings.append(f"{title} / {app.get('title')}: missing algorithm")
            if not has_complexity:
                warnings.append(f"{title} / {app.get('title')}: missing complexity")
            if len(code_langs) < 2:
                warnings.append(f"{title} / {app.get('title')}: code in only {len(code_langs)} language(s); recommend 2+ (e.g. Python + Java)")

        if title in RICH_SOLUTIONS:
            rich = RICH_SOLUTIONS[title]
            if not (rich.get("prerequisites") or []):
                warnings.append(f"{title}: no prerequisites in RICH_SOLUTIONS")
            if not (rich.get("common_pitfalls") or "").strip():
                warnings.append(f"{title}: no common_pitfalls in RICH_SOLUTIONS (recommend at least 3)")

    if errors:
        print("ERRORS:")
        for e in errors:
            print("  ", e)
    if warnings:
        print("WARNINGS:")
        for w in warnings:
            print("  ", w)

    if errors:
        sys.exit(1)
    print("Validation finished. No hard errors.")
    if warnings:
        print(f"({len(warnings)} warning(s) — see above)")


if __name__ == "__main__":
    main()
