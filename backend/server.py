from fastapi import FastAPI, APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from starlette.concurrency import run_in_threadpool
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
from urllib.parse import quote_plus

from models import (
    User, UserCreate, UserLogin, UserInDB, Token, UserRole,
    RefreshTokenRequest, ChangePasswordRequest,
    SendSignupOtpRequest, VerifySignupOtpRequest, GoogleSignInRequest,
    Problem, ProblemCreate, Submission, SubmissionCreate, RunCodeRequest,
    PlaygroundRunRequest,
    UserProgress, Difficulty, SubmissionStatus, Language, TestCase,
    CoachHintRequest, CoachCodeReviewRequest, CoachDebugRequest,
    CoachConceptRequest, CoachChatRequest, CoachMentorRequest, CoachFullSolutionRequest,
    CoachChatUnifiedRequest, CoachSessionInDB, CoachMessageInDB,
    AIFeedbackRecord, UserWeaknessMetrics,
    CoachGeneratePlanRequest, CoachUpdatePlanProblemStatusRequest,
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, get_current_user, get_current_admin_user, security, get_user_id_from_refresh_token
)
from code_executor import CodeExecutor, get_available_runtimes
from docker_executor import run_in_docker
from signature_validator import validate_signature
from email_otp import send_otp_email, get_otp_expire_minutes, generate_otp, smtp_configured
from google.oauth2 import id_token as google_id_token
from google.auth.transport import requests as google_requests
from seed_hints import get_hints_for_problem
from seed_solutions import get_solutions_for_problem
from seed_starters import title_to_function_name
from ai.service import AICoachService
from ai.safety import looks_like_injection, sanitize_for_llm
from test_case_validation import (
    validate_no_duplicates_within_problem,
    validate_no_duplicate_inputs,
    validate_test_case_requirements,
    all_visible_outputs_identical,
)
from solution_validator import validate_solution as validate_solution_integrity
from starter_template_generator import generate_starter_and_driver
from signature_contract import (
    REQUIRED_SIGNATURE_LANGS,
    LANG_CODE_KEY,
    align_solution_code_to_metadata,
    extract_signature,
    metadata_signature,
    signatures_match,
)
from preparation_plan_service import (
    ActivePlanExistsError,
    DEFAULT_DAILY_HOURS,
    DEFAULT_DURATION_DAYS,
    PlanGenerationError,
    delete_active_preparation_plan,
    generate_preparation_plan,
    get_active_plan_assigned_problem_map,
    get_active_preparation_plan,
    parse_plan_request_from_message,
    update_plan_problem_status,
)

logger = logging.getLogger(__name__)
GENERIC_SOLUTION_PREFIX = "Implement based on the problem description and examples."


def _ensure_starter_function_name(problem: dict) -> None:
    """Replace generic 'solve' in starter/driver code with problem-derived function name (e.g. findMedianFromDataStream)."""
    title = problem.get("title") or ""
    fn_name = title_to_function_name(title)
    for key in ("starter_code_python", "starter_code_javascript", "starter_code_java", "starter_code_cpp", "starter_code_c",
                "starter_code_go", "starter_code_csharp", "starter_code_typescript",
                "driver_code_python", "driver_code_javascript", "driver_code_java", "driver_code_cpp", "driver_code_c",
                "driver_code_go", "driver_code_csharp", "driver_code_typescript"):
        val = problem.get(key)
        if val and isinstance(val, str) and re.search(r"\bsolve\b", val):
            problem[key] = re.sub(r"\bsolve\b", fn_name, val)


def _youtube_search_url(title: str) -> str:
    q = quote_plus(f"{title} leetcode solution" if title else "leetcode solution")
    return f"https://www.youtube.com/results?search_query={q}"


_HELPER_LIKE_FN_NAMES = {
    "__init__",
    "constructor",
    "helper",
    "dfs",
    "bfs",
    "backtrack",
    "push",
    "pop",
    "top",
    "peek",
    "insert",
    "search",
    "startswith",
    "get",
    "put",
    "add",
    "addnum",
    "findmedian",
    "addnode",
    "removenode",
    "isbadversion",
}


def _prefer_problem_entrypoint_name(title: str, fn_name: str) -> str:
    """For inferred schemas, avoid helper/class-method names as the public entrypoint."""
    canonical = title_to_function_name(title or "")
    current = (fn_name or "").strip()
    if not canonical:
        return current
    low = current.lower()
    if not current or low in _HELPER_LIKE_FN_NAMES or (low.startswith("__") and low.endswith("__")):
        return canonical
    return current


def _starter_contract_function_name(problem: dict) -> str:
    """Prefer starter signature as callable contract when available."""
    for lang in ("python", "javascript", "java", "cpp", "go", "csharp", "typescript"):
        starter = (problem.get(f"starter_code_{lang}") or "").strip()
        if not starter:
            continue
        sig = extract_signature(starter, lang)
        if sig and sig.function_name:
            return (sig.function_name or "").strip()
    return ""


def _load_solution_approaches_for_title(title: str) -> List[dict]:
    """Load solution approaches for metadata inference/alignment."""
    try:
        data = get_solutions_for_problem(title or "")
    except Exception:
        return []
    if isinstance(data, dict):
        approaches = data.get("approaches") or data.get("solutions") or []
    elif isinstance(data, list):
        approaches = data
    else:
        approaches = []
    return [a for a in approaches if isinstance(a, dict)]


def _recover_inferred_params_from_approaches(meta: dict, approaches: List[dict]) -> None:
    """When inferred metadata has no params (often due class-style snippets), recover from typed signatures."""
    if not isinstance(meta, dict) or meta.get("parameters") or not approaches:
        return
    code_keys = (
        ("code_java", "java"),
        ("code_cpp", "cpp"),
        ("code_go", "go"),
        ("code_csharp", "csharp"),
        ("code_javascript", "javascript"),
        ("code_python", "python"),
        ("code_typescript", "typescript"),
    )
    for code_key, lang in code_keys:
        for approach in approaches:
            sig = extract_signature((approach.get(code_key) or ""), lang)
            if not sig:
                continue
            cleaned = []
            for i, p in enumerate(sig.params):
                pname = (p.name or f"arg{i + 1}").strip() or f"arg{i + 1}"
                if pname.lower() in {"self", "cls"}:
                    continue
                ptype = (p.type or "").strip() or "int"
                cleaned.append({"name": pname, "type": ptype})
            if cleaned:
                meta["parameters"] = cleaned
                recovered_return = (sig.return_type or "").strip()
                if recovered_return and (not meta.get("return_type")):
                    meta["return_type"] = recovered_return
                return


