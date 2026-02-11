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
- Node.js 18+ & Yarn
- MongoDB running locally

### Installation

1. **Backend Setup**
```bash
cd /app/backend
pip install -r requirements.txt
python seed_db.py  # Seed database with sample problems
```

2. **Frontend Setup**
```bash
cd /app/frontend
yarn install
```

3. **Environment Variables**

Backend (`.env`):
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=ifelse_db
JWT_SECRET=your-super-secret-jwt-key
CORS_ORIGINS=*
```

Frontend (`.env`):
```env
REACT_APP_BACKEND_URL=https://your-backend-url.com
```

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
