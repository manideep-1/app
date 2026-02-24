# ifelse - Coding Interview Platform 🚀

A production-ready coding interview practice platform built with **React** + **FastAPI** + **MongoDB**, featuring real-time code execution, progress tracking, and a vibrant UI.

## 🎯 Phase 1 - Core MVP Features (COMPLETED)

### ✅ Implemented Features

#### 🔐 Authentication System
- JWT-based authentication with access & refresh tokens
- User registration and login
- Protected routes with role-based access (user, premium, admin)
- Password hashing with bcrypt

#### 📝 Problem Management
- 5+ curated coding problems (Easy, Medium, Hard)
- Detailed problem descriptions with examples
- Test cases (visible and hidden)
- Tags and company associations
- Difficulty-based filtering

#### 💻 Code Execution Engine
- Real-time code execution for Python & JavaScript
- Secure subprocess-based sandbox
- 5-second timeout protection
- Test case validation
- Detailed execution results with runtime metrics

#### 📊 User Progress Tracking
- Total problems solved
- Difficulty-wise breakdown
- Submission history
- Acceptance rates
- Dashboard with visual stats

#### 🎨 Modern UI/UX
- **Electric Obsidian** design theme
- Dark mode with vibrant neon accents (Indigo, Pink, Cyan)
- Custom fonts: Outfit (headings), Plus Jakarta Sans (body), JetBrains Mono (code)
- Monaco code editor integration
- Responsive design for all screen sizes

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React 19, Tailwind CSS, Monaco Editor, Shadcn UI
- **Backend**: FastAPI, Python 3.11
- **Database**: MongoDB with Motor (async)
- **Authentication**: JWT + passlib + bcrypt
- **Code Execution**: Subprocess-based Python/JavaScript runner

### Project Structure

```
/app
├── backend/
│   ├── server.py              # Main FastAPI application
│   ├── models.py              # Pydantic models
│   ├── auth.py                # Authentication logic
│   ├── code_executor.py       # Code execution engine
│   ├── seed_db.py             # Database seeding script
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LandingPage.js
│   │   │   ├── LoginPage.js
│   │   │   ├── RegisterPage.js
│   │   │   ├── ProblemsPage.js
│   │   │   ├── ProblemSolvePage.js
│   │   │   └── DashboardPage.js
│   │   ├── context/
│   │   │   └── AuthContext.js
│   │   ├── utils/
│   │   │   ├── api.js
│   │   │   └── constants.js
│   │   ├── components/ui/      # Shadcn UI components
│   │   ├── App.js
│   │   ├── App.css
│   │   └── index.css
│   ├── package.json
│   └── tailwind.config.js
└── design_guidelines.json
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.11+
- Node.js 18+ & Yarn (or npm)
- MongoDB running locally (or use Docker Compose)

### Option A: Run with Docker Compose (recommended for clean install)

From the project root (`/app` or `learning/app`):

```bash
docker-compose up -d mongodb    # Start MongoDB
# Wait for MongoDB to be healthy, then:
cd backend
cp .env.example .env            # Edit .env: set MONGO_URL=mongodb://localhost:27017, DB_NAME=ifelse_db
pip install -r requirements.txt
python seed_db.py               # One-time: seed problems and admin/demo users
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

In another terminal (frontend):

```bash
cd frontend
yarn install   # or npm install
yarn start     # or npm start
```

Backend: http://localhost:8000  
Frontend: http://localhost:3000  
API docs: http://localhost:8000/docs

### Option B: Full stack with Docker Compose (backend + MongoDB)

```bash
docker-compose up -d
# Seed DB once (run from host with backend deps, or exec into backend container):
# docker-compose exec backend python seed_db.py
```

Then run frontend locally (see above).

### Option C: Local install (no Docker)

1. **Backend**
```bash
cd backend
pip install -r requirements.txt
# Create .env with MONGO_URL, DB_NAME, JWT_SECRET (see .env.example)
python seed_db.py  # One-time: seed database
uvicorn server:app --reload --port 8000
```

2. **Frontend**
```bash
cd frontend
yarn install
yarn start
```

3. **Environment Variables**

Backend (`.env` in `backend/`). **Required**: `MONGO_URL`, `DB_NAME`. Optional: `JWT_SECRET`, `CORS_ORIGINS`, `GOOGLE_CLIENT_ID`, SMTP vars for email OTP.
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=ifelse_db
JWT_SECRET=your-super-secret-jwt-key-change-in-production
CORS_ORIGINS=*
```

Frontend (`.env` in `frontend/`). For local dev, frontend uses `http://localhost:8000` when hostname is localhost.
```env
REACT_APP_BACKEND_URL=http://localhost:8000
```

**Note:** The backend fails fast at startup if `MONGO_URL` or `DB_NAME` are missing.

---

## 📖 API Documentation

### Authentication Endpoints

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "coder123",
  "password": "securepass",
  "full_name": "John Doe"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass"
}
```

### Problem Endpoints

#### Get All Problems
```http
GET /api/problems?difficulty=easy
```

### Submission Endpoints

#### Submit Code
```http
POST /api/submissions
Authorization: Bearer <token>
Content-Type: application/json

{
  "problem_id": "uuid",
  "code": "def twoSum(nums, target): ...",
  "language": "python"
}
```

---

## 👥 Test Accounts

```
Admin Account:
Email: admin@ifelse.com
Password: admin123

Demo Account:
Email: demo@ifelse.com
Password: demo123
```

---

## 🔮 Phase 2 - Advanced Features (Planned)

### 🤖 AI Integration (OpenAI GPT-5.2)
- AI-powered hint engine
- Code review suggestions
- Structured JSON output
- Context-limited prompts

### 💳 Payment Integration (Razorpay)
- Premium subscription tiers
- Payment history
- Webhook handling

### 🔐 Enhanced Authentication
- Google OAuth integration
- Email verification
- Password reset flow

---

**Built with ❤️ for the coding community**