def _resolve_problem_metadata(problem: dict, approaches: Optional[List[dict]] = None) -> tuple[Optional[dict], Optional[str]]:
    """Resolve function metadata using DB -> registry -> inferred fallback."""
    meta = problem.get("function_metadata")
    meta_source = "db" if (meta and isinstance(meta, dict)) else None

    if not meta or not isinstance(meta, dict):
        try:
            from problem_metadata_registry import get_metadata
            entry = get_metadata(problem.get("title") or "")
            if entry is not None:
                metadata_obj, _ = entry
                meta = metadata_obj.model_dump()
                meta_source = "registry"
        except Exception:
            pass

    if not meta or not isinstance(meta, dict):
        try:
            from seed_solutions import _infer_alignment_metadata
            inferred = _infer_alignment_metadata(problem.get("title") or "", approaches or [])
            if inferred is not None:
                meta = inferred.model_dump() if hasattr(inferred, "model_dump") else inferred
                meta_source = "inferred"
        except Exception:
            pass

    if meta and isinstance(meta, dict) and meta_source == "inferred":
        starter_fn = _starter_contract_function_name(problem)
        if starter_fn:
            meta["function_name"] = starter_fn
        else:
            meta["function_name"] = _prefer_problem_entrypoint_name(
                problem.get("title") or "",
                meta.get("function_name") or "",
            )
        params = meta.get("parameters")
        if isinstance(params, list) and params:
            first = params[0] if isinstance(params[0], dict) else None
            first_name = ((first or {}).get("name") or "").strip().lower()
            if first_name in {"self", "cls"}:
                meta["parameters"] = params[1:]
        _recover_inferred_params_from_approaches(meta, approaches or [])

    return (meta if isinstance(meta, dict) else None, meta_source)


def _ensure_problem_execution_metadata(problem: dict) -> None:
    """Ensure run/submit paths have function metadata so driver generation works (esp. Java Main wrapper)."""
    approaches = [a for a in (problem.get("solutions") or []) if isinstance(a, dict)]
    if not approaches:
        approaches = _load_solution_approaches_for_title(problem.get("title") or "")
    meta, _ = _resolve_problem_metadata(problem, approaches)
    if meta and isinstance(meta, dict):
        problem["function_metadata"] = meta


SOLUTION_LANGUAGE_CODE_KEY = {
    "python": "code_python",
    "javascript": "code_javascript",
    "java": "code_java",
    "cpp": "code_cpp",
    "go": "code_go",
    "csharp": "code_csharp",
    "typescript": "code_typescript",
    "c": "code_c",
}


def _language_contract_ready(problem: dict, language: str) -> bool:
    """A solution language is shown only when this problem has a runnable starter+driver contract."""
    starter = (problem.get(f"starter_code_{language}") or "").strip()
    driver = (problem.get(f"driver_code_{language}") or "").strip()
    return bool(starter and driver)


def _filter_solution_languages_by_contract(problem: dict, approaches: List[dict]) -> List[dict]:
    """Return approaches with all solution code intact. Solution tab shows every language we have;
    runnable languages (starter+driver) are enforced elsewhere for the code editor."""
    if not approaches:
        return approaches
    return [dict(a) if isinstance(a, dict) else a for a in approaches]

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

from database import client, db, get_db

# Create the main app
app = FastAPI(title="ifelse API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize code executor and AI coach
code_executor = CodeExecutor()
ai_coach = AICoachService(use_cache=True)

# Contract: function_metadata is the single source of truth. Driver is generated from metadata at execution time when present.
def _merge_header_prefixed_source(user_code: str, driver_code: str, header_re: str) -> str:
    """Merge two code blocks while keeping all header lines (imports/usings) at the top."""
    import re as _re

    user_headers: List[str] = []
    user_body: List[str] = []
    for ln in (user_code or "").splitlines():
        if _re.match(header_re, ln.strip()):
            user_headers.append(ln.strip())
        else:
            user_body.append(ln)

    driver_headers: List[str] = []
    driver_body: List[str] = []
    for ln in (driver_code or "").splitlines():
        if _re.match(header_re, ln.strip()):
            driver_headers.append(ln.strip())
        else:
            driver_body.append(ln)

    merged_headers: List[str] = []
    for h in [*user_headers, *driver_headers]:
        if h not in merged_headers:
            merged_headers.append(h)
    parts = []
    if merged_headers:
        parts.append("\n".join(merged_headers))
    if user_body:
        parts.append("\n".join(user_body).strip())
    if driver_body:
        parts.append("\n".join(driver_body).strip())
    return "\n\n".join(p for p in parts if p).strip()


def _is_generic_python_driver(driver_code: str) -> bool:
    src = (driver_code or "").strip()
    return (
        'if __name__ == "__main__":' in src
        and "data = sys.stdin.read().strip().split('\\n')" in src
        and "result =" in src
    )


def build_full_code(problem: dict, user_code: str, language: str) -> str:
    from starter_template_generator import generate_driver
    from models import ProblemFunctionMetadata
    user_code = (user_code or "").strip()
    driver_key = f"driver_code_{language}"
    existing_driver = ((problem or {}).get(driver_key) or "").strip()
    driver = existing_driver
    meta = problem.get("function_metadata")
    if not meta or not isinstance(meta, dict):
        try:
            from problem_metadata_registry import get_metadata
            entry = get_metadata((problem or {}).get("title") or "")
            if entry is not None:
                meta = entry[0].model_dump() if hasattr(entry[0], "model_dump") else entry[0]
        except Exception:
            pass
    metadata = None
    if meta and isinstance(meta, dict):
        try:
            metadata = ProblemFunctionMetadata(**meta)
            input_spec = []
            for p in (metadata.parameters or []):
                if isinstance(p, dict):
                    input_spec.append({"name": p.get("name", ""), "type": p.get("type", "str")})
                else:
                    input_spec.append({
                        "name": getattr(p, "name", ""),
                        "type": getattr(p, "type", "str"),
                    })
            generated = generate_driver(metadata, language, input_spec)
            if (generated or "").strip():
                # For Python/JavaScript, DB driver is often hand-tuned to the stored sample I/O contract.
                # Preserve hand-tuned drivers, but replace obviously generic stale templates.
                regenerated = (generated or "").strip()
                if (not existing_driver) or language not in ("python", "javascript"):
                    driver = regenerated
                elif language == "python" and _is_generic_python_driver(existing_driver):
                    driver = regenerated
        except Exception:
            pass
    if not driver:
        driver = ((problem or {}).get(driver_key) or "").strip()
    driver = (driver or "").strip()
    if not driver:
        return user_code
    # Align user code signature to metadata at run time so e.g. int[] -> int[][] for merge(); fixes compile errors.
    if metadata and language in ("java", "csharp"):
        try:
            aligned = align_solution_code_to_metadata(user_code, language, metadata)
            if (aligned or "").strip():
                user_code = aligned.strip()
        except Exception:
            pass
    # Go driver is a full file with ___USER_CODE___ placeholder (package main must be first).
    if language == "go" and "___USER_CODE___" in driver:
        return driver.replace("___USER_CODE___", user_code)
    if language == "java":
        return _merge_header_prefixed_source(user_code, driver, r"^import\s+.+;\s*$")
    if language == "csharp":
        return _merge_header_prefixed_source(user_code, driver, r"^using\s+.+;\s*$")
    return user_code + "\n\n" + driver


# ==================== AUTH ROUTES ====================
def _normalize_email(email: str) -> str:
    """Normalize email for lookup and storage (lowercase, strip)."""
    return (email or "").strip().lower()


def _validate_password_strength(password: str) -> None:
    """Basic password policy to prevent weak credentials."""
    pwd = (password or "").strip()
    if len(pwd) < 8 or len(pwd) > 128:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be 8-128 characters long.",
        )
    if not re.search(r"[A-Z]", pwd) or not re.search(r"[a-z]", pwd) or not re.search(r"\d", pwd):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must include uppercase, lowercase, and a number.",
        )


