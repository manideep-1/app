#!/usr/bin/env python3
"""
Audit all problems with solutions: registry membership, approach count, and
language coverage across every approach after normalization.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from seed_solutions import SOLUTIONS, RICH_SOLUTIONS, get_solutions_for_problem
from problem_metadata_registry import REGISTRY

REQUIRED_LANGS = ("python", "javascript", "java", "cpp", "go", "csharp")
CODE_KEYS = [f"code_{l}" for l in REQUIRED_LANGS]

def main():
    in_registry = set(REGISTRY.keys())
    solution_titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    missing_registry = []
    missing_langs = {}  # title -> set of missing lang
    single_approach = []
    ok = []

    for title in solution_titles:
        sol = get_solutions_for_problem(title)
        if not sol or not sol.get("approaches"):
            continue
        approaches = sol["approaches"]
        has_registry = title in in_registry
        if len(approaches) < 2:
            single_approach.append(title)
        missing = set()
        for approach in approaches:
            for lang in REQUIRED_LANGS:
                if not (approach.get(f"code_{lang}") or "").strip():
                    missing.add(lang)
        if not has_registry:
            missing_registry.append(title)
        if missing:
            missing_langs[title] = missing
        else:
            ok.append(title)

    print("=== Problems NOT in problem_metadata_registry ===")
    for t in sorted(missing_registry):
        print(" ", t)
    print(f"Total: {len(missing_registry)}")

    print("\n=== Problems with fewer than 2 approaches ===")
    for t in sorted(single_approach):
        print(" ", t)
    print(f"Total: {len(single_approach)}")

    print("\n=== Problems missing one or more solution languages (after normalization) ===")
    for t in sorted(missing_langs.keys(), key=lambda x: (-len(missing_langs[x]), x)):
        print(f"  {t}: missing {sorted(missing_langs[t])}")
    print(f"Total: {len(missing_langs)}")

    print("\n=== Problems with all 6 languages present ===")
    print(f"  {len(ok)} problems")

if __name__ == "__main__":
    main()
