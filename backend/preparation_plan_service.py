"""
Preparation plan engine:
- Generates structured day-wise plans
- Maps each day to real problems from DB
- Stores and reads user plan state
"""
from __future__ import annotations

import logging
import re
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional, Tuple


logger = logging.getLogger(__name__)


class ActivePlanExistsError(Exception):
    def __init__(self, existing_plan: Dict[str, Any]):
        super().__init__("Active preparation plan already exists.")
        self.existing_plan = existing_plan


class PlanGenerationError(Exception):
    pass


DEFAULT_DURATION_DAYS = 14
DEFAULT_DAILY_HOURS = 3.0
MAX_DURATION_DAYS = 90
MIN_DURATION_DAYS = 1
MIN_DAILY_HOURS = 0.5
MAX_DAILY_HOURS = 12.0

PLAN_STATUS_NOT_STARTED = "not_started"
PLAN_STATUS_IN_PROGRESS = "in_progress"
PLAN_STATUS_COMPLETED = "completed"
VALID_PLAN_STATUSES = {PLAN_STATUS_NOT_STARTED, PLAN_STATUS_IN_PROGRESS, PLAN_STATUS_COMPLETED}

KNOWN_COMPANIES = [
    "Amazon",
    "Google",
    "Microsoft",
    "Meta",
    "Apple",
    "Netflix",
    "Adobe",
    "Bloomberg",
    "LinkedIn",
    "Uber",
    "Airbnb",
    "Oracle",
    "Salesforce",
    "Twitter",
]

TOPIC_BLUEPRINTS: List[Dict[str, Any]] = [
    {"focus": "Arrays & Strings", "tags": {"array", "string"}},
    {"focus": "Hashing", "tags": {"hash table"}},
    {"focus": "Two Pointers", "tags": {"two pointers"}},
    {"focus": "Sliding Window", "tags": {"sliding window"}},
    {"focus": "Stack & Queue", "tags": {"stack", "queue", "deque"}},
    {"focus": "Binary Search", "tags": {"binary search"}},
    {"focus": "Linked List", "tags": {"linked list"}},
    {"focus": "Trees", "tags": {"tree", "binary tree", "bst"}},
    {"focus": "Graphs", "tags": {"graph", "bfs", "dfs", "topological sort"}},
    {"focus": "Dynamic Programming", "tags": {"dynamic programming"}},
    {"focus": "Greedy", "tags": {"greedy"}},
    {"focus": "Heap & Priority Queue", "tags": {"heap"}},
    {"focus": "Intervals", "tags": {"intervals"}},
    {"focus": "Backtracking", "tags": {"backtracking"}},
    {"focus": "Trie", "tags": {"trie"}},
]

TOPIC_FOCUS_BY_KEYWORD = {
    "array": "Arrays & Strings",
    "string": "Arrays & Strings",
    "hash": "Hashing",
    "two pointer": "Two Pointers",
    "sliding window": "Sliding Window",
    "stack": "Stack & Queue",
    "queue": "Stack & Queue",
    "binary search": "Binary Search",
    "linked list": "Linked List",
    "tree": "Trees",
    "graph": "Graphs",
    "dynamic programming": "Dynamic Programming",
    "dp": "Dynamic Programming",
    "greedy": "Greedy",
    "heap": "Heap & Priority Queue",
    "interval": "Intervals",
    "backtracking": "Backtracking",
    "trie": "Trie",
}