def _validate_user_profile_fields(username: str, full_name: Optional[str]) -> None:
    uname = (username or "").strip()
    if len(uname) < 3 or len(uname) > 30:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username must be 3-30 characters.",
        )
    if not re.fullmatch(r"[A-Za-z0-9_]+", uname):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Username can contain only letters, numbers, and underscore.",
        )
    if full_name is not None and len(full_name) > 80:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Full name cannot exceed 80 characters.",
        )


@api_router.post("/auth/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, database=Depends(get_db)):
    email_normalized = _normalize_email(user_data.email)
    if not email_normalized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email is required")
    _validate_user_profile_fields(user_data.username, user_data.full_name)
    _validate_password_strength(user_data.password)
    existing_user = await database.users.find_one({"email": email_normalized})
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
        email=email_normalized,
        username=user_data.username,
        full_name=user_data.full_name
    )
    user_in_db = UserInDB(**user.model_dump(), hashed_password=get_password_hash(user_data.password))

    user_dict = user_in_db.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    await database.users.insert_one(user_dict)
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.post("/auth/send-signup-otp")
async def send_signup_otp(body: SendSignupOtpRequest, database=Depends(get_db)):
    """Send a 6-digit OTP to the given email for signup verification."""
    email_normalized = _normalize_email(body.email)
    if not email_normalized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email is required")
    existing = await database.users.find_one({"email": email_normalized})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    otp = generate_otp()
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=get_otp_expire_minutes())
    await database.pending_signups.delete_many({"email": email_normalized})
    await database.pending_signups.insert_one({
        "email": email_normalized,
        "otp": otp,
        "expires_at": expires_at.isoformat(),
    })
    try:
        send_otp_email(email_normalized, otp)
    except RuntimeError as e:
        await database.pending_signups.delete_many({"email": email_normalized})
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Unable to send email. Try again later.")
    response = {"message": "OTP sent to your email"}
    if not smtp_configured():
        response["dev_otp"] = otp
    return response


@api_router.post("/auth/verify-signup-otp", response_model=Token, status_code=status.HTTP_201_CREATED)
async def verify_signup_otp(body: VerifySignupOtpRequest, database=Depends(get_db)):
    """Verify OTP and create the user; returns tokens."""
    email_normalized = _normalize_email(body.email)
    if not email_normalized:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Email is required")
    _validate_user_profile_fields(body.username, body.full_name)
    _validate_password_strength(body.password)
    pending = await database.pending_signups.find_one({"email": email_normalized})
    if not pending:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP. Please request a new code.",
        )
    expires_at = datetime.fromisoformat(pending["expires_at"])
    if datetime.now(timezone.utc) > expires_at:
        await database.pending_signups.delete_many({"email": email_normalized})
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="OTP expired. Please request a new code.",
        )
    if pending["otp"] != body.otp.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid OTP.",
        )
    existing_user = await database.users.find_one({"email": email_normalized})
    if existing_user:
        await database.pending_signups.delete_many({"email": email_normalized})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    existing_username = await database.users.find_one({"username": body.username})
    if existing_username:
        await database.pending_signups.delete_many({"email": email_normalized})
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
    user = User(
        email=email_normalized,
        username=body.username,
        full_name=body.full_name,
    )
    user_in_db = UserInDB(**user.model_dump(), hashed_password=get_password_hash(body.password))
    user_dict = user_in_db.model_dump()
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    await database.users.insert_one(user_dict)
    await database.pending_signups.delete_many({"email": email_normalized})
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    return Token(access_token=access_token, refresh_token=refresh_token)


# In-memory rate limit for login: IP -> list of timestamps (pruned to last window)
_login_attempts: dict = {}
_LOGIN_RATE_LIMIT_WINDOW = 60  # seconds
_LOGIN_RATE_LIMIT_MAX = 10


