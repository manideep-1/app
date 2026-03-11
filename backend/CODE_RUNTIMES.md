# Code execution runtimes (Docker + local fallback)

**Quick fix for "unable to run java" / "Docker runner images are required":**

1. Start **Docker Desktop** (or ensure the Docker daemon is running).
2. From the **repo root** run one of:
   - `./scripts/build-runners.sh`
   - `docker-compose build runner-python runner-javascript runner-java runner-cpp runner-c runner-go runner-csharp runner-typescript`
3. **Restart the backend** (stop and start uvicorn, or `docker-compose restart backend`). The server only checks for images at startup and when you run code.
4. Verify images exist: `docker images | grep ifelse-runner` (you should see ifelse-runner-java, ifelse-runner-python, etc.).

---

The backend runs user code in **Docker containers** when runner images are available. For **Python** and **JavaScript** only, a **local fallback** is used when Docker (or the runner image) is not available: the server runs `python3` or `node` on the host so the compiler/playground works without Docker during development. Other languages (Java, C++, C, Go, C#, TypeScript) always require the corresponding Docker runner image.

## Requirements

1. **Docker** must be installed and running (Docker Desktop or engine).
2. **Runner images** must be built so the backend can run code in them.

## Building runner images

### Option A: Full stack with docker-compose

From the repo root:

```bash
docker-compose build runner-python runner-javascript runner-java runner-cpp runner-c runner-go runner-csharp runner-typescript
```

Or build everything (including backend and MongoDB):

```bash
docker-compose build
```

Then start services as needed. The backend service will have the runner images available.

### Option B: Backend running locally (e.g. uvicorn)

If you run the backend on your machine (e.g. `uvicorn server:app --reload`) and want code execution to work, you still need Docker running and the runner images built. From the repo root:

```bash
./scripts/build-runners.sh
```

Or build images manually (from repo root):

```bash
docker build -t ifelse-runner-python    -f backend/runners/Dockerfile.python    backend/runners
docker build -t ifelse-runner-javascript -f backend/runners/Dockerfile.javascript backend/runners
docker build -t ifelse-runner-java      -f backend/runners/Dockerfile.java      backend/runners
docker build -t ifelse-runner-cpp      -f backend/runners/Dockerfile.cpp      backend/runners
docker build -t ifelse-runner-c        -f backend/runners/Dockerfile.c        backend/runners
docker build -t ifelse-runner-go      -f backend/runners/Dockerfile.go      backend/runners
docker build -t ifelse-runner-csharp  -f backend/runners/Dockerfile.csharp  backend/runners
docker build -t ifelse-runner-typescript -f backend/runners/Dockerfile.typescript backend/runners
```

## If you see "Code execution is not available"

That message means either:

- **Docker is not running** – Start Docker Desktop (or the Docker daemon).
- **Runner images are missing** – Build them with one of the options above, then run the backend.

## Check what’s available

- **At startup**: The server logs which runtimes (runner images) are available.
- **API**: `GET /api/runtimes` returns a JSON object like `{"python": true, "javascript": true, "java": false, ...}`.
