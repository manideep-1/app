# Test Case Design Rules (ifelse)

## Principles

1. **Uniqueness:** No two test cases in the same problem may have identical (input, expected_output) after normalization (trim, collapse whitespace). The platform rejects duplicate test cases at seed time and in the Admin Create Problem API.
2. **Examples (visible):** 2–3 per problem, all different, often increasing in complexity.
3. **Hidden cases:** Varied (normal, edge, min/max boundary, worst-case). No repeats of visible or other hidden cases.

## Normalization

- Input and expected_output are trimmed and have runs of whitespace (including newlines) collapsed to a single space for comparison and hashing.
- Duplicate detection uses SHA256(normalized_input + "|" + normalized_expected).

## Enforcement

- **Seed:** `seed_db.py` runs `deduplicate_test_cases` then `ensure_min_visible_test_cases` then `ensure_min_hidden_test_cases`. When adding visible or hidden cases to meet minimums, it prefers sources that are not already in the set (so examples stay distinct).
- **Admin API:** `POST /problems` validates with `validate_no_duplicates_within_problem` and returns 400 if duplicates exist.
- **Detection:** Run `python scripts/detect_duplicate_test_cases.py` from `backend/` to report within-problem and across-problem duplicates.

## Adding or Editing Problems

- In seed files (e.g. `seed_problems_top100.py`, inline in `seed_db.py`), define each test case with unique input and expected_output.
- After changes, run the duplicate detection script and re-run `seed_db.py` so the database stays consistent.
