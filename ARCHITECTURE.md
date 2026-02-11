# ifelse Platform - System Architecture

## Overview
This document outlines the production-grade architecture for the ifelse coding interview platform, designed to scale to 100,000+ active users.

---

## 1. System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                │
│                                                                     │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐       │
│   │  Web Browser │    │ Mobile App   │    │   CLI Tool   │       │
│   │  (React)     │    │ (Planned)    │    │  (Planned)   │       │
│   └──────────────┘    └──────────────┘    └──────────────┘       │
│           │                   │                   │                │
└───────────┼───────────────────┼───────────────────┼────────────────┘
            │                   │                   │
            └───────────────────┴───────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    API GATEWAY / LOAD BALANCER                      │
│                     (Nginx/Kubernetes Ingress)                      │
│                    - Rate Limiting                                  │
│                    - SSL Termination                                │
│                    - Request Routing                                │
└─────────────────────────────────────────────────────────────────────┘
                                │
                ┌───────────────┴───────────────┐
                ▼                               ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│   BACKEND API SERVICE    │      │  CODE EXECUTION SERVICE  │
│     (FastAPI)            │      │   (Microservice)         │
│                          │      │                          │
│  - Auth & JWT            │      │  - Docker Containers     │
│  - Problems API          │      │  - Language Runtime      │
│  - Submissions API       │      │  - Timeout Enforcement   │
│  - User Progress         │      │  - Resource Limits       │
│  - Admin APIs            │      │  - Queue Processing      │
└──────────────────────────┘      └──────────────────────────┘
        │                                     │
        │                                     │
        ▼                                     ▼
┌──────────────────────────┐      ┌──────────────────────────┐
│    REDIS CACHE/QUEUE     │      │      MONGODB CLUSTER     │
│                          │      │                          │
│  - Session Storage       │      │  Collections:            │
│  - Rate Limit Tracking   │      │  - users                 │
│  - BullMQ Job Queue      │      │  - problems              │
│  - Submission Queue      │      │  - submissions           │
└──────────────────────────┘      │  - payments              │
                                  │  - ai_usage              │
                                  └──────────────────────────┘
                                              │
                                              ▼
                                  ┌──────────────────────────┐
                                  │   BACKUP STORAGE (S3)    │
                                  │  - Database Backups      │
                                  │  - Logs Archive          │
                                  └──────────────────────────┘
