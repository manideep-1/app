from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid

# Languages that must have types in signature schema when using per-language types
SUPPORTED_LANGUAGES = ("python", "javascript", "java", "cpp", "c", "go", "csharp", "typescript")


class UserRole(str, Enum):
    USER = "user"
    PREMIUM = "premium"
    ADMIN = "admin"


class Difficulty(str, Enum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class SubmissionStatus(str, Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    WRONG_ANSWER = "wrong_answer"
    TIME_LIMIT_EXCEEDED = "time_limit_exceeded"
    MEMORY_LIMIT_EXCEEDED = "memory_limit_exceeded"
    RUNTIME_ERROR = "runtime_error"
    COMPILE_ERROR = "compile_error"


class Language(str, Enum):
    JAVA = "java"
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    CPP = "cpp"
    C = "c"
    GO = "go"
    CSHARP = "csharp"
    TYPESCRIPT = "typescript"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: Optional[str] = None


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class SendSignupOtpRequest(BaseModel):
    email: EmailStr


class VerifySignupOtpRequest(BaseModel):
    email: EmailStr
    otp: str
    username: str
    password: str
    full_name: Optional[str] = None


class GoogleSignInRequest(BaseModel):
    credential: str  # Google ID token from frontend


class User(UserBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: UserRole = UserRole.USER
    is_premium: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    solved_problems: List[str] = []
    total_submissions: int = 0


class UserInDB(User):
    hashed_password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


# Problem Models
class TestCase(BaseModel):
    input: str
    expected_output: str
    is_hidden: bool = False


class ProblemFunctionParam(BaseModel):
    """Parameter for the problem's solution function (name + type).
    When type_by_language is set, it takes precedence for generation (exact type per language)."""
    name: str
    type: str = ""  # Canonical fallback: int, int[], List[List[int]], etc.
    type_by_language: Optional[Dict[str, str]] = None  # e.g. {"java": "int[][]", "cpp": "vector<vector<int>>&"}


class ProblemFunctionMetadata(BaseModel):
    """SINGLE SOURCE OF TRUTH for the judge contract: function name, return type, parameters.
    When return_type_by_language is set, exact types per language are used (no canonical mapping).
    Starters and driver are generated from this; execution wrapper calls this function."""
    function_name: str
    return_type: str = ""  # Canonical fallback: int, int[], List[List[int]], void, etc.
    return_type_by_language: Optional[Dict[str, str]] = None  # e.g. {"java": "int[][]", "cpp": "vector<vector<int>>"}
    parameters: List[ProblemFunctionParam] = []


class CustomTestCase(BaseModel):
    input: str
    expected_output: Optional[str] = None  # Optional: when omitted, run shows output only (no pass/fail)


class ApproachComplexity(BaseModel):
    """Structured time/space complexity for an approach."""
    time: str = ""
    space: str = ""


class SolutionApproach(BaseModel):
    """Learning-first: Brute Force → Better → Optimal. Each approach has intuition, algorithm, code (all langs), complexity."""
    title: str  # e.g. "Brute Force", "Better (Two Pointers)", "Optimal (Hash Map)"
    content: Optional[str] = None  # Legacy: single block of text
    intuition: Optional[str] = None
    algorithm: Optional[str] = None
    code: Optional[str] = None  # Legacy: typically Python; prefer code_python for multi-language
    code_python: Optional[str] = None
    code_javascript: Optional[str] = None
    code_java: Optional[str] = None
    code_cpp: Optional[str] = None
    code_c: Optional[str] = None
    code_go: Optional[str] = None
    code_csharp: Optional[str] = None
    complexity: Optional[str] = None  # Human-readable: "Time: O(n). Space: O(1)."
    complexity_time: Optional[str] = None  # e.g. "O(n)"
    complexity_space: Optional[str] = None  # e.g. "O(1)"


class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    tags: List[str] = []
    companies: List[str] = []
    solution: Optional[str] = ""  # Legacy; do not use as sole solution—use solutions[] in learning order
    solutions: Optional[List[SolutionApproach]] = None  # LEARNING ORDER: Brute Force first, then Better, then Optimal
    prerequisites: Optional[List[str]] = None  # Data structure, algorithm pattern, required concepts (clickable tags)
    youtube_video_id: Optional[str] = None  # Cached YouTube video ID for "Video Explanation" section
    youtube_video_url: Optional[str] = None  # Fallback video/search URL when no curated YouTube ID is available
    common_pitfalls: Optional[str] = None  # At least 3 common mistakes; wrong vs correct; edge case warnings
    pitfalls: Optional[List[Dict[str, Any]]] = None  # Optional structured: [{title, wrong_example?, correct_example?, warning}]
    # Premium (NeetCode-level) solution content — see docs/SOLUTION_QUALITY_STANDARD.md
    pattern_recognition: Optional[str] = None  # Category, why, signals that indicate this pattern
    dry_run: Optional[str] = None  # Line-by-step walkthrough with sample input
    edge_cases: Optional[str] = None  # Empty, single element, duplicates, large input, overflow, etc.
    interview_tips: Optional[str] = None  # How to explain, follow-ups, how to optimize further
    hints: List[str] = []
    constraints: Optional[str] = None
    likes: int = 0
    dislikes: int = 0
    function_metadata: Optional[ProblemFunctionMetadata] = None


class ProblemCreate(ProblemBase):
    test_cases: List[TestCase]
    starter_code_python: Optional[str] = ""
    starter_code_javascript: Optional[str] = ""
    starter_code_java: Optional[str] = ""
    starter_code_cpp: Optional[str] = ""
    starter_code_c: Optional[str] = ""
    starter_code_go: Optional[str] = ""
    starter_code_csharp: Optional[str] = ""
    starter_code_typescript: Optional[str] = ""
    driver_code_python: Optional[str] = ""
    driver_code_javascript: Optional[str] = ""
    driver_code_java: Optional[str] = ""
    driver_code_cpp: Optional[str] = ""
    driver_code_c: Optional[str] = ""
    driver_code_go: Optional[str] = ""
    driver_code_csharp: Optional[str] = ""
    driver_code_typescript: Optional[str] = ""


class Problem(ProblemBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_cases: List[TestCase]
    starter_code_python: str = ""
    starter_code_javascript: str = ""
    starter_code_java: str = ""
    starter_code_cpp: str = ""
    starter_code_c: str = ""
    starter_code_go: str = ""
    starter_code_csharp: str = ""
    starter_code_typescript: str = ""
    driver_code_python: str = ""
    driver_code_javascript: str = ""
    driver_code_java: str = ""
    driver_code_cpp: str = ""
    driver_code_c: str = ""
    driver_code_go: str = ""
    driver_code_csharp: str = ""
    driver_code_typescript: str = ""
    acceptance_rate: float = 0.0
    total_submissions: int = 0
    accepted_submissions: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str = ""


# Submission Models
class SubmissionCreate(BaseModel):
    problem_id: str
    code: str
    language: Language


class RunCodeRequest(BaseModel):
    problem_id: str
    code: str
    language: Language
    custom_test_cases: Optional[List[CustomTestCase]] = None


class PlaygroundRunRequest(BaseModel):
    code: str
    language: Language
    input: Optional[str] = ""


class SubmissionResult(BaseModel):
    passed: int
    total: int
    test_results: List[Dict[str, Any]]
    runtime: Optional[float] = None
    memory: Optional[float] = None


class Submission(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    problem_id: str
    code: str
    language: Language
    status: SubmissionStatus
    result: Optional[SubmissionResult] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# User Progress Models
class UserProgress(BaseModel):
    easy_solved: int = 0
    medium_solved: int = 0
    hard_solved: int = 0
    total_solved: int = 0
    total_submissions: int = 0
    recent_submissions: List[str] = []
    solved_problem_ids: List[str] = []
    attempted_problem_ids: List[str] = []  # submitted but not accepted


# --- AI Coach Models ---
class CoachHintRequest(BaseModel):
    problem_id: str
    code: str
    hint_level: int  # 1-4


class CoachCodeReviewRequest(BaseModel):
    problem_id: str
    code: str
    language: Language
    status: str  # submission status


class CoachDebugRequest(BaseModel):
    problem_id: str
    code: str
    status: str
    failing_test_info: Optional[str] = None


class CoachConceptRequest(BaseModel):
    problem_id: str


class CoachChatRequest(BaseModel):
    problem_id: str
    message: str


class CoachMentorRequest(BaseModel):
    """For AI Coaching Agent: personalized DSA / interview prep (no problem context)."""
    message: str


class CoachFullSolutionRequest(BaseModel):
    problem_id: str
    request_text: str  # user's explicit request for solution


class CoachChatUnifiedRequest(BaseModel):
    """Unified coach chat: works with or without problem context. Supports sessions."""
    message: str
    session_id: Optional[str] = None
    problem_id: Optional[str] = None
    problem_context: Optional[dict] = None  # title, description, language, user_code if from problem page
    user_code: Optional[str] = None
    language: Optional[str] = None


class PlanProblemStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class CoachGeneratePlanRequest(BaseModel):
    """Create a structured preparation plan and assign real problems."""
    model_config = ConfigDict(populate_by_name=True)

    duration_days: int = Field(default=14, alias="durationDays")
    daily_hours: float = Field(default=3.0, alias="dailyHours")
    target_company: str = Field(default="Generic", alias="targetCompany")
    difficulty_preference: str = Field(default="balanced", alias="difficultyPreference")
    user_weak_topics: Optional[List[str]] = Field(default=None, alias="userWeakTopics")
    replace_existing: bool = Field(default=False, alias="replaceExisting")


class CoachUpdatePlanProblemStatusRequest(BaseModel):
    status: PlanProblemStatus


# DB: Coach chat sessions (per user)
class CoachSessionInDB(BaseModel):
    id: str
    user_id: str
    problem_id: Optional[str] = None
    title: str = "New chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# DB: Coach messages within a session
class CoachMessageInDB(BaseModel):
    id: str
    session_id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# DB: AI feedback history (for logging and personalization)
class AIFeedbackRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    problem_id: str
    kind: str  # hint | code_review | debug | concept | chat | full_solution
    hint_level: Optional[int] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    response_preview: Optional[str] = None  # first 200 chars for analytics


# DB: User weakness / learning metrics (for recommendations)
class UserWeaknessMetrics(BaseModel):
    user_id: str
    weak_topics: List[str] = []  # topics with repeated wrong/TLE
    tle_count: int = 0
    accuracy_by_topic: Dict[str, float] = {}  # topic -> 0.0-1.0
    last_updated: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# DB: Preparation plan header (per user)
class UserPreparationPlanInDB(BaseModel):
    id: str
    user_id: str
    target_company: str
    duration_days: int
    daily_hours: float
    difficulty_preference: str = "balanced"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = True


# DB: Preparation plan day buckets
class UserPlanDayInDB(BaseModel):
    id: str
    plan_id: str
    day_number: int
    focus_topic: str
    is_revision_day: bool = False
    is_mock_interview_day: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# DB: Problems assigned under each plan day
class UserPlanProblemInDB(BaseModel):
    id: str
    plan_day_id: str
    problem_id: str
    status: PlanProblemStatus = PlanProblemStatus.NOT_STARTED
    assigned_order: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
