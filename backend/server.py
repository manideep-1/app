from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime, timezone

from models import (
    User, UserCreate, UserLogin, UserInDB, Token,
    Problem, ProblemCreate, Submission, SubmissionCreate,
    UserProgress, Difficulty, SubmissionStatus, Language, TestCase
)
from auth import (
    get_password_hash, verify_password, create_access_token,
    create_refresh_token, get_current_user, get_current_admin_user, security
)
from code_executor import CodeExecutor

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app
app = FastAPI(title="ifelse API", version="1.0.0")

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Initialize code executor
code_executor = CodeExecutor()


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


@api_router.get("/auth/me", response_model=User)
async def get_current_user_info(database=Depends(get_db), credentials=Depends(security)):
    current_user = await get_current_user(credentials, database)
    return User(**current_user.model_dump())


# ==================== PROBLEMS ROUTES ====================
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
    
    # Convert datetime strings back
    for problem in problems:
        if isinstance(problem.get('created_at'), str):
            problem['created_at'] = datetime.fromisoformat(problem['created_at'])
    
    return problems


@api_router.get("/problems/{problem_id}", response_model=Problem)
async def get_problem(problem_id: str, database=Depends(get_db)):
    problem = await database.problems.find_one({"id": problem_id}, {"_id": 0})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    if isinstance(problem.get('created_at'), str):
        problem['created_at'] = datetime.fromisoformat(problem['created_at'])
    
    return Problem(**problem)


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


# ==================== SUBMISSIONS ROUTES ====================
@api_router.post("/submissions", response_model=Submission, status_code=status.HTTP_201_CREATED)
async def submit_code(
    submission_data: SubmissionCreate,
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_user(credentials, database)
    
    # Get problem
    problem = await database.problems.find_one({"id": submission_data.problem_id}, {"_id": 0})
    if not problem:
        raise HTTPException(status_code=404, detail="Problem not found")
    
    problem_obj = Problem(**problem)
    
    # Execute code
    execution_result = code_executor.execute_code(
        submission_data.code,
        submission_data.language,
        problem_obj.test_cases
    )
    
    # Create submission
    submission = Submission(
        user_id=current_user.id,
        problem_id=submission_data.problem_id,
        code=submission_data.code,
        language=submission_data.language,
        status=execution_result["status"],
        result={
            "passed": execution_result["passed"],
            "total": execution_result["total"],
            "test_results": execution_result["test_results"]
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
    database=Depends(get_db),
    credentials=Depends(security)
):
    current_user = await get_current_user(credentials, database)
    
    query = {"user_id": current_user.id}
    if problem_id:
        query["problem_id"] = problem_id
    
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


# ==================== USER PROGRESS ROUTES ====================
@api_router.get("/user/progress", response_model=UserProgress)
async def get_user_progress(database=Depends(get_db), credentials=Depends(security)):
    current_user = await get_current_user(credentials, database)
    
    # Get solved problems by difficulty
    solved_problems = current_user.solved_problems
    
    easy_count = 0
    medium_count = 0
    hard_count = 0
    
    for problem_id in solved_problems:
        problem = await database.problems.find_one({"id": problem_id}, {"_id": 0, "difficulty": 1})
        if problem:
            if problem["difficulty"] == Difficulty.EASY:
                easy_count += 1
            elif problem["difficulty"] == Difficulty.MEDIUM:
                medium_count += 1
            elif problem["difficulty"] == Difficulty.HARD:
                hard_count += 1
    
    # Get recent submissions
    recent_submissions = await database.submissions.find(
        {"user_id": current_user.id},
        {"_id": 0, "id": 1}
    ).sort("created_at", -1).limit(10).to_list(10)
    
    return UserProgress(
        easy_solved=easy_count,
        medium_solved=medium_count,
        hard_solved=hard_count,
        total_solved=len(solved_problems),
        total_submissions=current_user.total_submissions,
        recent_submissions=[s["id"] for s in recent_submissions]
    )


# ==================== HEALTH CHECK ====================
@api_router.get("/health")
async def health_check():
    return {"status": "healthy", "service": "ifelse API"}


# Include the router in the main app
app.include_router(api_router)

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
logger = logging.getLogger(__name__)


@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()