```

---

## 2. Component Details

### 2.1 Frontend (React)
**Technology:** React 19, Tailwind CSS, Monaco Editor
**Responsibilities:**
- User interface rendering
- Client-side routing
- State management (Context API)
- API communication
- Code editor integration

**Scaling Strategy:**
- CDN for static assets
- Code splitting
- Lazy loading
- Service worker caching

### 2.2 Backend API (FastAPI)
**Technology:** FastAPI, Python 3.11, Motor (async MongoDB)
**Responsibilities:**
- REST API endpoints
- Authentication & authorization
- Business logic
- Database operations
- Request validation

**Scaling Strategy:**
- Horizontal scaling (K8s pods)
- Stateless design
- Database connection pooling
- Async I/O operations

### 2.3 Code Execution Service
**Current:** Subprocess-based execution
**Production:** Docker-based isolation

**Features:**
- Language runtime isolation
- Resource limits (CPU, memory)
- Timeout enforcement (5s)
- Test case validation
- Output capture

**Scaling Strategy:**
- Worker pool architecture
- Queue-based job distribution
- Auto-scaling based on queue depth
- Separate containers per language

### 2.4 Database Layer (MongoDB)
**Collections:**
- users: User profiles and auth
- problems: Coding problems
- submissions: Code submissions
- payments: Transaction history (Phase 2)
- ai_usage: AI hint tracking (Phase 2)

**Indexes:**
- users: email (unique), username (unique)
- problems: difficulty, tags, companies
- submissions: user_id, problem_id, created_at

**Scaling Strategy:**
- Replica set for read scaling
- Sharding by user_id for write scaling
- Read preference: secondary for queries
- Write concern: majority for consistency

### 2.5 Cache & Queue (Redis)
**Use Cases:**
- Session storage
- Rate limiting
- API response caching
- Job queue (BullMQ)
- Leaderboard caching

**Scaling Strategy:**
- Redis Cluster mode
- Sentinel for high availability
- Separate instances for cache vs queue

---

## 3. Data Flow

### 3.1 User Authentication Flow
```
1. User → POST /api/auth/login → Backend
2. Backend → Verify credentials → MongoDB
3. Backend → Generate JWT tokens → Response
4. Client → Store tokens → LocalStorage
5. Client → Include token in headers → All requests
6. Backend → Verify token → Decode user_id
7. Backend → Fetch user data → MongoDB
```

### 3.2 Code Submission Flow
```
1. User → Write code → Monaco Editor
2. User → Click "Run" → POST /api/submissions
3. Backend → Validate request → Auth middleware
4. Backend → Fetch problem & test cases → MongoDB
5. Backend → Queue job → Redis/BullMQ
6. Code Executor → Pick job → Execute code
7. Code Executor → Run test cases → Collect results
8. Code Executor → Store results → MongoDB
9. Backend → Return results → Client
10. Client → Display results → UI
```

### 3.3 AI Hint Request Flow (Phase 2)
```
1. User → Click "Get Hint" → POST /api/hints
2. Backend → Check AI usage limits → MongoDB
3. Backend → Build context prompt → Problem description
4. Backend → Call OpenAI API → GPT-5.2
5. OpenAI → Generate hint → JSON response
6. Backend → Parse & validate → Store in DB
7. Backend → Increment usage count → MongoDB
8. Backend → Return hint → Client
```

---

## 4. Security Architecture

### 4.1 Authentication & Authorization
- JWT tokens with expiry (30min access, 7d refresh)
- Refresh token rotation
- Role-based access control (user, premium, admin)
- Password hashing (bcrypt, 12 rounds)

### 4.2 Code Execution Security
- Subprocess isolation (current)
- Docker container isolation (production)
- Resource limits (CPU, memory, disk)
- Network isolation (no outbound connections)
- Timeout enforcement

### 4.3 API Security
- Rate limiting (100 req/min per user)
- CORS configuration
- Input validation (Pydantic)
- SQL injection prevention (MongoDB parameterized queries)
- XSS protection (React auto-escaping)

### 4.4 Data Security
- Environment variable secrets
- MongoDB encryption at rest
- SSL/TLS for data in transit
- Regular security audits
- Backup encryption

---

## 5. Monitoring & Observability

### 5.1 Logging Strategy
**Tool:** Winston (Backend), Browser console (Frontend)
**Levels:** ERROR, WARN, INFO, DEBUG
**Storage:** ELK Stack (Elasticsearch, Logstash, Kibana)

**Log Types:**
- API requests/responses
- Authentication events
- Code execution results
- Error stack traces
- Performance metrics

### 5.2 Metrics Collection
**Tool:** Prometheus + Grafana

**Key Metrics:**
- Request rate (req/s)
- Response latency (p50, p95, p99)
- Error rate (%)
- Active users (concurrent)
- Code execution time (avg, max)
- Database query time
- Cache hit rate

### 5.3 Alerting
**Tool:** Alertmanager

**Alert Conditions:**
- Error rate > 5%
- Response time > 2s (p95)
- Database connection pool exhausted
- Code execution queue > 1000
- Disk usage > 80%
- Memory usage > 85%

---

## 6. Scalability Strategy

### 6.1 Horizontal Scaling
**Components:**
- Backend API: 3-10 pods (auto-scaling)
- Code Executor: 5-20 workers (auto-scaling)
- MongoDB: 3-node replica set (manual scaling)
- Redis: 3-node cluster (manual scaling)

**Auto-scaling Rules:**
- CPU > 70% → Scale up
- CPU < 30% → Scale down
- Queue depth > 500 → Scale up executors

### 6.2 Performance Optimization
- Database indexing on hot paths
- API response caching (Redis)
- CDN for static assets
- Code splitting & lazy loading
- Connection pooling (DB, Redis)
- Async I/O operations

### 6.3 Load Testing
**Tool:** K6, Locust

**Test Scenarios:**
- 1,000 concurrent users
- 10,000 req/min
- 1,000 code submissions/min

**Targets:**
- Response time < 500ms (p95)
- Error rate < 0.1%
- 100% uptime

---

## 7. Disaster Recovery

### 7.1 Backup Strategy
**Database:**
- Automated daily backups (MongoDB Atlas)
- Point-in-time recovery (PITR)
- Cross-region replication
- 30-day retention

**Application:**
- Git version control
- Docker image registry
- Infrastructure as Code (IaC)

### 7.2 Recovery Time Objectives
- RTO (Recovery Time): < 1 hour
- RPO (Recovery Point): < 15 minutes

### 7.3 Failover Plan
1. Detect failure (monitoring alerts)
2. Switch to secondary database replica
3. Scale up backup API pods
4. Update DNS/load balancer
5. Investigate root cause
6. Restore primary service

---

## 8. CI/CD Pipeline

### 8.1 Continuous Integration
**Tool:** GitHub Actions

**Pipeline Steps:**
1. Code push → GitHub
2. Linting (ESLint, Ruff)
3. Unit tests (Jest, pytest)
4. Integration tests
5. Build Docker images
6. Push to registry

### 8.2 Continuous Deployment
**Tool:** ArgoCD / FluxCD

**Deployment Strategy:**
- Blue-green deployment
- Canary releases (10% → 50% → 100%)
- Automatic rollback on errors

**Environments:**
- Development (auto-deploy)
- Staging (manual approval)
- Production (canary + approval)

---

## 9. Cost Optimization

### 9.1 Infrastructure Costs
- **Compute:** Auto-scaling based on demand
- **Database:** Right-sized instances
- **Storage:** S3 lifecycle policies
- **CDN:** Cloudflare (free tier)
- **Monitoring:** Open-source tools

### 9.2 Optimization Strategies
- Reserved instances for base load
- Spot instances for code executors
- Database query optimization
- Cache frequently accessed data
- Compress static assets

---

## 10. Future Enhancements

### 10.1 Phase 2 Features
- AI hint system (OpenAI GPT-5.2)
- Razorpay payment integration
- Google OAuth
- Email notifications

### 10.2 Phase 3 Features
- WebSocket for real-time updates
- Contest mode with leaderboards
- Discussion forum
- Video explanations
- Mobile app (React Native)

### 10.3 Advanced Optimizations
- GraphQL API (Apollo)
- Serverless functions (AWS Lambda)
- Edge computing (Cloudflare Workers)
- ML-based recommendations
- Personalized learning paths

---

## Conclusion

This architecture is designed for production-grade scalability, security, and reliability. The modular design allows for incremental improvements and feature additions without disrupting existing functionality.

**Target Metrics:**
- 100,000+ active users
- 99.9% uptime
- < 500ms response time (p95)
- < 0.1% error rate

**Built for the future of coding education! 🚀**
