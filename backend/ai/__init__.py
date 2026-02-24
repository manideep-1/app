"""
AI Coach module for ifelse.
- Smart hints (progressive, no full solution leak)
- Code review, debug help, concept explanation
- Personalized recommendations
"""
from ai.prompts import PROMPTS
from ai.service import AICoachService
from ai.safety import sanitize_for_llm, ensure_no_solution_leak

__all__ = ["PROMPTS", "AICoachService", "sanitize_for_llm", "ensure_no_solution_leak"]
