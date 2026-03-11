# Containerized Code Execution

Code runs **only inside Docker**. There is no dependency on the host machine’s Java, Python, gcc, or Node.

## Runner images

| Language   | Base image               | Verify with        |
|-----------|---------------------------|--------------------|
| Java      | eclipse-temurin:17-jdk    | `javac -version`, `java -version` |
| Python    | python:3.11-slim          | `python3 --version` |
| C++       | gcc:latest                | `g++ --version` |
| C         | gcc:latest                | `gcc --version` |
| JavaScript| node:20-slim              | `node --version` |

Images are built from `backend/runners/` (one Dockerfile per language).

## Flow (per submission)

1. Backend creates a temp dir and writes the user’s code to the expected file (`Main.java`, `code.py`, `code.cpp`, `code.c`, `code.js`).
2. Backend runs:  
   `docker run --rm -v <work_dir>:/workspace -i --network=none --memory=128m --pids-limit=50 --read-only --security-opt=no-new-privileges --user=10000:10000 <runner_image>`
3. Stdin = test input; stdout/stderr and exit code are captured.
4. Subprocess timeout enforces time limit; container is removed on exit (no leaks).

## Security

- **Network:** `--network=none`
- **Filesystem:** `--read-only` (root FS); `/workspace` is the only writable mount for compile artifacts.
- **User:** `--user=10000:10000` (non-root)
- **Limits:** `--memory=128m`, `--pids-limit=50`, `--security-opt=no-new-privileges`
- **Timeout:** Enforced by the backend (subprocess timeout).

## Production

1. **Build all images**  
   `docker compose build`

2. **Start stack** (builds runner images, then starts MongoDB and backend)  
   `docker compose up`

   The backend needs the Docker socket:  
   `-v /var/run/docker.sock:/var/run/docker.sock`  
   so it can run `docker run` against the runner images.

3. **Confirmation**  
   On startup, the backend logs:
   - Which runtimes (runner images) are available.
   - `Java runner self-check: OK (containerized execution ready)` after a minimal Java run in Docker.

## Self-validation

From the repo root:

```bash
# Build runner images first
docker compose build runner-java runner-python runner-cpp runner-c runner-javascript

# Run validation (requires Docker and built images)
cd backend && python scripts/validate_runners.py
```

This runs: Hello World (Java), Two Sum–style Java, compile error, runtime error, and timeout (infinite loop).

## No host PATH

- The backend container does **not** install JDK, Python, gcc, or Node for executing user code.
- It only installs the **Docker CLI** and uses the runner images for all execution.
- Runtimes are reported via `docker image inspect` for each runner image, not `which javac`/`which python`, etc.
