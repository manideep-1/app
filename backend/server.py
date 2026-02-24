from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
import re
import secrets
import time
import uuid
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone, timedelta
from collections import defaultdict

from models import (
    User, UserCreate, UserLogin, UserInDB, Token,
    SendSignupOtpRequest, VerifySignupOtpRequest, GoogleSignInRequest,
    Problem, ProblemCreate, Submission, SubmissionCreate, RunCodeRequest,
    PlaygroundRunRequest,
    UserProgress, Difficulty, SubmissionStatus, Language, TestCase,
    CoachHintRequest, CoachCodeReviewRequest, CoachDebugRequest,
    CoachConceptRequest, CoachChatRequest, CoachFullSolutionRequest,
    AIFeedbackRecord, UserWeaknessMetrics,
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, get_current_user, get_current_admin_user, security
)
from code_executor import CodeExecutor, get_available_runtimes
from email_otp import send_otp_email, get_otp_expire_minutes, generate_otp
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from seed_hints import get_hints_for_problem
from seed_solutions import get_solutions_for_problem
from starter_from_solution import apply_starters_from_solutions
from ai.service import AICoachService
from ai.safety import looks_like_injection, sanitize_for_llm

logger = logging.getLogger(__name__)
GENERIC_SOLUTION_PREFIX = "Implement based on the problem description and examples."

# Code execution limits
MAX_CODE_LENGTH = 100_000
RATE_LIMIT_MAX = 60
RATE_LIMIT_WINDOW = 60  # seconds
_rate_limit_buckets = defaultdict(list)  # user_id -> [timestamps]
COACH_RATE_LIMIT_MAX = 20
COACH_RATE_LIMIT_WINDOW = 60
_coach_rate_limit_buckets = defaultdict(list)

def _rate_limit_check(user_id: str) -> None:
    """Raise HTTPException 429 if user exceeded rate limit."""
    now = time.time()
    bucket = _rate_limit_buckets[user_id]
    bucket[:] = [t for t in bucket if now - t < RATE_LIMIT_WINDOW]
    if len(bucket) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Too many requests. Please try again later.")
    bucket.append(now)


def _coach_rate_limit_check(user_id: str) -> None:
    now = time.time()
    bucket = _coach_rate_limit_buckets[user_id]
    bucket[:] = [t for t in bucket if now - t < COACH_RATE_LIMIT_WINDOW]
    if len(bucket) >= COACH_RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="If Else AI rate limit exceeded. Try again in a minute.")
    bucket.append(now)

def _execution_error_result(message: str, is_compile: bool = False) -> dict:
    """Return a structured execution result for compile/runtime errors."""
    status = SubmissionStatus.COMPILE_ERROR if is_compile else SubmissionStatus.RUNTIME_ERROR
    return {
        "status": status,
        "passed": 0,
        "total": 1,
        "test_results": [{
            "test_case": 1,
            "input": "",
            "expected": "",
            "output": message,
            "passed": False,
            "runtime": 0,
            "hidden": False,
            "custom": False,
        }],
        "runtime": 0,
        "memory": None,
    }

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

def _get_required_env(name: str) -> str:
    val = os.environ.get(name)
    if not val or not str(val).strip():
        raise RuntimeError(f"Missing required environment variable: {name}")
    return val.strip()

# MongoDB connection (validated on startup)
mongo_url = _get_required_env("MONGO_URL")
db_name = _get_required_env("DB_NAME")
client = AsyncIOMotorClient(mongo_url)
db = client[db_name]

