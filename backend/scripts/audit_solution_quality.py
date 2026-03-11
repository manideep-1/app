"""
Audit solution quality against docs/SOLUTION_QUALITY_STANDARD.md (NeetCode-level).

Run from repo root: python backend/scripts/audit_solution_quality.py
Or from backend: python scripts/audit_solution_quality.py

Outputs:
- Per-problem: quality tier (low / medium / high), score, missing sections.
- Summary: counts by tier, list of problems needing full rewrite.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from seed_solutions import get_solutions_for_problem, SOLUTIONS, RICH_SOLUTIONS

REQUIRED_LANGS = ("code_python", "code_java", "code_cpp", "code_javascript", "code_go", "code_csharp")
MIN_APPROACHES = 2
MIN_PITFALLS_ITEMS = 3
MIN_INTUITION_LEN = 80
MIN_COMMON_PITFALLS_LEN = 150


def _count_code_langs(approach):
    return sum(1 for k in REQUIRED_LANGS if (approach.get(k) or "").strip())


def _has_brute_first(approaches):
    if not approaches:
        return False
    first = (approaches[0].get("title") or "").lower()
    return "brute" in first or first.startswith("1.")


def audit_one(title):
    data = get_solutions_for_problem(title, enforce_signature=False)
    if not data:
        return {"tier": "none", "score": 0, "missing": ["no solution data"], "approaches": 0}

    approaches = data.get("approaches") or []
    missing = []
    score = 0
    max_score = 0

    # Approaches count (0–2)
    max_score += 2
    if len(approaches) >= 2:
        score += 2
    elif len(approaches) == 1:
        score += 1
        missing.append("need at least 2 approaches (Brute + Optimal/Better)")
    else:
        missing.append("no approaches")

    # Brute first (0–1)
    max_score += 1
    if approaches and _has_brute_first(approaches):
        score += 1
    elif approaches:
        missing.append("first approach should be Brute Force")

    # Per-approach: intuition, algorithm, complexity, code langs (max 8 pts total)
    ap_score = 0
    for app in approaches:
        has_intuition = bool((app.get("intuition") or "").strip())
        has_algorithm = bool((app.get("algorithm") or "").strip())
        has_complexity = bool((app.get("complexity") or "").strip())
        n_langs = _count_code_langs(app)
        if has_intuition:
            ap_score += 1
        else:
            missing.append(f"{app.get('title', '?')}: missing intuition")
        if has_algorithm:
            ap_score += 1
        else:
            missing.append(f"{app.get('title', '?')}: missing algorithm")
        if has_complexity:
            ap_score += 1
        else:
            missing.append(f"{app.get('title', '?')}: missing complexity")
        if n_langs >= 6:
            ap_score += 2
        elif n_langs >= 4:
            ap_score += 1
        elif n_langs < 2:
            missing.append(f"{app.get('title', '?')}: code in only {n_langs} of 6 required languages")
    max_score += 8
    score += min(ap_score, 8)

    # Prerequisites (0–1)
    max_score += 1
    prereq = data.get("prerequisites") or []
    if prereq and len(prereq) >= 1:
        score += 1
    else:
        missing.append("missing prerequisites")

    # common_pitfalls (0–1)
    max_score += 1
    pitfalls_str = (data.get("common_pitfalls") or "").strip()
    pitfalls_list = data.get("pitfalls") or []
    if pitfalls_str and len(pitfalls_str) >= MIN_COMMON_PITFALLS_LEN:
        score += 1
    elif pitfalls_list and len(pitfalls_list) >= MIN_PITFALLS_ITEMS:
        score += 1
    else:
        if not pitfalls_str and not pitfalls_list:
            missing.append("missing common_pitfalls (need ≥3 pitfalls)")
        elif pitfalls_str and len(pitfalls_str) < MIN_COMMON_PITFALLS_LEN:
            missing.append("common_pitfalls too short (recommend ≥3 pitfalls, ~150+ chars)")

    # Premium: pattern_recognition, dry_run, edge_cases, interview_tips (0–4)
    max_score += 4
    for key, label in (
        ("pattern_recognition", "pattern recognition"),
        ("dry_run", "dry run"),
        ("edge_cases", "edge cases"),
        ("interview_tips", "interview tips"),
    ):
        val = (data.get(key) or "").strip()
        if val and len(val) >= 50:
            score += 1
        else:
            missing.append(f"missing or too short: {label}")

    # Normalize score to 0–100 for readability
    pct = (score / max_score * 100) if max_score else 0

    if pct >= 75:
        tier = "high"
    elif pct >= 40:
        tier = "medium"
    else:
        tier = "low"

    return {
        "tier": tier,
        "score": score,
        "max_score": max_score,
        "pct": round(pct, 1),
        "missing": missing,
        "approaches": len(approaches),
        "in_rich": title in RICH_SOLUTIONS,
    }


def main():
    all_titles = sorted(set(SOLUTIONS.keys()) | set(RICH_SOLUTIONS.keys()))
    results = []
    for title in all_titles:
        r = audit_one(title)
        r["title"] = title
        results.append(r)

    by_tier = {"high": [], "medium": [], "low": [], "none": []}
    for r in results:
        by_tier[r["tier"]].append(r["title"])

    print("=" * 60)
    print("SOLUTION QUALITY AUDIT (NeetCode-level standard)")
    print("=" * 60)
    print(f"\nTotal problems: {len(results)}")
    print(f"  High (≥75%):  {len(by_tier['high'])}")
    print(f"  Medium (40–74%): {len(by_tier['medium'])}")
    print(f"  Low (<40%):   {len(by_tier['low'])}")
    print(f"  No solution:  {len(by_tier['none'])}")

    print("\n--- LOW QUALITY (need full upgrade) ---")
    for r in results:
        if r["tier"] != "low":
            continue
        print(f"\n  {r['title']} ({r['pct']}%)")
        for m in r["missing"][:12]:
            print(f"    - {m}")
        if len(r["missing"]) > 12:
            print(f"    ... and {len(r['missing']) - 12} more")

    print("\n--- MEDIUM (improve with pattern, dry run, edge cases, tips) ---")
    for t in by_tier["medium"][:15]:
        r = next(x for x in results if x["title"] == t)
        print(f"  {t} ({r['pct']}%) — missing: {', '.join(r['missing'][:5])}")
    if len(by_tier["medium"]) > 15:
        print(f"  ... and {len(by_tier['medium']) - 15} more")

    print("\n--- HIGH (premium-ready) ---")
    for t in by_tier["high"][:20]:
        r = next(x for x in results if x["title"] == t)
        print(f"  {t} ({r['pct']}%)")
    if len(by_tier["high"]) > 20:
        print(f"  ... and {len(by_tier['high']) - 20} more")

    need_rewrite = [r["title"] for r in results if r["tier"] == "low" and r["approaches"] > 0]
    print(f"\n--- RECOMMENDATION ---")
    print(f"  Full rewrite (low quality, have content): {len(need_rewrite)} problems")
    print(f"  Add premium sections to medium: {len(by_tier['medium'])} problems")
    print("  See docs/SOLUTION_QUALITY_STANDARD.md for required structure.")

    if "--csv" in sys.argv:
        import csv
        out = Path(__file__).parent.parent.parent / "solution_quality_audit.csv"
        with open(out, "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(["title", "tier", "pct", "approaches", "missing_count", "missing_sample"])
            for r in results:
                w.writerow([
                    r["title"],
                    r["tier"],
                    r["pct"],
                    r["approaches"],
                    len(r["missing"]),
                    "; ".join(r["missing"][:5]) if r["missing"] else "",
                ])
        print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
