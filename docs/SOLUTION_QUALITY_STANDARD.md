# Solution Quality Standard (NeetCode / Premium Level)

Every problem solution on IfElse must meet this standard. Use it as the single source of truth for content creation and audits.

---

## 1. Pattern Recognition (MANDATORY)

- **What category is this?** (e.g. Two Pointers, Sliding Window, Hash Map, DP, Backtracking)
- **Why?** Brief justification from the problem statement and constraints.
- **What signals indicate this pattern?** (e.g. "subarray sum" → prefix sum; "find pair" → hash map or two pointers)

---

## 2. Brute Force (MANDATORY)

- **Intuition**: Clear 2–4 sentence explanation of why checking all possibilities works.
- **Why it works**: Logical correctness in plain language.
- **Step-by-step logic**: Numbered steps the reader can follow.
- **Clean code**: All required languages (see Code Requirements below).
- **Complexity**: Time and space in Big-O with one-line justification.

---

## 3. Better Approach (if exists)

- **Why brute force is inefficient**: What makes it slow or heavy (e.g. repeated work, unnecessary space).
- **Key insight**: The one idea that improves the solution.
- **Explanation**: How the insight leads to the better algorithm.
- **Code**: All required languages.
- **Complexity**: Time and space.

---

## 4. Optimal Approach (MANDATORY)

- **Core insight**: The main idea (e.g. "we only need to remember the last minimum").
- **Data structure reasoning**: Why this DS and not another.
- **Why it works**: Short correctness argument or proof idea.
- **Code**: Clean, minimal, interview-ready in all languages.
- **Complexity**: Time and space with brief justification.

---

## 5. Dry Run (MANDATORY)

- Use **one sample input** from the problem (e.g. from examples).
- **Line-by-line** (or step-by-step) walkthrough of how the optimal algorithm runs.
- Show variable values at key steps so a beginner can follow.

---

## 6. Edge Cases (MANDATORY)

Cover at least:

- Empty input
- Single element
- Duplicates (if relevant)
- Large input / constraints
- Negative values (if relevant)
- Overflow risks (if relevant)

List each with how the solution handles it (or why it’s safe).

---

## 7. Common Pitfalls (MANDATORY — at least 3)

For each pitfall:

- **Title**: Short name (e.g. "Off-by-one in loop bound").
- **What goes wrong**: Typical interview mistake.
- **Wrong code snippet** (optional but recommended): 2–4 lines showing the bug.
- **Correct code snippet** (optional but recommended): Same lines fixed.
- **Warning**: One sentence on how to avoid it.

---

## 8. Interview Tips (MANDATORY)

- **How to explain to the interviewer**: What to say first (pattern, then approach, then complexity).
- **Likely follow-up questions**: e.g. "What if array is streamed?", "How to do it in O(1) space?"
- **How to optimize further**: One or two next steps (e.g. different DS, different invariant).

---

## Code Requirements

For **every** approach (Brute, Better, Optimal), provide implementations in:

| Language   | Required | Notes                          |
|-----------|----------|---------------------------------|
| Java      | Yes      | Match problem signature         |
| Python    | Yes      | Match problem signature         |
| C++       | Yes      | Match problem signature         |
| JavaScript| Yes      | Match problem signature         |
| Go        | Yes      | Match problem signature         |
| C#        | Yes      | Match problem signature         |

- Code must **compile** and pass the problem’s test contract.
- **No unnecessary comments**; variable names should be self-explanatory.
- **Interview-ready formatting**: consistent indentation, clear structure.

---

## Content Quality Rules

### DO NOT

- Use vague or generic AI-style explanations.
- Skip reasoning steps (e.g. "obviously we use a hash map" without why).
- Show only the optimal solution; always include Brute → Better (if any) → Optimal.
- Use copy-paste or repeated phrasing across problems.
- Leave approaches with only "content" and no separate intuition/algorithm.

### DO

- Teach like NeetCode: explain **why**, not just what.
- Explain the **mental model** and how to recognize the pattern.
- Explain **trade-offs** (time vs space, simplicity vs optimality).
- Use consistent structure across all problems so learners know where to find what.

---

## Quality Benchmark (Before Marking Complete)

For a random sample of 10 problems, ask:

1. Would this **genuinely help a beginner** understand from scratch?
2. Is it **good enough to replace** watching a NeetCode (or similar) video for this problem?
3. Is the **reasoning deep** (insight + correctness + complexity)?
4. Is the **code clean** and the same in all languages in spirit?
5. Are **edge cases and pitfalls** clearly covered?

If the answer to any is **no**, rewrite or extend the solution until it passes.

---

## Upgrade Process

1. **Scan** all problems (run `audit_solution_quality.py`).
2. **Detect** low-quality solutions: too short, single approach, no intuition, no dry run, missing languages, no edge cases, fewer than 3 pitfalls.
3. **Rewrite** them to this standard (pattern → brute → better → optimal → dry run → edge cases → pitfalls → interview tips; all languages).
4. **Validate** code compiles and matches signature in all languages (use existing validation scripts).
5. **Keep** formatting and structure consistent across the platform.

---

## Schema / Data Shape

- **Problem-level** (one per problem): `pattern_recognition`, `dry_run`, `edge_cases`, `interview_tips`, `common_pitfalls` (string), `pitfalls` (array of `{ title, wrong_example?, correct_example?, warning }`).
- **Per-approach**: `title`, `intuition`, `algorithm`, `code_java`, `code_python`, `code_cpp`, `code_javascript`, `code_go`, `code_csharp`, `complexity` (or `complexity_time` / `complexity_space`).

Solution tab order: Prerequisites → Video → Pattern Recognition → Brute Force → Better → Optimal → Dry Run → Edge Cases → Common Pitfalls (and structured pitfalls) → Interview Tips.