# Create the main app
app = FastAPI(title="ifelse API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize code executor and AI coach
code_executor = CodeExecutor()
ai_coach = AICoachService(use_cache=True)

# LeetCode-style: user writes only the function; driver handles I/O. Merge user code + driver when driver exists.
def build_full_code(problem: dict, user_code: str, language: str) -> str:
    driver_key = f"driver_code_{language}"
    driver = (problem or {}).get(driver_key) or ""
    driver = (driver or "").strip()
    if not driver:
        return user_code
    return (user_code or "").strip() + "\n\n" + driver


# Dependency to inject db
async def get_db():
    return db


# ==================== AUTH ROUTES ====================
@api_router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, database=Depends(get_db)):
    # Check if user already exists
    existing_user = await database.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await database.users.find_one({"username": user_data.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name
    )
    user_in_db = UserInDB(**user.model_dump(), hashed_password=get_password_hash(user_data.password))
    
    # Save to database
    user_dict = user_in_db.model_dump()
    user_dict['created_at'] = user_dict['created_at'].isoformat()
    await database.users.insert_one(user_dict)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.post("/auth/send-signup-otp")
async def send_signup_otp(body: SendSignupOtpRequest, database=Depends(get_db)):
    """Send a 6-digit OTP to the given email for signup verification."""
    existing = await database.users.find_one({"email": body.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=get_otp_expire_minutes())
    await database.pending_signups.delete_many({"email": body.email})
    await database.pending_signups.insert_one({
        "email": body.email,
        "otp": otp,
        "expires_at": expires_at.isoformat(),
    })
    try:
        send_otp_email(body.email, otp)
    except RuntimeError as e:
        await database.pending_signups.delete_many({"email": body.email})
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    return {"message": "OTP sent to your email"}


@api_router.post("/auth/verify-signup-otp", response_model=Token, status_code=status.HTTP_201_CREATED)
async def verify_signup_otp(body: VerifySignupOtpRequest, database=Depends(get_db)):
    """Verify OTP and create the user; returns tokens."""
    pending = await database.pending_signups.find_one({"email": body.email})
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please request a new code.",
        )
    expires_at = datetime.fromisoformat(pending["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        await database.pending_signups.delete_many({"email": body.email})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new code.",
        )
    if pending["otp"] != body.otp.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP.",
        )
    existing_user = await database.users.find_one({"email": body.email})
    if existing_user:
        await database.pending_signups.delete_many({"email": body.email})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    existing_username = await database.users.find_one({"username": body.username})
    if existing_username:
        await database.pending_signups.delete_many({"email": body.email})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user = User(
        email=body.email,
        username=body.username,
        full_name=body.full_name,
    )
    user_in_db = UserInDB(**user.model_dump(), hashed_password=get_password_hash(body.password))
    user_dict = user_in_db.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    await database.users.insert_one(user_dict)
    await database.pending_signups.delete_many({"email": body.email})
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, database=Depends(get_db)):
    # Find user
    user = await database.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    user_in_db = UserInDB(**user)
    
    # Verify password
    if not verify_password(credentials.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create tokens
    access_token = create_access_token(data={"sub": user_in_db.id})
    refresh_token = create_refresh_token(data={"sub": user_in_db.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


async def _unique_username_from_email(database, email: str, full_name: Optional[str]) -> str:
    """Generate a unique username from email (local part) or name; append suffix if needed."""
    local = email.split("@")[0] if "@" in email else email
    base = re.sub(r"[^a-zA-Z0-9_]", "", local)[:20] or "user"
    base = base.lower()
    candidate = base
    n = 0
    while await database.users.find_one({"username": candidate}):
        n += 1
        candidate = f"{base}{n}" if n <= 999 else f"{base}_{secrets.token_hex(2)}"
    return candidate


@api_router.post("/auth/google", response_model=Token)
async def google_signin(body: GoogleSignInRequest, database=Depends(get_db)):
    """Sign in or sign up with Google ID token (credential from frontend)."""
    client_id = os.environ.get("GOOGLE_CLIENT_ID")
    if not client_id:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured",
        )
    try:
        idinfo = google_id_token.verify_oauth2_token(
            body.credential, google_requests.Request(), client_id
        )
    except ValueError as e:
        logging.warning("Google token verification failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google sign-in token",
        ) from e
    email = idinfo.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not provide an email",
        )
    name = idinfo.get("name") or idinfo.get("given_name") or ""
    existing = await database.users.find_one({"email": email}, {"_id": 0})
    if existing:
        user_id = existing["id"]
    else:
        username = await _unique_username_from_email(database, email, name)
        user = User(
            email=email,
            username=username,
            full_name=name or None,
        )
        user_in_db = UserInDB(
            **user.model_dump(),
            hashed_password=get_password_hash(secrets.token_urlsafe(32)),
        )
        user_dict = user_in_db.model_dump()
        user_dict["created_at"] = user_dict["created_at"].isoformat()
        await database.users.insert_one(user_dict)
        user_id = user.id
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(database=Depends(get_db), credentials=Depends(security)):
    current_user = await get_current_user(credentials, database)
    return User(**current_user.model_dump())


# ==================== PROBLEMS ROUTES ====================
@api_router.get("/problems/meta")
async def get_problems_meta(database=Depends(get_db)):
    """Return distinct tags and companies with counts for filter chips."""
    cursor = database.problems.find({}, {"tags": 1, "companies": 1})
    tag_counts = {}
    company_counts = {}
    async for doc in cursor:
        for t in doc.get("tags") or []:
            tag_counts[t] = tag_counts.get(t, 0) + 1
        for c in doc.get("companies") or []:
            company_counts[c] = company_counts.get(c, 0) + 1
    tags = [{"name": t, "count": tag_counts[t]} for t in sorted(tag_counts.keys())]
    companies = [{"name": c, "count": company_counts[c]} for c in sorted(company_counts.keys())]
    return {"tags": tags, "companies": companies}


@api_router.get("/runtimes")
async def get_runtimes():
    """Return which language runtimes are available on the server (python, javascript, java, cpp, c). No auth required."""
    return get_available_runtimes()


@api_router.get("/problems", response_model=List[Problem])
async def get_problems(
    difficulty: Optional[Difficulty] = None,
    tag: Optional[str] = None,
    company: Optional[str] = None,
    database=Depends(get_db)
):
    query = {}
    if difficulty:
        query["difficulty"] = difficulty
    if tag:
        query["tags"] = tag
    if company:
        query["companies"] = company
    
    problems = await database.problems.find(query, {"_id": 0}).to_list(1000)
    
    for problem in problems:
        if isinstance(problem.get('created_at'), str):
            problem['created_at'] = datetime.fromisoformat(problem['created_at'])
        total = problem.get('total_submissions') or 0
        accepted = problem.get('accepted_submissions') or 0
        problem['acceptance_rate'] = round(100 * accepted / total, 1) if total > 0 else 0.0
        hints = get_hints_for_problem(problem.get('title'))
        if hints is not None:
            problem['hints'] = list(hints)
    
    return problems


@api_router.get("/problems/{problem_id}", response_model=Problem)
async def get_problem(problem_id: str, database=Depends(get_db)):
    problem = await database.problems.find_one({"id": problem_id}, {"_id": 0})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if isinstance(problem.get('created_at'), str):
        problem['created_at'] = datetime.fromisoformat(problem['created_at'])
    total = problem.get('total_submissions') or 0
    accepted = problem.get('accepted_submissions') or 0
    problem['acceptance_rate'] = round(100 * accepted / total, 1) if total > 0 else 0.0
    hints = get_hints_for_problem(problem.get('title'))
    if hints is not None:
        problem['hints'] = list(hints)
    else:
        # Never show DB hints when we have no seed hints—avoids any generic or stale hints.
        problem['hints'] = []
    solutions = get_solutions_for_problem(problem.get('title'))
    if solutions is not None:
        approaches = solutions.get('approaches') if isinstance(solutions, dict) else solutions
        problem['solutions'] = approaches
        # Ensure starter templates match the solution function signatures
        if approaches:
            apply_starters_from_solutions(problem, approaches)
        if isinstance(solutions, dict):
            if solutions.get('prerequisites') is not None:
                problem['prerequisites'] = solutions['prerequisites']
            if solutions.get('common_pitfalls') is not None:
                problem['common_pitfalls'] = solutions['common_pitfalls']
    elif not problem.get('solutions'):
        fallback_solution = (problem.get('solution') or "").strip()
        if fallback_solution.startswith(GENERIC_SOLUTION_PREFIX) or not fallback_solution:
            fallback_solution = "Solution walkthrough will be added for this problem. Use the approach suggested by the topic tags and examples."
        problem['solutions'] = [{"title": "Solution", "content": fallback_solution}]
    
    # Hide input/expected_output for hidden test cases (user sees them only after submit)
    if problem.get("test_cases"):
        for tc in problem["test_cases"]:
            if tc.get("is_hidden"):
                tc["input"] = "Hidden"
                tc["expected_output"] = "Hidden"
    # Don't send driver code to client (used only on server for Run/Submit)
    for key in list(problem.keys()):
        if key.startswith("driver_code_"):
            del problem[key]
    return Problem(**problem)


@api_router.get("/problems/{problem_id}/related")
async def get_related_problems(problem_id: str, database=Depends(get_db)):
    """Return up to 5 related problems (same tags or same stack). Excludes current problem."""
    problem = await database.problems.find_one({"id": problem_id}, {"_id": 0, "tags": 1})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    tags = problem.get("tags") or []
    if not tags:
        cursor = database.problems.find({"id": {"$ne": problem_id}}, {"_id": 0, "id": 1, "title": 1, "difficulty": 1}).limit(5)
        related = await cursor.to_list(5)
        return related
    cursor = database.problems.find(
        {"id": {"$ne": problem_id}, "tags": {"$in": tags}},
        {"_id": 0, "id": 1, "title": 1, "difficulty": 1}
    ).limit(6)
    related = await cursor.to_list(6)
    seen = set()
    out = []
    for p in related:
        if p["id"] != problem_id and p["id"] not in seen:
            seen.add(p["id"])
            out.append(p)
            if len(out) >= 5:
                break
    return out


@api_router.post("/problems", response_model=Problem, status_code=status.HTTP_201_CREATED)
async def create_problem(
    problem_data: ProblemCreate,
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_admin_user(await get_current_user(credentials, database))
    
    problem = Problem(
        **problem_data.model_dump(),
        created_by=current_user.id
    )
    
    problem_dict = problem.model_dump()
    problem_dict['created_at'] = problem_dict['created_at'].isoformat()
    
    await database.problems.insert_one(problem_dict)
    return problem


# ==================== RUN CODE (sample tests only; no save) ====================
@api_router.post("/run")
async def run_code(
    body: RunCodeRequest,
    database=Depends(get_db),
    credentials=Depends(security)
):
    """Run code against visible/sample test cases + optional custom test cases. Does not save."""
    current_user = await get_current_user(credentials, database)
    if len((body.code or "")) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters.")
    _rate_limit_check(current_user.id)
    problem = await database.problems.find_one({"id": body.problem_id}, {"_id": 0})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    problem_obj = Problem(**problem)
    full_code = build_full_code(problem, body.code, body.language.value)
    # Visible test cases only (no hidden)
    test_cases = [tc for tc in problem_obj.test_cases if not tc.is_hidden]
    # Append user-added custom test cases (input only; no expected = show output only)
    if body.custom_test_cases:
        for c in body.custom_test_cases:
            exp = (c.expected_output or "").strip() or "__CUSTOM_OUTPUT_ONLY__"
            test_cases.append(TestCase(input=c.input, expected_output=exp, is_hidden=False))
    try:
        execution_result = code_executor.execute_code(
            full_code,
            body.language,
            test_cases,
            visible_only=False,  # we already filtered; no hidden in list
        )
    except Exception as e:
        logger.exception("Run code execution failed: %s", e)
        err_msg = str(e)
        is_compile = "compil" in err_msg.lower() or "syntax" in err_msg.lower()
        return _execution_error_result(err_msg, is_compile=is_compile)
    return execution_result


# ==================== PLAYGROUND / COMPILER (run raw code, no problem) ====================
@api_router.post("/run/playground")
async def run_playground(
    body: PlaygroundRunRequest,
    database=Depends(get_db),
    credentials=Depends(security)
):
    """Run raw code with optional stdin. No problem required. Auth required."""
    await get_current_user(credentials, database)
    try:
        import time
        start = time.time()
        output = code_executor._run_code(body.code, body.input or "", body.language)
        runtime_ms = round((time.time() - start) * 1000, 2)
        return {"output": output, "error": None, "runtime_ms": runtime_ms}
    except Exception as e:
        return {"output": "", "error": str(e), "runtime_ms": None}


# ==================== SUBMISSIONS ROUTES ====================
@api_router.post("/submissions", response_model=Submission, status_code=status.HTTP_201_CREATED)
async def submit_code(
    submission_data: SubmissionCreate,
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_user(credentials, database)
    if len((submission_data.code or "")) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters.")
    _rate_limit_check(current_user.id)

    # Get problem
    problem = await database.problems.find_one({"id": submission_data.problem_id}, {"_id": 0})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")

    problem_obj = Problem(**problem)
    full_code = build_full_code(problem, submission_data.code, submission_data.language.value)

    try:
        execution_result = code_executor.execute_code(
            full_code,
            submission_data.language,
            problem_obj.test_cases,
            visible_only=False,
        )
    except Exception as e:
        logger.exception("Submit code execution failed: %s", e)
        err_msg = str(e)
        is_compile = "compil" in err_msg.lower() or "syntax" in err_msg.lower()
        execution_result = _execution_error_result(err_msg, is_compile=is_compile)
        # Still create a submission record with failed status
        submission = Submission(
            user_id=current_user.id,
            problem_id=submission_data.problem_id,
            code=submission_data.code,
            language=submission_data.language,
            status=execution_result["status"],
            result={
                "passed": execution_result["passed"],
                "total": execution_result["total"],
                "test_results": execution_result["test_results"],
                "runtime": execution_result.get("runtime"),
                "memory": execution_result.get("memory"),
            },
        )
        submission_dict = submission.model_dump()
        submission_dict["created_at"] = submission_dict["created_at"].isoformat()
        await database.submissions.insert_one(submission_dict)
        await database.users.update_one({"id": current_user.id}, {"$inc": {"total_submissions": 1}})
        await database.problems.update_one(
            {"id": submission_data.problem_id},
            {"$inc": {"total_submissions": 1}},
        )
        return submission

    # Create submission (include runtime/memory in result)
    submission = Submission(
        user_id=current_user.id,
        problem_id=submission_data.problem_id,
        code=submission_data.code,
        language=submission_data.language,
        status=execution_result["status"],
        result={
            "passed": execution_result["passed"],
            "total": execution_result["total"],
            "test_results": execution_result["test_results"],
            "runtime": execution_result.get("runtime"),
            "memory": execution_result.get("memory"),
        }
    )
    
    submission_dict = submission.model_dump()
    submission_dict['created_at'] = submission_dict['created_at'].isoformat()
    
    await database.submissions.insert_one(submission_dict)
    
    # Update user stats
    await database.users.update_one(
        {"id": current_user.id},
        {"$inc": {"total_submissions": 1}}
    )
    
    # Update problem stats
    await database.problems.update_one(
        {"id": submission_data.problem_id},
        {"$inc": {
            "total_submissions": 1,
            "accepted_submissions": 1 if execution_result["status"] == SubmissionStatus.ACCEPTED else 0
        }}
    )
    
    # If accepted, add to solved problems
    if execution_result["status"] == SubmissionStatus.ACCEPTED:
        await database.users.update_one(
            {"id": current_user.id},
            {"$addToSet": {"solved_problems": submission_data.problem_id}}
        )
    
    return submission


@api_router.get("/submissions", response_model=List[Submission])
async def get_submissions(
    problem_id: Optional[str] = None,
    status: Optional[SubmissionStatus] = None,
    language: Optional[Language] = None,
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_user(credentials, database)
    
    query = {"user_id": current_user.id}
    if problem_id:
        query["problem_id"] = problem_id
    if status is not None:
        query["status"] = status
    if language is not None:
        query["language"] = language
    
    submissions = await database.submissions.find(query, {"_id": 0}).sort("created_at", -1).to_list(100)
    
    # Convert datetime strings
    for submission in submissions:
        if isinstance(submission.get('created_at'), str):
            submission['created_at'] = datetime.fromisoformat(submission['created_at'])
    
    return submissions


@api_router.get("/submissions/{submission_id}", response_model=Submission)
async def get_submission(
    submission_id: str,
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_user(credentials, database)
    
    submission = await database.submissions.find_one(
        {"id": submission_id, "user_id": current_user.id},
        {"_id": 0}
    )
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    if isinstance(submission.get('created_at'), str):
        submission['created_at'] = datetime.fromisoformat(submission['created_at'])
    
    return Submission(**submission)


# ==================== AI COACH ROUTES ====================
async def _get_problem_meta(database, problem_id: str):
    """Return problem title, difficulty, tags for coach (or None)."""
    p = await database.problems.find_one({"id": problem_id}, {"_id": 0, "title": 1, "difficulty": 1, "tags": 1})
    return p


async def _get_problem_for_chat(database, problem_id: str):
    """Return problem with description and visible test cases for chat context (or None)."""
    p = await database.problems.find_one(
        {"id": problem_id},
        {"_id": 0, "title": 1, "difficulty": 1, "tags": 1, "description": 1, "test_cases": 1},
    )
    if not p:
        return None
    # Build examples from non-hidden test cases only
    examples_lines = []
    for i, tc in enumerate((p.get("test_cases") or [])[:5]):
        if tc.get("is_hidden"):
            continue
        inp = (tc.get("input") or "").strip()
        out = (tc.get("expected_output") or "").strip()
        if inp or out:
            examples_lines.append(f"Example {len(examples_lines) + 1}: Input: {inp[:500]}\nExpected output: {out[:500]}")
    p["examples_text"] = "\n\n".join(examples_lines) if examples_lines else "No examples provided."
    return p


async def _log_ai_feedback(database, user_id: str, problem_id: str, kind: str, response_text: str, hint_level: Optional[int] = None):
    """Store AI feedback for analytics and personalization."""
    try:
        record = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "problem_id": problem_id,
            "kind": kind,
            "hint_level": hint_level,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "response_preview": (response_text or "")[:200],
        }
        await database.ai_feedback_history.insert_one(record)
    except Exception as e:
        logger.warning("Failed to log AI feedback: %s", e)


@api_router.post("/coach/hint")
async def coach_hint(
    body: CoachHintRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Progressive hint (level 1–4). Does not leak full solution."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    problem = await _get_problem_meta(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    level = max(1, min(4, body.hint_level or 1))
    try:
        response = ai_coach.get_progressive_hint(
            problem_title=problem["title"],
            difficulty=problem.get("difficulty") or "medium",
            tags=problem.get("tags") or [],
            code=body.code or "",
            hint_level=level,
        )
    except Exception as e:
        logger.exception("Coach hint failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "hint", response, hint_level=level)
    return {"hint_level": level, "text": response}


@api_router.post("/coach/code-review")
async def coach_code_review(
    body: CoachCodeReviewRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Structured code review after submit: what's good, what to improve, better approach (no full code)."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    problem = await _get_problem_meta(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        response = ai_coach.code_review(
            problem_title=problem["title"],
            difficulty=problem.get("difficulty") or "medium",
            tags=problem.get("tags") or [],
            code=body.code or "",
            status=body.status,
            language=body.language.value,
        )
    except Exception as e:
        logger.exception("Coach code review failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "code_review", response)
    return {"feedback": response}


@api_router.post("/coach/debug")
async def coach_debug(
    body: CoachDebugRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Debug help when submission failed: explain error, where to look, how to fix (no full solution)."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    problem = await _get_problem_meta(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        response = ai_coach.debug_help(
            problem_title=problem["title"],
            code=body.code or "",
            status=body.status,
            failing_test_info=body.failing_test_info,
        )
    except Exception as e:
        logger.exception("Coach debug failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "debug", response)
    return {"text": response}


@api_router.post("/coach/explain-concept")
async def coach_explain_concept(
    body: CoachConceptRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Explain concept relevant to the problem (no solution code)."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    problem = await _get_problem_meta(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        response = ai_coach.explain_concept(
            problem_title=problem["title"],
            tags=problem.get("tags") or [],
        )
    except Exception as e:
        logger.exception("Coach explain concept failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "concept", response)
    return {"text": response}


@api_router.get("/coach/recommendations")
async def coach_recommendations(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Personalized next problems, revision topics, study plan."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    solved_ids = current_user.solved_problems or []
    attempted_set = set()
    async for doc in database.submissions.find(
        {"user_id": current_user.id, "status": {"$ne": "accepted"}},
        {"_id": 0, "problem_id": 1},
    ):
        attempted_set.add(doc.get("problem_id"))
    attempted_ids = list(attempted_set - set(solved_ids))
    solved_titles = []
    if solved_ids:
        cursor = database.problems.find({"id": {"$in": solved_ids}}, {"_id": 0, "title": 1})
        async for p in cursor:
            solved_titles.append(p.get("title") or "")
    attempted_titles = []
    if attempted_ids:
        cursor = database.problems.find({"id": {"$in": attempted_ids}}, {"_id": 0, "title": 1})
        async for p in cursor:
            attempted_titles.append(p.get("title") or "")
    weak_topics = []
    metrics = await database.user_weakness_metrics.find_one({"user_id": current_user.id}, {"_id": 0, "weak_topics": 1})
    if metrics:
        weak_topics = metrics.get("weak_topics") or []
    recent = await database.submissions.find(
        {"user_id": current_user.id},
        {"_id": 0, "status": 1}
    ).sort("created_at", -1).limit(20).to_list(20)
    recent_statuses = [r.get("status") for r in recent if r.get("status")]
    try:
        result = ai_coach.get_recommendations(
            solved_titles=solved_titles,
            attempted_titles=attempted_titles,
            weak_topics=weak_topics,
            recent_statuses=recent_statuses,
        )
    except Exception as e:
        logger.exception("Coach recommendations failed: %s", e)
        result = {"next_problems": [], "revision_topics": [], "study_plan": "Keep practicing! Try problems from topics you've attempted."}
    return result


@api_router.post("/coach/chat")
async def coach_chat(
    body: CoachChatRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Interview simulation or general chat. Problem context is injected so AI doesn't ask for problem statement."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    if looks_like_injection(body.message):
        raise HTTPException(status_code=400, detail="Invalid message.")
    problem = await _get_problem_for_chat(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        response = ai_coach.chat(
            problem_title=problem["title"],
            user_message=body.message,
            problem_description=problem.get("description") or "",
            problem_examples=problem.get("examples_text") or "",
            difficulty=problem.get("difficulty") or "medium",
            tags=problem.get("tags") or [],
        )
    except Exception as e:
        logger.exception("Coach chat failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "chat", response)
    return {"text": response}


@api_router.post("/coach/full-solution")
async def coach_full_solution(
    body: CoachFullSolutionRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Only when user explicitly requested full solution. Still applies leak check."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    problem = await _get_problem_meta(database, body.problem_id)
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    try:
        response = ai_coach.full_solution(
            problem_title=problem["title"],
            user_request=body.request_text or "",
        )
    except Exception as e:
        logger.exception("Coach full solution failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, body.problem_id, "full_solution", response)
    return {"text": response}


# ==================== USER PROGRESS ROUTES ====================
@api_router.get("/user/progress", response_model=UserProgress)
async def get_user_progress(database=Depends(get_db), credentials=Depends(security)):
    current_user = await get_current_user(credentials, database)

    solved_problems = current_user.solved_problems
    easy_count = medium_count = hard_count = 0
    if solved_problems:
        cursor = database.problems.find({"id": {"$in": solved_problems}}, {"_id": 0, "difficulty": 1})
        async for problem in cursor:
            d = problem.get("difficulty")
            if d == Difficulty.EASY:
                easy_count += 1
            elif d == Difficulty.MEDIUM:
                medium_count += 1
            elif d == Difficulty.HARD:
                hard_count += 1

    # Get recent submissions
    recent_submissions = await database.submissions.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    # Attempted = problem_ids with at least one submission, not in solved
    attempted_cursor = database.submissions.find(
        {"user_id": current_user.id, "status": {"$ne": "accepted"}},
        {"_id": 0, "problem_id": 1}
    )
    attempted_ids = set()
    async for doc in attempted_cursor:
        attempted_ids.add(doc["problem_id"])
    attempted_ids -= set(solved_problems)
    
    return UserProgress(
        easy_solved=easy_count,
        medium_solved=medium_count,
        hard_solved=hard_count,
        total_solved=len(solved_problems),
        total_submissions=current_user.total_submissions,
        recent_submissions=[s["id"] for s in recent_submissions],
        solved_problem_ids=solved_problems,
        attempted_problem_ids=list(attempted_ids),
    )


@api_router.delete("/user/progress", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_progress(database=Depends(get_db), credentials=Depends(security)):
    """Delete all user progress: submissions and solved/attempted state. Requires confirmation on frontend."""
    current_user = await get_current_user(credentials, database)
    await database.submissions.delete_many({"user_id": current_user.id})
    await database.users.update_one(
        {"id": current_user.id},
        {"$set": {"solved_problems": [], "total_submissions": 0}}
    )
    return None


# ==================== USER ACTIVITY / STREAK ====================
def _parse_created_to_date(created):
    """Parse created_at (str or datetime) to date or None."""
    if created is None:
        return None
    if isinstance(created, str):
        try:
            created = datetime.fromisoformat(created.replace("Z", "+00:00"))
        except Exception:
            return None
    try:
        return created.date() if hasattr(created, "date") else created
    except Exception:
        return None


@api_router.get("/user/activity")
async def get_user_activity(
    year: Optional[int] = None,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Return submission counts per day and streaks. Optional query param 'year' (e.g. 2024) for that calendar year; otherwise last 365 days. Includes available_years (last 5 years) for the year selector."""
    from datetime import timedelta
    from collections import defaultdict

    current_user = await get_current_user(credentials, database)
    now = datetime.now(timezone.utc)
    current_year = now.year
    available_years = [current_year - i for i in range(5)]

    if year is not None:
        year = max(min(year, current_year), current_year - 4)
        start_date = datetime(year, 1, 1, tzinfo=timezone.utc).date()
        end_date = datetime(year + 1, 1, 1, tzinfo=timezone.utc).date()
        start_str = start_date.isoformat()
        end_str = end_date.isoformat()
        query = {
            "user_id": current_user.id,
            "created_at": {"$gte": start_str, "$lt": end_str},
        }
    else:
        start_date = (now - timedelta(days=365)).date()
        query = {"user_id": current_user.id}
        end_date = now.date()

    cursor = database.submissions.find(query, {"_id": 0, "created_at": 1}).sort("created_at", -1)
    if year is None:
        cursor = cursor.limit(5000)

    dates_count = defaultdict(int)
    async for doc in cursor:
        created = doc.get("created_at")
        day = _parse_created_to_date(created)
        if day is None:
            continue
        if year is not None and (day < start_date or day >= end_date):
            continue
        if year is None and day < start_date:
            continue
        day_str = day.isoformat()
        dates_count[day_str] += 1

    submission_dates = list(dates_count.keys())

    # End date for "current" streak: today if in range, else last day of selected year
    streak_end = now.date() if year is None else min(now.date(), end_date - timedelta(days=1))
    streak = 0
    d = streak_end
    while d >= start_date:
        day_str = d.isoformat()
        if dates_count.get(day_str, 0) > 0:
            streak += 1
            d -= timedelta(days=1)
        else:
            break

    if not submission_dates:
        longest_streak = 0
    else:
        sorted_dates = sorted(set(submission_dates))
        longest_streak = 1
        current = 1
        for i in range(1, len(sorted_dates)):
            try:
                prev = datetime.fromisoformat(sorted_dates[i - 1]).date()
                curr = datetime.fromisoformat(sorted_dates[i]).date()
            except Exception:
                continue
            if (curr - prev).days == 1:
                current += 1
                longest_streak = max(longest_streak, current)
            else:
                current = 1

    return {
        "year": year if year is not None else current_year,
        "available_years": available_years,
        "submission_dates": submission_dates,
        "dates_count": dict(dates_count),
        "current_streak": streak,
        "longest_streak": longest_streak,
    }


# ==================== HEALTH CHECK & RUNTIMES ====================
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ifelse API"}


@api_router.get("/runtimes")
async def get_runtimes():
    """Return which language runtimes are available (python, javascript, java, cpp, c). Useful for UI to disable or warn when a runtime is missing."""
    return get_available_runtimes()


# Include the router in the main app
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    logger.exception("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.on_event("startup")
async def startup_validate():
    """Validate env, create indexes, ping DB."""
    _get_required_env("MONGO_URL")
    _get_required_env("DB_NAME")
    try:
        await db.command("ping")
    except Exception as e:
        logger.warning("MongoDB ping on startup: %s", e)
    try:
        await db.problems.create_index("id", unique=True)
        await db.problems.create_index("difficulty")
        await db.problems.create_index("tags")
        await db.submissions.create_index([("user_id", 1), ("problem_id", 1)])
        await db.submissions.create_index("created_at")
        await db.ai_feedback_history.create_index([("user_id", 1), ("created_at", -1)])
        await db.user_weakness_metrics.create_index("user_id", unique=True)
        logger.info("Database indexes ensured.")
    except Exception as e:
        logger.warning("Index creation (may already exist): %s", e)


app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Log which runtimes are available at startup (so missing Java etc. is visible in logs)
try:
    runtimes = get_available_runtimes()
    missing = [lang for lang, ok in runtimes.items() if not ok]
    if missing:
        logger.info("Code runtimes available: %s; missing (install if you need them): %s", runtimes, missing)
    else:
        logger.info("Code runtimes: all available %s", runtimes)
except Exception as e:
    logger.warning("Could not check runtimes: %s", e)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