DIFFICULTY_RATIO_MAP = {
    "balanced": {"easy": 0.25, "medium": 0.55, "hard": 0.20},
    "medium-heavy": {"easy": 0.10, "medium": 0.65, "hard": 0.25},
    "easy-medium": {"easy": 0.40, "medium": 0.50, "hard": 0.10},
    "hard-heavy": {"easy": 0.05, "medium": 0.45, "hard": 0.50},
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _norm(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip().lower())


def _difficulty_value(raw: Any) -> str:
    value = _norm(raw)
    if "." in value:
        value = value.split(".")[-1]
    if value not in {"easy", "medium", "hard"}:
        return "medium"
    return value


def _parse_iso_date(raw: Any) -> datetime:
    if isinstance(raw, datetime):
        return raw if raw.tzinfo else raw.replace(tzinfo=timezone.utc)
    text = str(raw or "").strip()
    if not text:
        return datetime.now(timezone.utc)
    try:
        return datetime.fromisoformat(text.replace("Z", "+00:00"))
    except Exception:
        return datetime.now(timezone.utc)


def _coerce_duration_days(value: Any) -> int:
    try:
        days = int(float(value))
    except Exception:
        days = DEFAULT_DURATION_DAYS
    return max(MIN_DURATION_DAYS, min(MAX_DURATION_DAYS, days))


def _coerce_daily_hours(value: Any) -> float:
    try:
        hours = float(value)
    except Exception:
        hours = DEFAULT_DAILY_HOURS
    return max(MIN_DAILY_HOURS, min(MAX_DAILY_HOURS, hours))


def _problems_per_day_for_hours(daily_hours: float) -> int:
    if daily_hours <= 2.0:
        return 4
    if daily_hours <= 3.5:
        return 5
    return 6


def _normalize_difficulty_preference(raw: Optional[str]) -> str:
    value = _norm(raw)
    if not value:
        return "balanced"
    if value in DIFFICULTY_RATIO_MAP:
        return value
    if "medium" in value and ("hard" in value or "heavy" in value):
        return "medium-heavy"
    if "easy" in value and "medium" in value:
        return "easy-medium"
    if "hard" in value:
        return "hard-heavy"
    return "balanced"


def _extract_duration_days_from_text(text: str) -> Optional[int]:
    lower = _norm(text)
    m = re.search(r"\b(\d{1,3})\s*(day|days|d)\b", lower)
    if m:
        return _coerce_duration_days(int(m.group(1)))
    m = re.search(r"\b(\d{1,2})\s*(week|weeks|w)\b", lower)
    if m:
        return _coerce_duration_days(int(m.group(1)) * 7)
    m = re.search(r"\b(\d{1,2})\s*(month|months)\b", lower)
    if m:
        return _coerce_duration_days(int(m.group(1)) * 30)
    return None


def _extract_daily_hours_from_text(text: str) -> Optional[float]:
    lower = _norm(text)
    m = re.search(r"\b(\d{1,2}(?:\.\d+)?)\s*(hours?|hrs?|h)\s*(?:per\s*day|/day|daily)?\b", lower)
    if m:
        return _coerce_daily_hours(float(m.group(1)))
    m = re.search(r"\b(\d{1,2}(?:\.\d+)?)\s*(?:per\s*day|daily)\b", lower)
    if m:
        return _coerce_daily_hours(float(m.group(1)))
    return None


def _extract_company_from_text(text: str) -> str:
    lower = _norm(text)
    for company in KNOWN_COMPANIES:
        if re.search(rf"\b{re.escape(company.lower())}\b", lower):
            return company
    # Generic fallback if no known company detected
    return "Generic"


def _extract_weak_topics_from_text(text: str) -> List[str]:
    lower = _norm(text)
    out: List[str] = []
    m = re.search(r"\bweak(?:\s+topics?)?\s*(?:are|in|:)?\s*([a-z0-9,\-/&\s]{4,120})", lower)
    if m:
        tail = m.group(1)
        for token in re.split(r",| and |/|&", tail):
            t = token.strip()
            if len(t) >= 2:
                out.append(t)
    return out[:6]


def _extract_difficulty_preference_from_text(text: str) -> str:
    lower = _norm(text)
    if "medium-heavy" in lower or ("medium" in lower and ("hard" in lower or "heavy" in lower)):
        return "medium-heavy"
    if "easy-medium" in lower or ("easy" in lower and "medium" in lower):
        return "easy-medium"
    if "hard-heavy" in lower or "hard" in lower:
        return "hard-heavy"
    if "balanced" in lower:
        return "balanced"
    return "balanced"


def should_generate_plan_from_message(message: str) -> bool:
    lower = _norm(message)
    has_plan_keyword = bool(
        re.search(
            r"\b(plan|roadmap|preparation|prep schedule|study plan|interview plan|day[- ]by[- ]day|schedule)\b",
            lower,
        )
    )
    has_duration = _extract_duration_days_from_text(lower) is not None
    has_hours = _extract_daily_hours_from_text(lower) is not None
    company = _extract_company_from_text(lower)
    if has_plan_keyword:
        return True
    return has_duration and has_hours and company != "Generic"


def parse_plan_request_from_message(message: str) -> Optional[Dict[str, Any]]:
    if not should_generate_plan_from_message(message):
        return None
    lower = _norm(message)
    duration_days = _extract_duration_days_from_text(lower) or DEFAULT_DURATION_DAYS
    daily_hours = _extract_daily_hours_from_text(lower) or DEFAULT_DAILY_HOURS
    target_company = _extract_company_from_text(lower)
    difficulty_preference = _extract_difficulty_preference_from_text(lower)
    weak_topics = _extract_weak_topics_from_text(lower)
    replace_existing = bool(re.search(r"\b(replace|overwrite|regenerate|new plan|reset plan)\b", lower))
    return {
        "duration_days": duration_days,
        "daily_hours": daily_hours,
        "target_company": target_company,
        "difficulty_preference": difficulty_preference,
        "user_weak_topics": weak_topics,
        "replace_existing": replace_existing,
    }


def _difficulty_counts(total: int, ratios: Dict[str, float]) -> Dict[str, int]:
    keys = ["easy", "medium", "hard"]
    raw = {k: max(0.0, float(ratios.get(k, 0.0))) for k in keys}
    s = sum(raw.values())
    if s <= 0:
        raw = DIFFICULTY_RATIO_MAP["balanced"].copy()
        s = 1.0
    normalized = {k: raw[k] / s for k in keys}
    base = {k: int(normalized[k] * total) for k in keys}
    assigned = sum(base.values())
    remainder = total - assigned
    fractional = sorted(
        keys,
        key=lambda k: (normalized[k] * total - base[k]),
        reverse=True,
    )
    i = 0
    while remainder > 0:
        base[fractional[i % len(fractional)]] += 1
        remainder -= 1
        i += 1
    return base


def _topic_tag_set_from_focus(focus_topic: str, weak_topics: List[str]) -> set:
    focus_norm = _norm(focus_topic)
    for bp in TOPIC_BLUEPRINTS:
        if _norm(bp["focus"]) == focus_norm:
            return set(bp["tags"])
    # Revision / weak-topic day
    tags = set()
    weak_norm = [_norm(w) for w in weak_topics]
    for weak in weak_norm:
        for key, focus in TOPIC_FOCUS_BY_KEYWORD.items():
            if key in weak:
                tags |= _topic_tag_set_from_focus(focus, [])
    return tags


def _focus_sequence(duration_days: int, weak_topics: List[str]) -> List[Dict[str, Any]]:
    # Build topic rotation with weak topics pulled forward
    weak_focuses: List[str] = []
    for weak in weak_topics:
        weak_norm = _norm(weak)
        for key, focus in TOPIC_FOCUS_BY_KEYWORD.items():
            if key in weak_norm and focus not in weak_focuses:
                weak_focuses.append(focus)

    base_focuses = [bp["focus"] for bp in TOPIC_BLUEPRINTS]
    merged_focuses = weak_focuses + [f for f in base_focuses if f not in weak_focuses]

    days: List[Dict[str, Any]] = []
    focus_idx = 0
    for day_number in range(1, duration_days + 1):
        is_mock = duration_days >= 7 and day_number == duration_days
        is_revision = duration_days >= 7 and (day_number % 7 == 0) and not is_mock
        if is_mock:
            focus_topic = "Mock Interview Day"
        elif is_revision:
            focus_topic = "Revision + Weak Topics"
        else:
            focus_topic = merged_focuses[focus_idx % len(merged_focuses)]
            focus_idx += 1
        days.append(
            {
                "day": day_number,
                "focus_topic": focus_topic,
                "is_revision_day": is_revision,
                "is_mock_interview_day": is_mock,
            }
        )
    return days


def _rank_problem(
    problem: Dict[str, Any],
    focus_tags: set,
    target_company_norm: str,
    weak_tag_keywords: set,
    solved_ids: set,
) -> float:
    score = 0.0
    tags = problem["tags_norm"]
    companies = problem["companies_norm"]
    if target_company_norm and target_company_norm != "generic":
        if target_company_norm in companies:
            score += 35.0
        elif any(target_company_norm in c or c in target_company_norm for c in companies):
            score += 20.0
    overlap = len(tags.intersection(focus_tags))
    score += overlap * 14.0
    weak_overlap = len(tags.intersection(weak_tag_keywords))
    score += weak_overlap * 7.0
    if problem["id"] in solved_ids:
        score -= 18.0
    if overlap == 0:
        score -= 3.0
    # Slight bias for medium to keep plans practical
    if problem["difficulty"] == "medium":
        score += 1.5
    return score


def _prepare_problem_pool(raw_problems: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    out = []
    for p in raw_problems:
        pid = str(p.get("id") or "").strip()
        title = str(p.get("title") or "").strip()
        if not pid or not title:
            continue
        out.append(
            {
                "id": pid,
                "title": title,
                "difficulty": _difficulty_value(p.get("difficulty")),
                "tags_norm": {_norm(t) for t in (p.get("tags") or []) if _norm(t)},
                "companies_norm": {_norm(c) for c in (p.get("companies") or []) if _norm(c)},
            }
        )
    return out


def _select_problems_for_day(
    problem_pool: List[Dict[str, Any]],
    used_problem_ids: set,
    focus_topic: str,
    target_company: str,
    weak_topics: List[str],
    solved_ids: set,
    difficulty_preference: str,
    day_type: str,
    daily_problem_count: int,
    adaptive_delta: Dict[str, float],
) -> Tuple[List[Dict[str, Any]], bool]:
    target_company_norm = _norm(target_company)
    focus_tags = _topic_tag_set_from_focus(focus_topic, weak_topics)

    weak_tag_keywords = set()
    for wt in weak_topics:
        wt_norm = _norm(wt)
        weak_tag_keywords.add(wt_norm)
        for key, mapped_focus in TOPIC_FOCUS_BY_KEYWORD.items():
            if key in wt_norm:
                weak_tag_keywords |= _topic_tag_set_from_focus(mapped_focus, [])

    ratios = DIFFICULTY_RATIO_MAP.get(difficulty_preference, DIFFICULTY_RATIO_MAP["balanced"]).copy()
    if day_type == "mock":
        ratios = {"easy": 0.0, "medium": 0.45, "hard": 0.55}
    elif day_type == "revision":
        ratios = {"easy": 0.20, "medium": 0.55, "hard": 0.25}

    for key, delta in adaptive_delta.items():
        if key in ratios:
            ratios[key] = max(0.0, ratios[key] + float(delta))

    counts = _difficulty_counts(daily_problem_count, ratios)
    available = [p for p in problem_pool if p["id"] not in used_problem_ids]
    fallback_used = False

    ranked = sorted(
        available,
        key=lambda p: (
            -_rank_problem(p, focus_tags, target_company_norm, weak_tag_keywords, solved_ids),
            p["title"].lower(),
        ),
    )
    selected: List[Dict[str, Any]] = []
    selected_ids = set()

    for diff in ("easy", "medium", "hard"):
        target = counts.get(diff, 0)
        if target <= 0:
            continue
        bucket = [p for p in ranked if p["difficulty"] == diff and p["id"] not in selected_ids]
        for p in bucket[:target]:
            selected.append(p)
            selected_ids.add(p["id"])

    if len(selected) < daily_problem_count:
        for p in ranked:
            if p["id"] in selected_ids:
                continue
            selected.append(p)
            selected_ids.add(p["id"])
            if len(selected) >= daily_problem_count:
                break

    if len(selected) < daily_problem_count:
        # Fallback: not enough unique problems. Reuse from already-used pool (still avoid duplicates within same day).
        fallback_used = True
        recycled = sorted(
            [p for p in problem_pool if p["id"] not in selected_ids],
            key=lambda p: (
                -_rank_problem(p, focus_tags, target_company_norm, weak_tag_keywords, solved_ids),
                p["title"].lower(),
            ),
        )
        for p in recycled:
            selected.append(p)
            selected_ids.add(p["id"])
            if len(selected) >= daily_problem_count:
                break

    for p in selected:
        used_problem_ids.add(p["id"])

    return selected[:daily_problem_count], fallback_used


async def _infer_adaptive_difficulty_delta(database, user_id: str) -> Dict[str, float]:
    """Adjust difficulty mix based on recent acceptance trend."""
    recent = await database.submissions.find(
        {"user_id": user_id},
        {"_id": 0, "status": 1},
    ).sort("created_at", -1).limit(60).to_list(60)
    if not recent:
        return {}

    accepted = sum(1 for r in recent if _norm(r.get("status")) == "accepted")
    ratio = accepted / max(1, len(recent))
    if ratio < 0.35:
        return {"easy": 0.12, "medium": 0.05, "hard": -0.17}
    if ratio > 0.75:
        return {"easy": -0.10, "medium": 0.00, "hard": 0.10}
    return {}


async def _infer_weak_topics(database, user_id: str, provided: Optional[List[str]] = None) -> List[str]:
    topics: List[str] = []
    for t in (provided or []):
        if _norm(t):
            topics.append(str(t).strip())

    metrics = await database.user_weakness_metrics.find_one(
        {"user_id": user_id},
        {"_id": 0, "weak_topics": 1},
    )
    if metrics:
        for t in (metrics.get("weak_topics") or []):
            if _norm(t):
                topics.append(str(t).strip())

    failed = await database.submissions.find(
        {"user_id": user_id, "status": {"$ne": "accepted"}},
        {"_id": 0, "problem_id": 1},
    ).sort("created_at", -1).limit(80).to_list(80)
    failed_problem_ids = [str(x.get("problem_id") or "").strip() for x in failed if x.get("problem_id")]
    if failed_problem_ids:
        counts = Counter(failed_problem_ids)
        docs = await database.problems.find(
            {"id": {"$in": list(counts.keys())}},
            {"_id": 0, "id": 1, "tags": 1},
        ).to_list(300)
        tag_weight = Counter()
        for doc in docs:
            weight = counts.get(str(doc.get("id") or ""), 1)
            for tag in (doc.get("tags") or []):
                if _norm(tag):
                    tag_weight[str(tag).strip()] += weight
        for tag, _ in tag_weight.most_common(4):
            topics.append(tag)

    deduped: List[str] = []
    seen = set()
    for t in topics:
        key = _norm(t)
        if key and key not in seen:
            seen.add(key)
            deduped.append(t)
    return deduped[:6]


async def _delete_plan_cascade(database, user_id: str, plan_id: str) -> bool:
    plan = await database.user_preparation_plans.find_one({"id": plan_id, "user_id": user_id}, {"_id": 0, "id": 1})
    if not plan:
        return False
    days = await database.user_plan_days.find({"plan_id": plan_id}, {"_id": 0, "id": 1}).to_list(500)
    day_ids = [d["id"] for d in days if d.get("id")]
    if day_ids:
        await database.user_plan_problems.delete_many({"plan_day_id": {"$in": day_ids}})
    await database.user_plan_days.delete_many({"plan_id": plan_id})
    await database.user_preparation_plans.delete_one({"id": plan_id, "user_id": user_id})
    return True


async def generate_preparation_plan(
    database,
    user_id: str,
    duration_days: int,
    daily_hours: float,
    target_company: str,
    difficulty_preference: str = "balanced",
    user_weak_topics: Optional[List[str]] = None,
    replace_existing: bool = False,
) -> Dict[str, Any]:
    duration_days = _coerce_duration_days(duration_days)
    daily_hours = _coerce_daily_hours(daily_hours)
    target_company = (str(target_company or "Generic").strip() or "Generic")
    difficulty_preference = _normalize_difficulty_preference(difficulty_preference)

    active = await database.user_preparation_plans.find_one(
        {"user_id": user_id, "is_active": True},
        {"_id": 0},
    )
    if active and not replace_existing:
        raise ActivePlanExistsError(active)
    if active and replace_existing:
        await _delete_plan_cascade(database, user_id, active["id"])

    raw_problems = await database.problems.find(
        {},
        {"_id": 0, "id": 1, "title": 1, "difficulty": 1, "tags": 1, "companies": 1},
    ).to_list(5000)
    problem_pool = _prepare_problem_pool(raw_problems)
    if not problem_pool:
        raise PlanGenerationError("No problems found in database.")

    user_doc = await database.users.find_one({"id": user_id}, {"_id": 0, "solved_problems": 1})
    solved_ids = set(user_doc.get("solved_problems") or []) if user_doc else set()
    weak_topics = await _infer_weak_topics(database, user_id, provided=user_weak_topics)
    adaptive_delta = await _infer_adaptive_difficulty_delta(database, user_id)

    day_templates = _focus_sequence(duration_days, weak_topics)
    used_problem_ids: set = set()
    daily_problem_count = _problems_per_day_for_hours(daily_hours)
    generated_days: List[Dict[str, Any]] = []
    fallback_used_any = False

    for day in day_templates:
        day_type = "normal"
        if day["is_mock_interview_day"]:
            day_type = "mock"
        elif day["is_revision_day"]:
            day_type = "revision"

        count_for_day = daily_problem_count
        if day_type == "mock":
            count_for_day = max(4, min(5, daily_problem_count))

        selected, fallback_used = _select_problems_for_day(
            problem_pool=problem_pool,
            used_problem_ids=used_problem_ids,
            focus_topic=day["focus_topic"],
            target_company=target_company,
            weak_topics=weak_topics,
            solved_ids=solved_ids,
            difficulty_preference=difficulty_preference,
            day_type=day_type,
            daily_problem_count=count_for_day,
            adaptive_delta=adaptive_delta,
        )
        if not selected:
            raise PlanGenerationError("Could not assign problems for one or more plan days.")
        fallback_used_any = fallback_used_any or fallback_used
        generated_days.append(
            {
                "day": day["day"],
                "focus_topic": day["focus_topic"],
                "is_revision_day": day["is_revision_day"],
                "is_mock_interview_day": day["is_mock_interview_day"],
                "problems": selected,
            }
        )

    now = _now_iso()
    plan_id = str(uuid.uuid4())
    plan_doc = {
        "id": plan_id,
        "user_id": user_id,
        "target_company": target_company,
        "duration_days": duration_days,
        "daily_hours": daily_hours,
        "difficulty_preference": difficulty_preference,
        "created_at": now,
        "updated_at": now,
        "is_active": True,
    }
    await database.user_preparation_plans.insert_one(plan_doc)

    day_docs = []
    plan_problem_docs = []
    for day in generated_days:
        day_id = str(uuid.uuid4())
        day_doc = {
            "id": day_id,
            "plan_id": plan_id,
            "day_number": day["day"],
            "focus_topic": day["focus_topic"],
            "is_revision_day": day["is_revision_day"],
            "is_mock_interview_day": day["is_mock_interview_day"],
            "created_at": now,
        }
        day_docs.append(day_doc)

        for idx, problem in enumerate(day["problems"], start=1):
            plan_problem_docs.append(
                {
                    "id": str(uuid.uuid4()),
                    "plan_day_id": day_id,
                    "problem_id": problem["id"],
                    "status": PLAN_STATUS_NOT_STARTED,
                    "assigned_order": idx,
                    "created_at": now,
                    "updated_at": now,
                }
            )

    if day_docs:
        await database.user_plan_days.insert_many(day_docs)
    if plan_problem_docs:
        await database.user_plan_problems.insert_many(plan_problem_docs)

    return {
        "planId": plan_id,
        "durationDays": duration_days,
        "dailyHours": daily_hours,
        "targetCompany": target_company,
        "difficultyPreference": difficulty_preference,
        "fallbackUsed": fallback_used_any,
        "days": [
            {
                "day": d["day"],
                "focusTopic": d["focus_topic"],
                "problems": [
                    {
                        "problemId": p["id"],
                        "title": p["title"],
                        "difficulty": p["difficulty"],
                    }
                    for p in d["problems"]
                ],
            }
            for d in generated_days
        ],
    }


async def _build_plan_payload(database, plan: Dict[str, Any]) -> Dict[str, Any]:
    day_docs = await database.user_plan_days.find(
        {"plan_id": plan["id"]},
        {"_id": 0},
    ).sort("day_number", 1).to_list(500)

    day_ids = [d["id"] for d in day_docs if d.get("id")]
    plan_problem_docs = []
    if day_ids:
        plan_problem_docs = await database.user_plan_problems.find(
            {"plan_day_id": {"$in": day_ids}},
            {"_id": 0},
        ).sort([("plan_day_id", 1), ("assigned_order", 1)]).to_list(5000)

    problem_ids = list({str(pp.get("problem_id")) for pp in plan_problem_docs if pp.get("problem_id")})
    problem_docs = []
    if problem_ids:
        problem_docs = await database.problems.find(
            {"id": {"$in": problem_ids}},
            {"_id": 0, "id": 1, "title": 1, "difficulty": 1},
        ).to_list(5000)
    problem_by_id = {str(p.get("id")): p for p in problem_docs}

    plan_problem_by_day = defaultdict(list)
    for pp in plan_problem_docs:
        plan_problem_by_day[pp["plan_day_id"]].append(pp)

    created_dt = _parse_iso_date(plan.get("created_at"))
    today = datetime.now(timezone.utc).date()
    next_rescheduled_day = max(1, (today - created_dt.date()).days + 1)

    total_count = 0
    completed_count = 0
    days_out = []
    next_day_to_resume = None
    has_rescheduled_days = False

    for day in day_docs:
        day_problem_rows = plan_problem_by_day.get(day["id"], [])
        problems_out = []
        day_completed = 0
        for row in day_problem_rows:
            p = problem_by_id.get(str(row.get("problem_id")))
            if not p:
                continue
            status = str(row.get("status") or PLAN_STATUS_NOT_STARTED)
            if status == PLAN_STATUS_COMPLETED:
                day_completed += 1
            problems_out.append(
                {
                    "planProblemId": row.get("id"),
                    "problemId": p.get("id"),
                    "title": p.get("title"),
                    "difficulty": _difficulty_value(p.get("difficulty")),
                    "status": status,
                }
            )

        day_total = len(problems_out)
        day_completion = int(round((100.0 * day_completed / day_total), 0)) if day_total else 0
        scheduled_date = created_dt.date() + timedelta(days=max(0, int(day.get("day_number", 1)) - 1))
        is_missed = scheduled_date < today and day_completion < 100

        if day_completion >= 100:
            suggested_day = int(day.get("day_number", 1))
        else:
            suggested_day = max(int(day.get("day_number", 1)), next_rescheduled_day)
            next_rescheduled_day = suggested_day + 1
            has_rescheduled_days = has_rescheduled_days or (suggested_day != int(day.get("day_number", 1)))
            if next_day_to_resume is None and problems_out:
                next_day_to_resume = int(day.get("day_number", 1))

        total_count += day_total
        completed_count += day_completed

        days_out.append(
            {
                "planDayId": day.get("id"),
                "day": int(day.get("day_number", 1)),
                "focusTopic": day.get("focus_topic") or "Practice",
                "isRevisionDay": bool(day.get("is_revision_day")),
                "isMockInterviewDay": bool(day.get("is_mock_interview_day")),
                "scheduledDate": scheduled_date.isoformat(),
                "isMissed": is_missed,
                "suggestedDay": suggested_day,
                "completionPercent": day_completion,
                "completedProblems": day_completed,
                "totalProblems": day_total,
                "problems": problems_out,
            }
        )

    overall_completion = int(round((100.0 * completed_count / total_count), 0)) if total_count else 0
    return {
        "planId": plan["id"],
        "targetCompany": plan.get("target_company") or "Generic",
        "durationDays": int(plan.get("duration_days") or 0),
        "dailyHours": float(plan.get("daily_hours") or 0),
        "difficultyPreference": plan.get("difficulty_preference") or "balanced",
        "createdAt": plan.get("created_at"),
        "updatedAt": plan.get("updated_at"),
        "overallCompletionPercent": overall_completion,
        "completedProblems": completed_count,
        "totalProblems": total_count,
        "nextDayToResume": next_day_to_resume,
        "hasRescheduledDays": has_rescheduled_days,
        "days": days_out,
    }


async def get_active_preparation_plan(database, user_id: str) -> Optional[Dict[str, Any]]:
    plan = await database.user_preparation_plans.find_one(
        {"user_id": user_id, "is_active": True},
        {"_id": 0},
        sort=[("updated_at", -1)],
    )
    if not plan:
        return None
    return await _build_plan_payload(database, plan)


async def update_plan_problem_status(
    database,
    user_id: str,
    plan_problem_id: str,
    status: str,
) -> Dict[str, Any]:
    status_norm = _norm(status)
    if status_norm not in VALID_PLAN_STATUSES:
        raise PlanGenerationError("Invalid plan problem status.")

    row = await database.user_plan_problems.find_one({"id": plan_problem_id}, {"_id": 0})
    if not row:
        raise PlanGenerationError("Plan problem not found.")

    day = await database.user_plan_days.find_one({"id": row["plan_day_id"]}, {"_id": 0})
    if not day:
        raise PlanGenerationError("Plan day not found.")

    plan = await database.user_preparation_plans.find_one({"id": day["plan_id"], "user_id": user_id}, {"_id": 0})
    if not plan:
        raise PlanGenerationError("Preparation plan not found.")

    now = _now_iso()
    await database.user_plan_problems.update_one(
        {"id": plan_problem_id},
        {"$set": {"status": status_norm, "updated_at": now}},
    )
    await database.user_preparation_plans.update_one(
        {"id": plan["id"]},
        {"$set": {"updated_at": now}},
    )

    fresh_plan = await database.user_preparation_plans.find_one({"id": plan["id"], "user_id": user_id}, {"_id": 0})
    if not fresh_plan:
        raise PlanGenerationError("Preparation plan not found after update.")
    return await _build_plan_payload(database, fresh_plan)


async def delete_active_preparation_plan(database, user_id: str) -> bool:
    active = await database.user_preparation_plans.find_one(
        {"user_id": user_id, "is_active": True},
        {"_id": 0, "id": 1},
        sort=[("updated_at", -1)],
    )
    if not active:
        return False
    return await _delete_plan_cascade(database, user_id, active["id"])


async def get_active_plan_assigned_problem_map(database, user_id: str) -> Dict[str, Dict[str, Any]]:
    plan = await get_active_preparation_plan(database, user_id)
    if not plan:
        return {}
    out: Dict[str, Dict[str, Any]] = {}
    for day in plan.get("days", []):
        for problem in day.get("problems", []):
            pid = str(problem.get("problemId") or "")
            if not pid:
                continue
            out[pid] = {
                "day": day.get("day"),
                "focusTopic": day.get("focusTopic"),
                "status": problem.get("status"),
            }
    return out

