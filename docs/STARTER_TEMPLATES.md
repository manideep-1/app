# Starter Templates & Function Metadata

## Objective

- **Users implement only the solution function** with the correct signature (name, parameters, return type).
- **Platform handles I/O**: driver code parses stdin, calls the function, prints the return value.
- **Multi-language consistent**: Same logical signature across Python, JavaScript, Java, C++, C.

## Schema

### ProblemFunctionMetadata (models.py)

- **function_name**: e.g. `twoSum`, `maxProfit`
- **return_type**: Canonical type (`int`, `int[]`, `boolean`, `str`, `List[int]`, `void`, etc.)
- **parameters**: List of `{ name, type }` in order

### Type mapping

Canonical types are mapped per language in `starter_template_generator.TYPE_MAP` (e.g. `int[]` → Python `List[int]`, Java `int[]`, C++ `vector<int>`).

## Flow

1. **Registry** (`problem_metadata_registry.py`): Map problem title → (metadata, input_spec). input_spec defines how each parameter is read from stdin (line order and type).
2. **Generator** (`starter_template_generator.py`): From metadata (+ input_spec for driver) generates:
   - **Starter**: Function or class to implement (correct name, params, return type; default return for compile).
   - **Driver**: Parses stdin, calls the function, prints result.
3. **get_starters_for_problem** (`seed_starters.py`): If title is in registry → use generator (all 5 languages). Else use STARTERS dict or default (Python + JS only).
4. **Execution** (`code_executor.py`): `full_code = user_code + "\n\n" + driver`. User edits only the starter; driver is appended at run/submit. For Java, starter is `class Solution`, driver is `public class Main` (single file `Main.java`).

## Java / C++

- **Java**: One file `Main.java` with package-private `class Solution` and `public class Main` (main reads stdin, instantiates Solution, calls method, prints).
- **C++**: One file with `class Solution` and `int main()`.

## Adding a problem

1. Add metadata (and optional input_spec) in `problem_metadata_registry._reg(...)`.
2. Re-run seed so the problem gets generated starter/driver for all languages.
3. If the problem is not in the registry, it uses STARTERS or the default (Python/JS only; function name from title).

## Admin create problem

- Optional: require `function_metadata` when creating a problem and **generate** starter/driver from it (no manual starter/driver paste). Validation can require either `function_metadata` or existing starter_code_* for at least one language.
