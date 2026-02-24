# AI Coach Module

DSA mentor for the ifelse coding platform. Guides users step-by-step without leaking full solutions unless explicitly requested.

## Capabilities

1. **Smart hints** – Progressive levels 1–4: concept → approach → pseudocode → edge cases. No full code in hints.
2. **Code review** – After submit: what’s good, what to improve, better approach (no full solution code).
3. **Debug help** – When submission fails: what went wrong, where to look, how to fix (no full solution).
4. **Concept explanation** – Core concept, example, intuition, common mistakes. No solution code.
5. **Recommendations** – Next problems, revision topics, study plan (from `/coach/recommendations`).
6. **Chat** – Interview-style Q&A; sanitized for prompt injection.
7. **Full solution** – Only when user explicitly asks; still post-processed to avoid accidental leak.

## Safety

- **Sanitization**: User message and code length capped; injection patterns rejected.
- **No solution leak**: Prompts instruct the model not to output full solution; response post-check truncates long code blocks.
- **Rate limit**: 20 coach requests per 60s per user.

## API

- `POST /api/coach/hint` – body: `problem_id`, `code`, `hint_level` (1–4).
- `POST /api/coach/code-review` – body: `problem_id`, `code`, `language`, `status`.
- `POST /api/coach/debug` – body: `problem_id`, `code`, `status`, optional `failing_test_info`.
- `POST /api/coach/explain-concept` – body: `problem_id`.
- `GET /api/coach/recommendations` – returns `next_problems`, `revision_topics`, `study_plan`.
- `POST /api/coach/chat` – body: `problem_id`, `message`.
- `POST /api/coach/full-solution` – body: `problem_id`, `request_text`.

All require `Authorization: Bearer <token>`.

## Config

Set `OPENAI_API_KEY` or `AI_COACH_API_KEY` and optionally `AI_COACH_MODEL` (default `gpt-4o-mini`). If unset, endpoints return a fallback message.

## Database

- `ai_feedback_history` – one doc per coach request (user_id, problem_id, kind, hint_level, response_preview, created_at).
- `user_weakness_metrics` – optional; used by recommendations (weak_topics, accuracy_by_topic, etc.).

Indexes are created at startup.
