"""
Safety controls for AI Coach: sanitization, prompt injection mitigation, solution leak prevention.
"""
import re
import logging

logger = logging.getLogger(__name__)

# Patterns that may indicate prompt injection or solution extraction attempts
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|above|prior)\s+instructions",
    r"disregard\s+(your\s+)?(instructions|rules)",
    r"you\s+are\s+now\s+",
    r"output\s+(the\s+)?(full\s+)?solution",
    r"give\s+me\s+the\s+complete\s+code",
    r"paste\s+(the\s+)?(entire\s+)?solution",
    r"show\s+me\s+the\s+answer\s+key",
    r"\[INST\]|\[/INST\]",
    r"<\|.*\|>",
]
INJECTION_RE = re.compile("|".join(INJECTION_PATTERNS), re.IGNORECASE)

# Max lengths to prevent abuse
MAX_USER_MESSAGE_LEN = 4000
MAX_CODE_LEN_FOR_AI = 8000


def sanitize_for_llm(text: str, max_len: int = MAX_USER_MESSAGE_LEN) -> str:
    """Sanitize user input before sending to LLM: truncate and strip."""
    if not text or not isinstance(text, str):
        return ""
    s = text.strip()
    if len(s) > max_len:
        s = s[:max_len] + "\n[... truncated]"
    return s


def sanitize_code_for_llm(code: str) -> str:
    """Sanitize code snippet for context in prompts."""
    return sanitize_for_llm(code, max_len=MAX_CODE_LEN_FOR_AI)


def looks_like_injection(user_message: str) -> bool:
    """Heuristic: does the user message look like prompt injection or solution extraction?"""
    if not user_message or len(user_message) > 2000:
        return True
    return bool(INJECTION_RE.search(user_message))


def ensure_no_solution_leak(response: str, problem_title: str) -> str:
    """Post-process: if response contains long code blocks that look like full solution, truncate or warn."""
    # Allow code snippets up to ~30 lines; beyond that might be full solution
    lines = response.split("\n")
    in_fence = False
    fence_line_count = 0
    for line in lines:
        if line.strip().startswith("```"):
            in_fence = not in_fence
            if in_fence:
                fence_line_count = 0
            continue
        if in_fence:
            fence_line_count += 1
            if fence_line_count > 35:
                # Truncate long code block and add note
                return response[: response.find("```") + 3] + "\n[... solution code truncated for learning. Try implementing it yourself from the explanation above. ]\n```"
    return response
