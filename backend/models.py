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


class ProblemBase(BaseModel):
    title: str
    description: str
    difficulty: Difficulty
    tags: List[str] = []
    companies: List[str] = []


class ProblemCreate(ProblemBase):
    test_cases: List[TestCase]
    starter_code_python: Optional[str] = ""
    starter_code_javascript: Optional[str] = ""


class Problem(ProblemBase):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    test_cases: List[TestCase]
    starter_code_python: str = ""
    starter_code_javascript: str = ""
    acceptance_rate: float = 0.0
    total_submissions: int = 0
    accepted_submissions: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    created_by: str


# Submission Models
class SubmissionCreate(BaseModel):
    problem_id: str
    code: str
    language: Language


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
