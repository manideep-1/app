# Judge Contract — Single Source of Truth

Function name, return type, and parameters are defined **once** in problem metadata. Starters, driver, and validation all derive from it.

## Canonical schema

Every problem that participates in the judge contract has:

```json
{
  "function_metadata": {
    "function_name": "maxArea",
    "return_type": "int",
    "parameters": [
      { "name": "height", "type": "vector<int>&" }
    ]
  }
}
```

- **function_name**: Exact name the user must implement (e.g. `twoSum`, `maxArea`).
- **return_type**: Canonical type (`int`, `int[]`, `boolean`, `str`, `void`, `List[int]`, etc.).
- **parameters**: Ordered list of `{ "name", "type" }` (canonical types).

This is the **single source of truth**. No hardcoded function names in starter templates, driver code, or execution.

## Flow

1. **Problem JSON** stores `function_metadata` (and optionally pre-generated starter/driver for display).
2. **Starter code** is generated from metadata per language (`starter_template_generator.generate_starter`). When the API returns a problem with `function_metadata`, starters are regenerated from metadata so the editor always shows the contract-compliant template.
3. **Driver / execution wrapper** is generated from metadata at **run/submit time** (`build_full_code` uses `generate_driver(metadata, language, input_spec)` when `function_metadata` is present). So the wrapper always calls `metadata.function_name` with the correct signature.
4. **Validation**: Before execution, `signature_validator.validate_signature` checks that user code defines the required function (by name). If not, the API returns 400: *"Function signature does not match problem definition."*
5. **Execution**: User code + metadata-generated driver is run; result is compared to test case expected output.

## Where things live

| Concern | Location | Rule |
|--------|----------|------|
| Metadata schema | `models.ProblemFunctionMetadata` | Single definition |
| Starter generation | `starter_template_generator.generate_starter` | From metadata only |
| Driver generation | `starter_template_generator.generate_driver` | From metadata only |
| Full code (user + driver) | `server.build_full_code` | Uses generated driver when metadata present |
| Signature check | `signature_validator.validate_signature` | Before run/submit |
| Run/Submit | `server.run_code`, `server.submit_code` | Validate then build_full_code then execute |

## Migration

- **Backfill metadata**: For problems without `function_metadata`, use the title → metadata registry (`problem_metadata_registry.get_metadata(title)`) and set `function_metadata` + regenerate starter/driver.
- **Regenerate from metadata**: For problems that already have `function_metadata`, regenerate all `starter_code_*` and `driver_code_*` from it so DB is consistent.

Run:

```bash
cd backend && python scripts/migrate_judge_contract.py [--dry-run] [--mongo-url URL]
```

## Frontend

- **Function name**: Use `problem.function_metadata.function_name` when present; otherwise fall back to title-derived name.
- **Starters**: When `function_metadata` is present, use server-provided `starter_code_*` as-is (already generated from metadata). No client-side replacement of `solve` with a derived name.

## Adding a new problem

1. Add metadata (admin create with `function_metadata`, or add to `problem_metadata_registry` and run migration).
2. Do **not** manually write starter templates that duplicate the function name or signature.
3. Starter and driver are generated; execution uses the same metadata at runtime.
