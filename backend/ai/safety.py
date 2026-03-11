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
    if not user_message or not isinstance(user_message, str):
        return True
    msg = user_message.strip()
    if not msg:
        return True
    # Allow long legitimate coaching questions. Very large payloads are still treated as abuse.
    if len(msg) > MAX_USER_MESSAGE_LEN * 3:
        return True
    return bool(INJECTION_RE.search(msg))


# Pattern: start of a line that looks like a function/class definition (common in leaked solution code)
_CODE_START_RE = re.compile(
    r"\n\s*(def\s+\w+\s*\(|class\s+\w+|function\s+\w+\s*\(|public\s+\w+.*\s+\w+\s*\(|int\s+\w+\s*\()",
    re.IGNORECASE,
)


def strip_code_blocks_from_hint(response: str) -> str:
    """Remove all markdown code blocks and raw solution code from a hint."""
    if not response or not isinstance(response, str):
        return response
    # Remove ```...``` blocks (with optional language tag)
    out = re.sub(r"```[\w]*\s*\n.*?```", "", response, flags=re.DOTALL)
    # If there is raw code (e.g. "def threeSum(nums):" without backticks), truncate before it
    match = _CODE_START_RE.search(out)
    if match:
        out = out[: match.start()].strip()
    out = re.sub(r"\n{3,}", "\n\n", out.strip())
    if len(out) < 20:
        return "Consider the technique suggested above and try implementing it yourself."
    return out


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