@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, database=Depends(get_db)):
    # Rate limit by IP
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    if client_ip not in _login_attempts:
        _login_attempts[client_ip] = []
    window_start = now - _LOGIN_RATE_LIMIT_WINDOW
    _login_attempts[client_ip] = [t for t in _login_attempts[client_ip] if t > window_start]
    if len(_login_attempts[client_ip]) >= _LOGIN_RATE_LIMIT_MAX:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Try again later.",
        )
    _login_attempts[client_ip].append(now)

    email_normalized = _normalize_email(credentials.email)
    if not email_normalized:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email is required",
        )

    # Match email case-insensitively (DB may have been seeded with different casing)
    email_regex = {"$regex": f"^{re.escape(email_normalized)}$", "$options": "i"}
    user = await database.users.find_one({"email": email_regex}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    user_in_db = UserInDB(**user)

    if not verify_password(credentials.password, user_in_db.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(data={"sub": user_in_db.id})
    refresh_token = create_refresh_token(data={"sub": user_in_db.id})
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.post("/auth/refresh", response_model=Token)
async def refresh_auth_token(body: RefreshTokenRequest, database=Depends(get_db)):
    """Exchange a valid refresh token for a new access+refresh token pair."""
    token = (body.refresh_token or "").strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="refresh_token is required",
        )
    user_id = get_user_id_from_refresh_token(token)
    user = await database.users.find_one({"id": user_id}, {"_id": 0})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    access_token = create_access_token(data={"sub": user_id})
    refresh_token = create_refresh_token(data={"sub": user_id})
    return Token(access_token=access_token, refresh_token=refresh_token)


@api_router.post("/auth/change-password")
async def change_password(
    body: ChangePasswordRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Change password for current user."""
    current_user = await get_current_user(credentials, database)
    current_password = (body.current_password or "").strip()
    new_password = (body.new_password or "").strip()
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect",
        )
    if current_password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be different from current password",
        )
    _validate_password_strength(new_password)
    hashed = get_password_hash(new_password)
    await database.users.update_one({"id": current_user.id}, {"$set": {"hashed_password": hashed}})
    return {"message": "Password updated successfully"}


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
    raw_email = idinfo.get("email")
    if not raw_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google account did not provide an email",
        )
    email = _normalize_email(raw_email)
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
    # LEARNING-FIRST: Only attach structured approaches (Brute Force → Better → Optimal). Never show a single optimized solution as the only content.
    solutions = get_solutions_for_problem(problem.get('title'))
    if solutions is not None:
        approaches = solutions.get('approaches') if isinstance(solutions, dict) else solutions
        problem['solutions'] = approaches
        if isinstance(solutions, dict):
            if solutions.get('prerequisites') is not None:
                problem['prerequisites'] = solutions['prerequisites']
            if solutions.get('common_pitfalls') is not None:
                problem['common_pitfalls'] = solutions['common_pitfalls']
            if solutions.get('youtube_video_id') is not None:
                problem['youtube_video_id'] = solutions['youtube_video_id']
            for key in ('pattern_recognition', 'dry_run', 'edge_cases', 'interview_tips', 'pitfalls'):
                if solutions.get(key) is not None:
                    problem[key] = solutions[key]
    else:
        # Do NOT use legacy problem.solution as the only approach—it often describes the optimal solution and breaks learning-first.
        problem['solutions'] = problem.get('solutions') or []
    
    # Hide input/expected_output for hidden test cases (user sees them only after submit)
    if problem.get("test_cases"):
        for tc in problem["test_cases"]:
            if tc.get("is_hidden"):
                tc["input"] = "Hidden"
                tc["expected_output"] = "Hidden"
    # Single source of truth: use function_metadata from DB, or from registry by title if not in DB
    meta = problem.get("function_metadata")
    meta_source = "db" if (meta and isinstance(meta, dict)) else None
    if not meta or not isinstance(meta, dict):
        try:
            from problem_metadata_registry import get_metadata
            entry = get_metadata(problem.get("title") or "")
            if entry is not None:
                metadata_obj, _ = entry
                problem["function_metadata"] = metadata_obj.model_dump()
                meta = problem["function_metadata"]
                meta_source = "registry"
        except Exception:
            pass
    if not meta or not isinstance(meta, dict):
        # Global fallback: infer metadata from available solution signatures so starters align
        # with solution tab code for unregistered problems as well.
        try:
            from seed_solutions import _infer_alignment_metadata
            inferred = _infer_alignment_metadata(problem.get("title") or "", problem.get("solutions") or [])
            if inferred is not None:
                problem["function_metadata"] = inferred.model_dump() if hasattr(inferred, "model_dump") else inferred
                meta = problem["function_metadata"]
                meta_source = "inferred"
        except Exception:
            pass
    if meta and isinstance(meta, dict) and meta_source == "inferred":
        meta["function_name"] = _prefer_problem_entrypoint_name(
            problem.get("title") or "",
            meta.get("function_name") or "",
        )
        params = meta.get("parameters")
        if isinstance(params, list) and params:
            first = params[0] if isinstance(params[0], dict) else None
            first_name = ((first or {}).get("name") or "").strip().lower()
            if first_name in {"self", "cls"}:
                meta["parameters"] = params[1:]
        # If inference ended up with no parameters (common for class-style python __init__),
        # recover argument shape from a typed language signature in solution snippets.
        if isinstance(problem.get("solutions"), list) and not meta.get("parameters"):
            code_keys = (
                ("code_java", "java"),
                ("code_cpp", "cpp"),
                ("code_go", "go"),
                ("code_csharp", "csharp"),
                ("code_javascript", "javascript"),
                ("code_python", "python"),
                ("code_typescript", "typescript"),
            )
            recovered_params = None
            recovered_return = None
            for code_key, lang in code_keys:
                if recovered_params:
                    break
                for approach in problem["solutions"]:
                    if not isinstance(approach, dict):
                        continue
                    sig = extract_signature((approach.get(code_key) or ""), lang)
                    if not sig:
                        continue
                    cleaned = []
                    for i, p in enumerate(sig.params):
                        pname = (p.name or f"arg{i + 1}").strip() or f"arg{i + 1}"
                        if pname.lower() in {"self", "cls"}:
                            continue
                        ptype = (p.type or "").strip() or "int"
                        cleaned.append({"name": pname, "type": ptype})
                    if cleaned:
                        recovered_params = cleaned
                        recovered_return = (sig.return_type or "").strip()
                        break
            if recovered_params:
                meta["parameters"] = recovered_params
                if recovered_return and (not meta.get("return_type")):
                    meta["return_type"] = recovered_return
        problem["function_metadata"] = meta
    if meta and isinstance(meta, dict):
        try:
            from models import ProblemFunctionMetadata
            from starter_template_generator import generate_starter
            metadata = ProblemFunctionMetadata(**meta)
            for lang in ("python", "javascript", "java", "cpp", "c", "go", "csharp", "typescript"):
                key = f"starter_code_{lang}"
                problem[key] = generate_starter(metadata, lang) or problem.get(key) or ""
            # Also align solution snippets to the same metadata contract by adding lightweight
            # adapter methods/wrappers when needed.
            if isinstance(problem.get("solutions"), list):
                for approach in problem["solutions"]:
                    if not isinstance(approach, dict):
                        continue
                    for code_key, lang in (
                        ("code_python", "python"),
                        ("code_javascript", "javascript"),
                        ("code_java", "java"),
                        ("code_cpp", "cpp"),
                        ("code_go", "go"),
                        ("code_csharp", "csharp"),
                        ("code_typescript", "typescript"),
                    ):
                        code = approach.get(code_key)
                        if code:
                            approach[code_key] = align_solution_code_to_metadata(code, lang, metadata)
                    if approach.get("code_python"):
                        approach["code"] = approach["code_python"]
        except Exception:
            pass
    else:
        _ensure_starter_function_name(problem)
    # Ensure every problem has a video link in the solution tab.
    if not (problem.get("youtube_video_id") or "").strip():
        problem["youtube_video_url"] = _youtube_search_url(problem.get("title") or "")
    else:
        problem["youtube_video_url"] = f"https://www.youtube.com/watch?v={problem.get('youtube_video_id')}"
    if isinstance(problem.get("solutions"), list):
        problem["solutions"] = _filter_solution_languages_by_contract(problem, problem["solutions"])
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
    if not problem_data.function_metadata:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "function_metadata is required to publish a problem. "
                "Use a single signature schema (function name, return type, and parameters)."
            ),
        )
    # Reject duplicate test cases within the problem (same input + expected_output)
    test_cases_list = [
        {"input": tc.input, "expected_output": tc.expected_output, "is_hidden": getattr(tc, "is_hidden", False)}
        for tc in problem_data.test_cases
    ]
    ok, dup_pairs = validate_no_duplicates_within_problem(test_cases_list)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate test cases are not allowed. Found duplicate pairs (indices): {dup_pairs}. Ensure every test case has unique input and expected output.",
        )
    # Reject duplicate inputs (same input with different outputs would be ambiguous for judge)
    ok_inputs, dup_input_pairs = validate_no_duplicate_inputs(test_cases_list)
    if not ok_inputs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Duplicate inputs are not allowed. Found test case pairs with same input (indices): {dup_input_pairs}. Each test case must have unique input.",
        )
    # Enforce minimum test case counts: at least 2 visible, at least 20 hidden
    ok_req, requirement_errors = validate_test_case_requirements(test_cases_list)
    if not ok_req:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Test case requirements not met. Each problem must have at least 2 visible example test cases and at least 20 hidden test cases.",
                "errors": requirement_errors,
            },
        )
    if all_visible_outputs_identical(test_cases_list):
        logging.warning(
            "Publish: problem has all visible test cases with identical expected output (overfitting risk): %s",
            getattr(problem_data, "title", "unknown"),
        )
    problem = Problem(
        **problem_data.model_dump(),
        created_by=current_user.id
    )
    problem_dict = problem.model_dump()
    # Signature schema is mandatory: generate starter/driver from metadata for all languages.
    generated = generate_starter_and_driver(
        problem_data.function_metadata,
        input_spec=[{"name": p.name, "type": p.type} for p in problem_data.function_metadata.parameters],
    )
    for k, v in generated.items():
        if v:
            problem_dict[k] = v

    # Publish gate 0: solution content integrity (no verbal-only; all 6 languages required per approach).
    if problem_data.solutions:
        solution_dict = {"approaches": [a.model_dump() if hasattr(a, "model_dump") else dict(a) for a in problem_data.solutions]}
        valid, integrity_errors = validate_solution_integrity(solution_dict)
        if not valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Solution validation failed. Every approach must have non-empty, compilable code for all 6 languages (Java, Python, C++, JavaScript, Go, C#). No placeholders (..., TODO) or verbal-only content.",
                    "errors": integrity_errors[:20],
                },
            )

    # Publish gate 1: enforce signature match between schema and provided solutions.
    if problem_data.solutions:
        for idx, approach in enumerate(problem_data.solutions):
            app = approach.model_dump() if hasattr(approach, "model_dump") else dict(approach)
            for lang in REQUIRED_SIGNATURE_LANGS:
                code_key = LANG_CODE_KEY[lang]
                code = (app.get(code_key) or "").strip()
                if not code:
                    continue
                expected_sig = metadata_signature(problem_data.function_metadata, lang)
                actual_sig = extract_signature(code, lang)
                if not expected_sig or not actual_sig or not signatures_match(expected_sig, actual_sig, strict_types=True):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Solution signature mismatch in approach {idx + 1} ('{app.get('title') or 'untitled'}'), "
                            f"language '{lang}'. Ensure solution code matches function_metadata exactly."
                        ),
                    )

    # Publish gate 2: compile + dry-run (single sample input) for each language that has solution code.
    if problem_data.solutions and problem_data.test_cases:
        sample_tc = problem_data.test_cases[0]
        first_code_by_lang: dict = {}
        for approach in problem_data.solutions:
            app = approach.model_dump() if hasattr(approach, "model_dump") else dict(approach)
            for lang in REQUIRED_SIGNATURE_LANGS:
                if lang in first_code_by_lang:
                    continue
                code = (app.get(LANG_CODE_KEY[lang]) or "").strip()
                if code:
                    first_code_by_lang[lang] = code
        for lang, sol_code in first_code_by_lang.items():
            driver = (generated.get(f"driver_code_{lang}") or "").strip()
            if not driver:
                continue
            full_code = driver.replace("___USER_CODE___", sol_code) if (lang == "go" and "___USER_CODE___" in driver) else (sol_code + "\n\n" + driver)
            try:
                dry = code_executor.execute_code(full_code, Language(lang), [sample_tc], visible_only=False)
                dry_status = dry.get("status")
                dry_val = dry_status.value if hasattr(dry_status, "value") else str(dry_status)
                if dry_val in {"compile_error", "runtime_error", "time_limit_exceeded", "memory_limit_exceeded"}:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=(
                            f"Publish validation failed for language '{lang}' on sample dry-run: {dry_val}. "
                            "Fix the solution or signature before publishing."
                        ),
                    )
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Publish validation failed for language '{lang}' during compile/dry-run: {e}",
                )
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
    _ensure_problem_execution_metadata(problem)
    meta = problem.get("function_metadata")
    if meta and isinstance(meta, dict):
        try:
            from models import ProblemFunctionMetadata
            metadata = ProblemFunctionMetadata(**meta)
            ok, err = validate_signature(body.code or "", body.language, metadata)
            if not ok and err:
                raise HTTPException(status_code=400, detail=err)
        except HTTPException:
            raise
        except Exception:
            pass
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
        execution_result = await run_in_threadpool(
            code_executor.execute_code,
            full_code,
            body.language,
            test_cases,
            False,  # visible_only=False (we already filtered; no hidden in list)
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
    current_user = await get_current_user(credentials, database)
    if len((body.code or "")) > MAX_CODE_LENGTH:
        raise HTTPException(status_code=400, detail=f"Code exceeds maximum length of {MAX_CODE_LENGTH} characters.")
    _rate_limit_check(current_user.id)
    try:
        import time
        start = time.time()
        output = await run_in_threadpool(
            code_executor._run_code,
            body.code,
            body.input or "",
            body.language,
        )
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
    _ensure_problem_execution_metadata(problem)
    meta = problem.get("function_metadata")
    if meta and isinstance(meta, dict):
        try:
            from models import ProblemFunctionMetadata
            metadata = ProblemFunctionMetadata(**meta)
            ok, err = validate_signature(submission_data.code or "", submission_data.language, metadata)
            if not ok and err:
                raise HTTPException(status_code=400, detail=err)
        except HTTPException:
            raise
        except Exception:
            pass
    problem_obj = Problem(**problem)
    full_code = build_full_code(problem, submission_data.code, submission_data.language.value)

    try:
        execution_result = await run_in_threadpool(
            code_executor.execute_code,
            full_code,
            submission_data.language,
            problem_obj.test_cases,
            False,
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
        response = await run_in_threadpool(
            ai_coach.get_progressive_hint,
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
        response = await run_in_threadpool(
            ai_coach.code_review,
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
        response = await run_in_threadpool(
            ai_coach.debug_help,
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
        response = await run_in_threadpool(
            ai_coach.explain_concept,
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
        result = await run_in_threadpool(
            ai_coach.get_recommendations,
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
        response = await run_in_threadpool(
            ai_coach.chat,
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


@api_router.post("/coach/mentor")
async def coach_mentor(
    body: CoachMentorRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """AI Coaching Agent: personalized DSA and interview prep (goals, diagnosis, plan, continuous coaching). No problem context."""
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    if looks_like_injection(body.message):
        raise HTTPException(status_code=400, detail="Invalid message.")
    try:
        response = await run_in_threadpool(ai_coach.coaching_agent_chat, body.message)
    except Exception as e:
        logger.exception("Coach mentor failed: %s", e)
        raise HTTPException(status_code=503, detail="AI Coach is temporarily unavailable.")
    await _log_ai_feedback(database, current_user.id, "", "mentor", response)
    return {"text": response}


# ==================== COACH (health + sessions) ====================
@api_router.get("/coach/health")
async def coach_health():
    """No auth. Returns 200 if coach API is reachable. Use this to verify backend URL."""
    return {"status": "ok", "coach": True}


@api_router.post("/coach/generate-plan")
async def coach_generate_plan(
    body: CoachGeneratePlanRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """
    Generate a structured preparation plan and map each day to real problems.
    If an active plan exists, returns 409 unless replaceExisting=true.
    """
    current_user = await get_current_user(credentials, database)
    _coach_rate_limit_check(current_user.id)
    try:
        result = await generate_preparation_plan(
            database=database,
            user_id=current_user.id,
            duration_days=body.duration_days,
            daily_hours=body.daily_hours,
            target_company=body.target_company,
            difficulty_preference=body.difficulty_preference,
            user_weak_topics=body.user_weak_topics,
            replace_existing=body.replace_existing,
        )
        return result
    except ActivePlanExistsError as e:
        existing = e.existing_plan or {}
        raise HTTPException(
            status_code=409,
            detail={
                "message": "Active preparation plan already exists. Set replaceExisting=true to regenerate.",
                "existingPlan": {
                    "planId": existing.get("id"),
                    "targetCompany": existing.get("target_company"),
                    "durationDays": existing.get("duration_days"),
                    "createdAt": existing.get("created_at"),
                },
            },
        )
    except PlanGenerationError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Generate preparation plan failed: %s", e)
        raise HTTPException(status_code=503, detail="Failed to generate preparation plan.")


@api_router.get("/coach/my-plan")
async def coach_get_my_plan(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Get current user's active preparation plan with day/problem completion details."""
    current_user = await get_current_user(credentials, database)
    plan = await get_active_preparation_plan(database, current_user.id)
    if not plan:
        return {"plan": None}
    return {"plan": plan}


@api_router.get("/coach/my-plan/assigned-map")
async def coach_get_my_plan_assigned_map(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Return quick lookup: problem_id -> {day, focusTopic, status} for active plan."""
    current_user = await get_current_user(credentials, database)
    mapping = await get_active_plan_assigned_problem_map(database, current_user.id)
    return {"assigned": mapping}


@api_router.patch("/coach/my-plan/problems/{plan_problem_id}")
async def coach_update_my_plan_problem_status(
    plan_problem_id: str,
    body: CoachUpdatePlanProblemStatusRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Update status for one assigned plan problem."""
    current_user = await get_current_user(credentials, database)
    try:
        updated = await update_plan_problem_status(
            database=database,
            user_id=current_user.id,
            plan_problem_id=plan_problem_id,
            status=body.status.value,
        )
        return {"plan": updated}
    except PlanGenerationError as e:
        msg = str(e)
        status_code = 404 if "not found" in msg.lower() else 400
        raise HTTPException(status_code=status_code, detail=msg)
    except Exception as e:
        logger.exception("Update plan problem status failed: %s", e)
        raise HTTPException(status_code=503, detail="Failed to update plan progress.")


@api_router.delete("/coach/my-plan")
async def coach_delete_my_plan(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Delete active preparation plan and cascade to day/problem assignments."""
    current_user = await get_current_user(credentials, database)
    ok = await delete_active_preparation_plan(database, current_user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="No active preparation plan found.")
    return {"ok": True}


# List route uses /coach/session-list to avoid matching /coach/sessions/{session_id} when path is /coach/sessions
@api_router.get("/coach/session-list")
async def coach_list_sessions(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """List current user's coach sessions, newest first."""
    current_user = await get_current_user(credentials, database)
    cursor = database.coach_sessions.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1, "title": 1, "problem_id": 1, "created_at": 1, "updated_at": 1},
    ).sort("updated_at", -1).limit(100)
    sessions = []
    async for doc in cursor:
        sessions.append({
            "id": doc["id"],
            "title": doc.get("title") or "New chat",
            "problem_id": doc.get("problem_id"),
            "created_at": doc.get("created_at"),
            "updated_at": doc.get("updated_at"),
        })
    return {"sessions": sessions}


@api_router.post("/coach/sessions")
async def coach_create_session(
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Create a new coach chat session."""
    current_user = await get_current_user(credentials, database)
    session_id = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    session_doc = {
        "id": session_id,
        "user_id": current_user.id,
        "problem_id": None,
        "title": "New chat",
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
    }
    await database.coach_sessions.insert_one(session_doc)
    return {"id": session_id, "title": "New chat", "created_at": session_doc["created_at"]}


@api_router.get("/coach/sessions/{session_id}")
async def coach_get_session(
    session_id: str,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Get a session and its messages."""
    current_user = await get_current_user(credentials, database)
    session = await database.coach_sessions.find_one({"id": session_id, "user_id": current_user.id}, {"_id": 0})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    cursor = database.coach_messages.find(
        {"session_id": session_id},
        {"_id": 0, "id": 1, "role": 1, "content": 1, "created_at": 1},
    ).sort("created_at", 1)
    messages = []
    async for doc in cursor:
        messages.append({
            "id": doc["id"],
            "role": doc["role"],
            "content": doc["content"],
            "created_at": doc.get("created_at"),
        })
    return {"session": session, "messages": messages}


@api_router.delete("/coach/sessions/{session_id}")
async def coach_delete_session(
    session_id: str,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Delete a coach session and its messages."""
    current_user = await get_current_user(credentials, database)
    result = await database.coach_sessions.delete_one({"id": session_id, "user_id": current_user.id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    await database.coach_messages.delete_many({"session_id": session_id})
    return {"ok": True}


COACH_MESSAGE_MAX_LENGTH = 8000
COACH_CHAT_TIMEOUT_SEC = 45
COACH_HISTORY_MAX_MESSAGES = 14


@api_router.post("/coach/chat/session")
async def coach_chat_session(
    body: CoachChatUnifiedRequest,
    database=Depends(get_db),
    credentials=Depends(security),
):
    """Unified coach chat: with or without problem context. Creates or uses a session. Returns structured response."""
    try:
        current_user = await get_current_user(credentials, database)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Coach chat auth failed: %s", e)
        raise HTTPException(status_code=401, detail="Authentication required.")

    try:
        _coach_rate_limit_check(current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        logger.warning("Coach rate limit check failed: %s", e)

    msg = (body.message or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    if len(msg) > COACH_MESSAGE_MAX_LENGTH:
        raise HTTPException(status_code=400, detail=f"Message too long (max {COACH_MESSAGE_MAX_LENGTH} characters).")
    if looks_like_injection(body.message):
        raise HTTPException(status_code=400, detail="Invalid message.")

    now = datetime.now(timezone.utc).isoformat()
    session_id = body.session_id
    problem_context = body.problem_context

    try:
        if body.problem_id and not problem_context:
            problem = await _get_problem_for_chat(database, body.problem_id)
            if problem:
                problem_context = {
                    "title": problem.get("title") or "",
                    "description": problem.get("description") or "",
                    "examples_text": problem.get("examples_text") or "",
                    "difficulty": problem.get("difficulty") or "medium",
                    "tags": problem.get("tags") or [],
                }
    except Exception as e:
        logger.warning("Coach get problem for chat failed: %s", e)
        problem_context = problem_context or None

    if not session_id:
        session_id = str(uuid.uuid4())
        title = (msg[:50] + "…") if len(msg) > 50 else msg
        try:
            await database.coach_sessions.insert_one({
                "id": session_id,
                "user_id": current_user.id,
                "problem_id": body.problem_id,
                "title": title or "New chat",
                "created_at": now,
                "updated_at": now,
            })
        except Exception as e:
            logger.exception("Coach session create failed: %s", e)
            raise HTTPException(status_code=503, detail="Failed to create chat session.")

    session = await database.coach_sessions.find_one({"id": session_id, "user_id": current_user.id})
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        user_msg_id = str(uuid.uuid4())
        await database.coach_messages.insert_one({
            "id": user_msg_id,
            "session_id": session_id,
            "role": "user",
            "content": msg,
            "created_at": now,
        })
        await database.coach_sessions.update_one(
            {"id": session_id},
            {"$set": {"updated_at": now, "title": (msg[:50] + "…") if len(msg) > 50 else msg}},
        )
    except Exception as e:
        logger.exception("Coach message insert failed: %s", e)
        raise HTTPException(status_code=503, detail="Failed to save message.")

    chat_history = []
    try:
        history_cursor = database.coach_messages.find(
            {"session_id": session_id},
            {"_id": 0, "role": 1, "content": 1},
        ).sort("created_at", -1).limit(COACH_HISTORY_MAX_MESSAGES)
        history_docs = await history_cursor.to_list(length=COACH_HISTORY_MAX_MESSAGES)
        for doc in reversed(history_docs):
            role = str(doc.get("role") or "").strip().lower()
            content = str(doc.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                chat_history.append({"role": role, "content": content})
    except Exception as e:
        logger.warning("Coach history fetch failed for session %s: %s", session_id, e)

    reply = None
    action = None
    generated_plan_id = None

    # If user asks for a prep plan, generate and assign it directly (non-text-only flow).
    plan_request = parse_plan_request_from_message(msg)
    if plan_request:
        try:
            plan_result = await generate_preparation_plan(
                database=database,
                user_id=current_user.id,
                duration_days=plan_request.get("duration_days", DEFAULT_DURATION_DAYS),
                daily_hours=plan_request.get("daily_hours", DEFAULT_DAILY_HOURS),
                target_company=plan_request.get("target_company", "Generic"),
                difficulty_preference=plan_request.get("difficulty_preference", "balanced"),
                user_weak_topics=plan_request.get("user_weak_topics"),
                replace_existing=bool(plan_request.get("replace_existing", False)),
            )
            generated_plan_id = plan_result.get("planId")
            duration_days = plan_result.get("durationDays")
            target_company = plan_result.get("targetCompany", "Generic")
            reply = (
                f"I've created your {duration_days}-day {target_company} preparation plan. "
                "You can view it in My Plan."
            )
            action = {"type": "prep_plan_created", "plan_id": generated_plan_id, "redirect_to": "/my-plan"}
        except ActivePlanExistsError as e:
            existing = e.existing_plan or {}
            existing_target = existing.get("target_company") or "current"
            existing_days = existing.get("duration_days") or "active"
            reply = (
                f"You already have an active {existing_days}-day {existing_target} plan. "
                "Say 'replace my current plan' to regenerate it."
            )
            action = {"type": "prep_plan_exists", "plan_id": existing.get("id"), "redirect_to": "/my-plan"}
        except PlanGenerationError as e:
            reply = f"I couldn't generate a preparation plan: {str(e)}"
        except Exception as e:
            logger.exception("Coach prep plan generation in chat failed: %s", e)
            reply = "I couldn't generate your preparation plan right now. Please try again in a moment."

    if reply is None:
        try:
            import asyncio
            reply = await asyncio.wait_for(
                asyncio.to_thread(
                    ai_coach.chat_unified,
                    user_message=msg,
                    problem_context=problem_context,
                    user_code=body.user_code,
                    language=body.language,
                    chat_history=chat_history,
                ),
                timeout=COACH_CHAT_TIMEOUT_SEC,
            )
        except asyncio.TimeoutError:
            logger.warning("Coach chat timed out after %ss", COACH_CHAT_TIMEOUT_SEC)
            reply = "The request took too long. Please try again with a shorter message or try again later."
        except Exception as e:
            logger.exception("Coach chat session LLM failed: %s", e)
            reply = "The AI coach is temporarily unavailable. Please try again in a moment."

    if reply is None or not isinstance(reply, str):
        reply = "I couldn't generate a response. Please try again."

    reply = reply.strip() or "I couldn't generate a response. Please try again."

    try:
        asst_msg_id = str(uuid.uuid4())
        await database.coach_messages.insert_one({
            "id": asst_msg_id,
            "session_id": session_id,
            "role": "assistant",
            "content": reply,
            "created_at": now,
        })
    except Exception as e:
        logger.exception("Coach assistant message insert failed: %s", e)
        # Still return reply; message may be lost but user gets response

    response = {
        "success": True,
        "reply": reply,
        "session_id": session_id,
    }
    if action:
        response["action"] = action
    if generated_plan_id:
        response["plan_id"] = generated_plan_id
    return response


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
        response = await run_in_threadpool(
            ai_coach.full_solution,
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


def _default_demo_admin_users():
    """Default admin and demo user definitions (lowercase email for consistent lookup)."""
    return [
        UserInDB(
            email="admin@ifelse.com",
            username="admin",
            full_name="Admin User",
            role=UserRole.ADMIN,
            hashed_password=get_password_hash("admin123"),
        ),
        UserInDB(
            email="demo@ifelse.com",
            username="demo",
            full_name="Demo User",
            hashed_password=get_password_hash("demo123"),
        ),
    ]


async def _ensure_default_users():
    """Ensure demo and admin users exist so login works (creates only if missing by email)."""
    try:
        for u in _default_demo_admin_users():
            # Case-insensitive: existing DB might have Demo@ifelse.com etc.
            existing = await db.users.find_one(
                {"email": {"$regex": f"^{re.escape(u.email)}$", "$options": "i"}}
            )
            if existing:
                continue
            user_dict = u.model_dump()
            user_dict["created_at"] = user_dict["created_at"].isoformat()
            await db.users.insert_one(user_dict)
            logger.info("Created default user: %s", u.email)
    except Exception as e:
        logger.warning("Could not ensure default users: %s", e)


@app.on_event("startup")
async def startup_validate():
    """Validate env, create indexes, ping DB, and confirm containerized runners."""
    # Log coach routes so operators can verify they are registered
    coach_routes = [r for r in app.routes if hasattr(r, "path") and "/coach" in r.path]
    for r in coach_routes:
        methods = getattr(r, "methods", set()) or set()
        logger.info("Coach route: %s %s", list(methods)[0] if methods else "GET", r.path)
    _get_required_env("MONGO_URL")
    _get_required_env("DB_NAME")
    try:
        await db.command("ping")
    except Exception as e:
        logger.warning("MongoDB ping on startup: %s", e)
    await _ensure_default_users()
    try:
        await db.problems.create_index("id", unique=True)
        await db.problems.create_index("difficulty")
        await db.problems.create_index("tags")
        await db.users.create_index("email", unique=True)
        await db.submissions.create_index([("user_id", 1), ("problem_id", 1)])
        await db.submissions.create_index("created_at")
        await db.ai_feedback_history.create_index([("user_id", 1), ("created_at", -1)])
        await db.user_weakness_metrics.create_index("user_id", unique=True)
        await db.user_preparation_plans.create_index([("user_id", 1), ("is_active", 1)])
        await db.user_preparation_plans.create_index([("user_id", 1), ("updated_at", -1)])
        await db.user_plan_days.create_index([("plan_id", 1), ("day_number", 1)], unique=True)
        await db.user_plan_problems.create_index([("plan_day_id", 1), ("assigned_order", 1)])
        await db.user_plan_problems.create_index([("plan_day_id", 1), ("problem_id", 1)], unique=True)
        logger.info("Database indexes ensured.")
    except Exception as e:
        logger.warning("Index creation (may already exist): %s", e)
    # Self-validate Java runner (confirmation that containerized execution works)
    try:
        import asyncio
        from models import Language
        hello_java = 'public class Main { public static void main(String[] args) { System.out.println("Hello from Java"); } }'
        out, err, code = await asyncio.to_thread(run_in_docker, hello_java, "", Language.JAVA, 5)
        if code == 0 and "Hello from Java" in (out or ""):
            logger.info("Java runner self-check: OK (containerized execution ready)")
        else:
            logger.warning("Java runner self-check: unexpected output code=%s out=%r stderr=%r", code, out, err)
    except Exception as e:
        logger.warning("Java runner self-check failed (build runner images with: docker-compose build): %s", e)


# With allow_credentials=True, browsers reject allow_origins=['*']. Default to dev origins.
_cors_origins_raw = os.environ.get("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000")
_cors_origins = [o.strip() for o in _cors_origins_raw.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=_cors_origins,
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
