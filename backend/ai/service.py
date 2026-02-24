"""
AI Coach service: LLM calls with retry, timeout, fallback, and optional cache.
"""
import os
import logging
import hashlib
import json
from typing import Optional, Dict, Any
from collections import OrderedDict

from ai.prompts import PROMPTS
from ai.safety import sanitize_for_llm, sanitize_code_for_llm, looks_like_injection, ensure_no_solution_leak

logger = logging.getLogger(__name__)

# In-memory cache for frequent responses (e.g. same hint level + problem). Max 200 entries.
CACHE_MAX_SIZE = 200
_llm_cache: OrderedDict[str, str] = OrderedDict()
AI_RESPONSE_TIMEOUT = 12  # seconds
AI_MAX_RETRIES = 2


def _get_llm_client():
    """Return OpenAI client if key is set; else None (use fallback)."""
    api_key = os.environ.get("OPENAI_API_KEY") or os.environ.get("AI_COACH_API_KEY")
    if not api_key or not api_key.strip():
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key.strip())
    except Exception as e:
        logger.warning("OpenAI client init failed: %s", e)
        return None


def _cache_key(prompt_name: str, **kwargs) -> str:
    key = prompt_name + "|" + "|".join(f"{k}={str(v)[:200]}" for k, v in sorted(kwargs.items()))
    return hashlib.sha256(key.encode()).hexdigest()


def _get_cached(key: str) -> Optional[str]:
    if key in _llm_cache:
        _llm_cache.move_to_end(key)
        return _llm_cache[key]
    return None


def _set_cached(key: str, value: str) -> None:
    if key in _llm_cache:
        _llm_cache.move_to_end(key)
    else:
        while len(_llm_cache) >= CACHE_MAX_SIZE:
            _llm_cache.popitem(last=False)
    _llm_cache[key] = value


def _call_llm(system: str, user_message: str, timeout: int = AI_RESPONSE_TIMEOUT) -> str:
    """Call LLM with retries. Returns response text or raises."""
    client = _get_llm_client()
    if not client:
        return _fallback_response(user_message)
    for attempt in range(AI_MAX_RETRIES + 1):
        try:
            response = client.chat.completions.create(
                model=os.environ.get("AI_COACH_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user", "content": user_message[:16000]},
                ],
                max_tokens=1024,
                temperature=0.4,
                timeout=timeout,
            )
            text = (response.choices[0].message.content or "").strip()
            if text:
                return text
        except Exception as e:
            logger.warning("LLM call attempt %s failed: %s", attempt + 1, e)
            if attempt == AI_MAX_RETRIES:
                return _fallback_response(user_message, error=str(e))
    return _fallback_response(user_message)


def _fallback_response(user_message: str, error: Optional[str] = None) -> str:
    """When AI is unavailable or fails."""
    if error:
        return "The AI coach is temporarily unavailable. Please try again in a moment, or use the built-in hints and solution tab for guidance."
    return (
        "AI Coach is not configured (set OPENAI_API_KEY or AI_COACH_API_KEY) or the service is busy. "
        "Use the problem's built-in hints and the Solution tab for step-by-step guidance."
    )


