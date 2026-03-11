# Solution Generation Pipeline (5-Stage Architecture)

**No single-shot AI generation.** All solutions must be produced by this pipeline and validated before save.

---

## Overview

| Stage | Purpose | Output | On failure |
|-------|--------|--------|------------|
| 1 | Structure only | patternRecognition, approaches (title, intuition, algorithm), dryRun, edgeCases, pitfalls. **NO CODE.** | Reject; do not proceed |
| 2 | Code per approach per language | One code block per (approach_index, language). Signature from schema. | Retry that language only (max 2 retries) |
| 3 | Compilation validation | Each (approach, lang) run in judge with one test case | Regenerate that language only; re-run Stage 3 |
| 4 | Content validation | ≥2 approaches, all 6 languages, dry run, complexity, no placeholders | Regenerate missing sections only |
| 5 | Final merge | Single solution dict | N/A (merge only) |

---

## Critical Rules

1. **Never trust raw AI output** — every stage validates before proceeding.
2. **Never save unvalidated content** — Stage 4 must pass before save.
3. **Never regenerate entire solution if only one language fails** — regenerate that language only (Stage 2 + Stage 3 retry).
4. **Signature schema is single source of truth** — code generation receives exact signature per language from `function_metadata` / `generate_starter`.
5. **Hard fail if any language missing** — do not publish with empty code blocks.

---

## Implementation

- **Pipeline module:** `backend/solution_generation_pipeline.py`
  - `stage1_generate_structure(problem_title, problem_description)` → structure dict or (None, errors)
  - `stage2_generate_all_code(structure, problem_title, get_signature_for_lang)` → code_by_key, errors
  - `stage3_validate_compilation(code_by_key, problem, code_executor)` → code_by_key, failed list
  - `stage4_validate_content(merged_solution)` → valid, errors
  - `stage5_merge(structure, code_by_key, complexity_by_approach)` → solution dict
  - `run_pipeline(problem, code_executor, **options)` → (solution_dict, errors)

- **Prompts:** `backend/ai/prompts.py`
  - `solution_structure_system` / `solution_structure_user` — structure only, no code
  - `solution_code_system` / `solution_code_user` — code only, one approach one language

- **Audit and rebuild:** `backend/scripts/audit_and_rebuild_solutions.py`
  - Validates all existing problems (Stage 4 rules).
  - Report: total, passed, need rebuild.
  - `--rebuild`: run pipeline for each failed problem; write to `backend/generated_solutions/<slug>.json`.
  - `--limit N`: rebuild only first N failed.
  - `--skip-compilation`: skip Stage 3 (e.g. when judge not available).

---

## Usage

```bash
# Audit only (report passed / need rebuild)
python backend/scripts/audit_and_rebuild_solutions.py

# Rebuild failed problems (writes JSON to backend/generated_solutions/)
python backend/scripts/audit_and_rebuild_solutions.py --rebuild

# Rebuild first 2 failed (for testing)
python backend/scripts/audit_and_rebuild_solutions.py --rebuild --limit 2 --skip-compilation
```

Generated JSON files can be reviewed and merged into `backend/seed_solutions.py` (e.g. into `RICH_SOLUTIONS`) or loaded by the server from a separate store.
