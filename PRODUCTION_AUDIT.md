# Production Readiness Audit – ifelse Platform

## Bugs Found and Fixes Applied

### 1. Backend – Execution & API

| Issue | Root cause | Fix |
|-------|------------|-----|
| Run/Submit could return 500 on executor exception | `code_executor.execute_code()` exceptions (e.g. Java not installed, runtime error) were not caught | Wrapped `execute_code` in try/except in `/run` and `/submissions`; return structured `COMPILE_ERROR`/`RUNTIME_ERROR` with message; on submit, still create a submission record with failed status |
| No code length limit | Large payloads could cause DoS | Enforced `MAX_CODE_LENGTH` (100k chars) on `/run` and `/submissions`; return 400 if exceeded |
| No rate limiting on execution | Users could spam run/submit | In-memory rate limit: 60 requests per 60s per user on `/run` and `/submissions`; return 429 when exceeded |
| N+1 in user progress | For each solved problem, a separate `find_one` was used | Replaced with single `find({"id": {"$in": solved_problems}})` and iterate cursor for difficulty counts |
| Missing global exception handling | Unhandled exceptions (e.g. DB errors) resulted in non-JSON 500 | Added `@app.exception_handler(RequestValidationError)` → 422 JSON and `@app.exception_handler(Exception)` → 500 JSON with logging |
| Playground route used global `db` | Inconsistent dependency injection | Added `database=Depends(get_db)` and pass `database` to `get_current_user` |

### 2. Backend – Code Executor

| Issue | Root cause | Fix |
|-------|------------|-----|
| JavaScript double-wrapping | Driver code already uses readline/stdin; executor wrapped again | In `_run_javascript`, only wrap when code does not contain `readline` or `process.stdin`; otherwise run as-is with stdin |
| Temp file cleanup on error | `os.unlink` in finally could be skipped | Wrapped unlink in try/except for JS runner |

### 3. Backend – Config & DB

| Issue | Root cause | Fix |
|-------|------------|-----|
| Env not validated at startup | Missing `MONGO_URL`/`DB_NAME` caused failures later | `_get_required_env("MONGO_URL")` and `DB_NAME` at module load; fail fast with clear error |
| No DB indexes | Slow problem/submission queries | Startup event: create indexes on `problems.id` (unique), `difficulty`, `tags`; `submissions`: (user_id, problem_id), `created_at` |
| Problem model `created_by` required | Old documents might lack field | `created_by: str = ""` in `Problem` model for backward compatibility |

### 4. Frontend

| Issue | Root cause | Fix |
|-------|------------|-----|
| `DIFFICULTY_BG` / `DIFFICULTY_COLORS` undefined or missing key | Some problems have no difficulty or constants not loaded | Used `DIFFICULTY_BG?.[problem.difficulty] ?? 'bg-muted border-border'` and same for colors; `(problem.difficulty ?? 'N/A')` for display |
| handleShuffle reassigning const | `list = list.filter(...)` on const | Changed to `let list = ...` |
| No 429 handling for run/submit | Rate limit response not user-friendly | In handleRun/handleSubmit catch: if status === 429 show rate limit message; else show detail or generic message |
| Unhandled promise rejections | API errors could be silent | Added `window.addEventListener('unhandledrejection', ...)` in index.js; skip 401 from `/auth/me` |

### 5. Production Readiness

| Item | Status |
|------|--------|
| Environment config | `.env` required; `MONGO_URL`, `DB_NAME` validated at startup |
| Logging | `logging.basicConfig` + module logger; exception handler logs tracebacks |
| Global exception filter | 422 for validation, 500 for unhandled with JSON body |
| Graceful shutdown | `@app.on_event("shutdown")` closes MongoDB client |
| Docker | `backend/Dockerfile` and root `docker-compose.yml` (MongoDB + backend) |
| Seed script | `python seed_db.py` documented; works with `MONGO_URL`/`DB_NAME` |
| README | Updated with Option A (Docker Compose + local backend/frontend), Option B (full compose), Option C (local); env and run instructions |

---

## Security Hardening

- **Execution**: Subprocess with 5s timeout; no network or filesystem isolation beyond process. For production, consider Docker-based sandbox per run.
- **Rate limiting**: 60 run + submit requests per 60s per user (in-memory).
- **Input**: Code length capped at 100k characters; request body validated via Pydantic.
- **Auth**: JWT + bcrypt; protected routes use `get_current_user`; admin routes use `get_current_admin_user`.

---

## Performance

- **DB**: Indexes on `problems.id`, `difficulty`, `tags`; `submissions` on `(user_id, problem_id)` and `created_at`.
- **User progress**: Single batch query for solved problems’ difficulties instead of N+1.

---

## Validation Proof

- Server module loads with `MONGO_URL` and `DB_NAME` from `.env`.
- TestClient: `POST /api/auth/register` with invalid body → 422; `GET /api/health` → 200.
- With MongoDB down, `GET /api/problems/{id}` is caught by global handler and returns 500 JSON (expected when DB unreachable).
- Frontend: Defensive constants and 429 handling in place; no const reassignment in shuffle.

---

## Final Stability Checklist

- [x] APIs return correct status codes (422 for validation, 404 for not found, 429 for rate limit, 500 with JSON for errors).
- [x] DTO validation via Pydantic; global exception handlers for consistent error responses.
- [x] No N+1 in user progress; DB indexes on startup.
- [x] Execution: compile/runtime errors return structured result; rate limit and code length enforced.
- [x] Frontend: defensive difficulty styling; 429 and error toasts; unhandled rejection logged.
- [x] Env validation, logging, graceful shutdown, Docker and README documented.

Run full user flow (register → login → open problem → run → submit → submissions → leaderboard → hints) with backend and MongoDB running and frontend pointing at the backend to validate end-to-end.
