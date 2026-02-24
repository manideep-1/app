from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from enum import Enum
import uuid


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
    RUNTIME_ERROR = "runtime_error"
    COMPILE_ERROR = "compile_error"


class Language(str, Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    JAVA = "java"
    CPP = "cpp"
    C = "c"


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


class CustomTestCase(BaseModel):
    input: str
    expected_output: Optional[str] = None  # Optional: when omitted, run shows output only (no pass/fail)


class SolutionApproach(BaseModel):
    title: str  # e.g. "1. Brute Force", "2. Two Stacks"
    content: Optional[str] = None  # Legacy: single block of text
    intuition: Optional[str] = None
    algorithm: Optional[str] = None
    code: Optional[str] = None  # Legacy: typically Python; prefer code_python for multi-language
    code_python: Optional[str] = None
    code_javascript: Optional[str] = None
    code_java: Optional[str] = None
    code_cpp: Optional[str] = None
    code_c: Optional[str] = None
    complexity: Optional[str] = None


class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    tags: List[str] = []
    companies: List[str] = []
    solution: Optional[str] = ""
    solutions: Optional[List[SolutionApproach]] = None  # Multiple approaches: brute force, optimal, etc.
    prerequisites: Optional[List[str]] = None  # e.g. "Stack Data Structure - ..."
    common_pitfalls: Optional[str] = None
    hints: List[str] = []
    constraints: Optional[str] = None  # Optional constraints section (markdown/text)
    likes: int = 0
    dislikes: int = 0


class ProblemCreate(ProblemBase):
    test_cases: List[TestCase]
    starter_code_python: Optional[str] = ""
    starter_code_javascript: Optional[str] = ""
    starter_code_java: Optional[str] = ""
    starter_code_cpp: Optional[str] = ""
    starter_code_c: Optional[str] = ""
    driver_code_python: Optional[str] = ""
    driver_code_javascript: Optional[str] = ""
    driver_code_java: Optional[str] = ""
    driver_code_cpp: Optional[str] = ""
    driver_code_c: Optional[str] = ""


class Problem(ProblemBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_cases: List[TestCase]
    starter_code_python: str = ""
    starter_code_javascript: str = ""
    starter_code_java: str = ""
    starter_code_cpp: str = ""
    starter_code_c: str = ""
    driver_code_python: str = ""
    driver_code_javascript: str = ""
    driver_code_java: str = ""
    driver_code_cpp: str = ""
    driver_code_c: str = ""
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


class CoachFullSolutionRequest(BaseModel):
    problem_id: str
    request_text: str  # user's explicit request for solution


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