class AICoachService:
    """Production-ready AI Coach: hints, code review, debug, concept, recommendations."""

    def __init__(self, use_cache: bool = True):
        self.use_cache = use_cache

    def get_progressive_hint(
        self,
        problem_title: str,
        difficulty: str,
        tags: list,
        code: str,
        hint_level: int,
    ) -> str:
        """Return hint at level 1–4. Does not leak full solution."""
        code_safe = sanitize_code_for_llm(code or "")
        tags_str = ", ".join(tags[:5]) if tags else "N/A"
        if hint_level == 1:
            user_msg = PROMPTS["hint_level_1"].format(
                title=problem_title, difficulty=difficulty, tags=tags_str, code=code_safe
            )
        elif hint_level == 2:
            user_msg = PROMPTS["hint_level_2"].format(title=problem_title, tags=tags_str)
        elif hint_level == 3:
            user_msg = PROMPTS["hint_level_3"].format(title=problem_title)
        else:
            user_msg = PROMPTS["hint_level_4"].format(title=problem_title)
        key = _cache_key("hint", title=problem_title, level=hint_level, code_hash=hashlib.sha256(code_safe.encode()).hexdigest()[:16])
        if self.use_cache:
            cached = _get_cached(key)
            if cached:
                return cached
        response = _call_llm(PROMPTS["system_coach"], user_msg)
        response = ensure_no_solution_leak(response, problem_title)
        if self.use_cache:
            _set_cached(key, response)
        return response

    def code_review(
        self,
        problem_title: str,
        difficulty: str,
        tags: list,
        code: str,
        status: str,
        language: str,
    ) -> str:
        """Structured feedback: what's good, what to improve, better approach (no full code)."""
        code_safe = sanitize_code_for_llm(code or "")
        user_msg = PROMPTS["code_review"].format(
            title=problem_title,
            difficulty=difficulty,
            tags=", ".join(tags[:5]) if tags else "N/A",
            code=code_safe,
            status=status,
            language=language,
        )
        return _call_llm(PROMPTS["system_coach"], user_msg)

    def debug_help(
        self,
        problem_title: str,
        code: str,
        status: str,
        failing_test_info: Optional[str] = None,
    ) -> str:
        """Explain error and suggest where to look / how to fix, without full solution."""
        code_safe = sanitize_code_for_llm(code or "")
        failing_safe = sanitize_for_llm(failing_test_info or "No details provided.")
        user_msg = PROMPTS["debug_help"].format(
            title=problem_title,
            code=code_safe,
            status=status,
            failing_test_info=failing_safe,
        )
        return _call_llm(PROMPTS["system_coach"], user_msg)

    def explain_concept(self, problem_title: str, tags: list) -> str:
        """Concept explanation: core idea, example, intuition, common mistakes. No solution code."""
        user_msg = PROMPTS["concept_explain"].format(
            title=problem_title, tags=", ".join(tags[:5]) if tags else "N/A"
        )
        key = _cache_key("concept", title=problem_title)
        if self.use_cache:
            cached = _get_cached(key)
            if cached:
                return cached
        response = _call_llm(PROMPTS["system_coach"], user_msg)
        if self.use_cache:
            _set_cached(key, response)
        return response

    def get_recommendations(
        self,
        solved_titles: list,
        attempted_titles: list,
        weak_topics: list,
        recent_statuses: list,
    ) -> Dict[str, Any]:
        """Next problems, revision topics, study plan. Returns dict."""
        user_msg = PROMPTS["recommend"].format(
            solved_titles=", ".join(solved_titles[:30]) or "None",
            attempted_titles=", ".join(attempted_titles[:20]) or "None",
            weak_topics=", ".join(weak_topics[:15]) or "None",
            recent_statuses=", ".join(str(s) for s in recent_statuses[:20]) or "None",
        )
        response = _call_llm(PROMPTS["system_coach"], user_msg)
        try:
            # Try to parse JSON from response (model might wrap in markdown)
            text = response.strip()
            if "```" in text:
                start = text.find("```") + 3
                if "json" in text[:start].lower():
                    start = text.find("\n", start) + 1 if text.find("\n", start) != -1 else start
                end = text.find("```", start)
                text = text[start:end] if end != -1 else text[start:]
            return json.loads(text)
        except json.JSONDecodeError:
            return {
                "next_problems": [],
                "revision_topics": [],
                "study_plan": response[:500],
            }

    def full_solution(self, problem_title: str, user_request: str) -> str:
        """Only when user explicitly requested full solution. Still apply leak check."""
        if not user_request or "solution" not in user_request.lower() and "code" not in user_request.lower():
            return "To get the full solution, please ask explicitly: 'Give me the full solution' or 'Show me the code'."
        user_msg = PROMPTS["full_solution"].format(title=problem_title)
        response = _call_llm(PROMPTS["full_solution_system"], user_msg)
        return ensure_no_solution_leak(response, problem_title)

    def chat(
        self,
        problem_title: str,
        user_message: str,
        problem_description: Optional[str] = None,
        problem_examples: Optional[str] = None,
        difficulty: str = "medium",
        tags: Optional[list] = None,
    ) -> str:
        """Chat with optional full problem context. When description/examples are provided, AI has full context and won't ask for problem statement."""
        if looks_like_injection(user_message):
            return "I'm here to guide you. Try describing where you're stuck or what approach you're considering."
        safe_msg = sanitize_for_llm(user_message)
        tags_list = tags or []
        tags_str = ", ".join(tags_list[:10]) if tags_list else "N/A"
        if problem_description is not None and problem_examples is not None:
            system = PROMPTS["chat_system_with_problem"].format(
                title=problem_title,
                difficulty=difficulty,
                tags=tags_str,
                description=(problem_description or "No description.").strip()[:8000],
                examples=(problem_examples or "No examples.").strip()[:2000],
            )
        else:
            system = PROMPTS["interview_mode"].format(title=problem_title)
        return _call_llm(system, safe_msg)
