# Problem Content Schema (Learning-First)

Every problem on IfElse must follow this **educational structure**. No problem may show only an optimized solution first.

## Global requirement

1. **Prerequisites**
2. **Video Explanation** (YouTube integration)
3. **Brute Force**
4. **Better / Optimal Approach** (e.g. Stack, Two Pointers)
5. *(Optional)* Advanced / DP
6. **Time & Space Complexity**
7. **Common Pitfalls**
8. **Solutions in all supported languages** (Java, Python, C++, JavaScript, Go, C#)

## Master template schema

```json
{
  "prerequisites": ["Monotonic Stack", "Array Traversal", "Dynamic Programming (Basic)"],
  "youtubeVideoUrl": "https://www.youtube.com/watch?v=...",
  "youtube_video_id": "VIDEO_ID",
  "approaches": [
    {
      "title": "Brute Force",
      "intuition": "...",
      "algorithm": "...",
      "code": {
        "java": "...",
        "python": "...",
        "cpp": "...",
        "javascript": "...",
        "go": "...",
        "csharp": "..."
      },
      "complexity": {
        "time": "O(n²)",
        "space": "O(1)"
      }
    },
    {
      "title": "Optimal (Hash Map)",
      "intuition": "...",
      "algorithm": "...",
      "code": { "java": "...", "python": "...", "cpp": "...", "javascript": "...", "go": "...", "csharp": "..." },
      "complexity": { "time": "O(n)", "space": "O(n)" }
    }
  ],
  "pitfalls": [
    { "title": "...", "wrong_example": "...", "correct_example": "...", "warning": "..." }
  ],
  "common_pitfalls": "Full markdown or plain text with at least 3 common mistakes."
}
```

## Backend models

- **ProblemBase**: `prerequisites`, `youtube_video_id`, `solutions` (list of approaches), `common_pitfalls`, `pitfalls` (optional structured), plus premium: `pattern_recognition`, `dry_run`, `edge_cases`, `interview_tips` (see **docs/SOLUTION_QUALITY_STANDARD.md**).
- **SolutionApproach**: `title`, `intuition`, `algorithm`, `code_python`, `code_java`, `code_cpp`, `code_javascript`, `code_go`, `code_csharp`, `code_c`, `complexity` (string), optional `complexity_time` / `complexity_space`.

## Solution order

Approaches must always be in **learning order**:

1. Brute Force  
2. Better approach (if any)  
3. Optimal approach  

Never attach a single “Solution” block that is only the optimal approach.

## UI behavior

- **Solution tab**: Prerequisites (clickable tags) → Video Explanation (embed + “View on YouTube”) → each approach with **progressive reveal** (“Reveal Brute Force”, “Reveal Optimal”).
- Solutions are hidden by default; the user reveals each approach step by step.
- Code is shown in all available languages (Java, Python, C++, JavaScript, Go, C#, C) per approach.
- No pink in the UI (theme uses primary blue, accent teal, neutral slate).

## Validation (before production)

- No problem directly shows the optimized solution as the only or first content.
- Every problem with solutions has: Prerequisites (or empty list), optional YouTube link, at least 2 approaches (Brute Force + Optimal/Better), and code in as many supported languages as possible.
- Run `python backend/scripts/validate_problem_content.py` to report missing fields or wrong order.
