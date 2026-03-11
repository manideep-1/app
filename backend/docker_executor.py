"""
Containerized code execution: no dependency on host PATH.
Runs each submission in an isolated Docker container with security limits.
When Docker/images are unavailable, Python and JavaScript can run via local interpreter (dev fallback).
"""
import logging
import os
import shutil
import subprocess
import sys
import tempfile
from typing import Tuple

from models import Language

logger = logging.getLogger(__name__)
CSHARP_WORKLOAD_NOTICE = (
    'An issue was encountered verifying workloads. For more information, run "dotnet workload update".'
)

# Runner image names (must be built via docker-compose or build script)
RUNNER_IMAGES = {
    Language.PYTHON: "ifelse-runner-python",
    Language.JAVASCRIPT: "ifelse-runner-javascript",
    Language.JAVA: "ifelse-runner-java",
    Language.CPP: "ifelse-runner-cpp",
    Language.C: "ifelse-runner-c",
    Language.GO: "ifelse-runner-go",
    Language.CSHARP: "ifelse-runner-csharp",
    Language.TYPESCRIPT: "ifelse-runner-typescript",
}

# Filenames expected by each runner image
RUNNER_SOURCE_FILES = {
    Language.PYTHON: "code.py",
    Language.JAVASCRIPT: "code.js",
    Language.JAVA: "Main.java",
    Language.CPP: "code.cpp",
    Language.C: "code.c",
    Language.GO: "main.go",
    Language.CSHARP: "Program.cs",
    Language.TYPESCRIPT: "code.ts",
}

# When backend runs in Docker, it uses a shared volume; runner must be invoked with script path.
# Maps language -> (docker run -v mount, list of CMD args with {subdir} placeholder)
RUNNER_VOLUME_ENV = "RUNNER_VOLUME"
RUNNER_WORKSPACE_ENV = "RUNNER_WORKSPACE"
GO_RUNNER_CACHE_DIR_ENV = "GO_RUNNER_CACHE_DIR"
FORCE_LOCAL_PYTHON_EXECUTION_ENV = "FORCE_LOCAL_PYTHON_EXECUTION"


def _container_cmd_for_volume(language: Language, subdir: str) -> list:
    """Return the command override when using shared volume (backend in Docker)."""
    w = f"/workspace/{subdir}"
    return {
        Language.PYTHON: ["python3", f"{w}/code.py"],
        Language.JAVASCRIPT: ["node", f"{w}/code.js"],
        Language.JAVA: ["sh", "-c", f"cd {w} && javac -d . Main.java && java Main"],
        Language.CPP: ["sh", "-c", f"cd {w} && g++ -std=c++17 -o out code.cpp && ./out"],
        Language.C: ["sh", "-c", f"cd {w} && gcc -o out code.c && ./out"],
        Language.GO: [
            "sh",
            "-c",
            f"cd {w} && mkdir -p /workspace/.go-cache {w}/.gotmp && "
            f"GOCACHE=/workspace/.go-cache GOTMPDIR={w}/.gotmp HOME={w} go run main.go",
        ],
        Language.CSHARP: ["sh", "-c", f"cp {w}/Program.cs /app/Program.cs && dotnet run --project /app/App.csproj --no-restore"],
        Language.TYPESCRIPT: ["npx", "ts-node", f"{w}/code.ts"],
    }.get(language) or ["sh", "-c", f"cd {w} && node code.js"]  # fallback

# Default limits: 2s timeout, 256MB (production-ready; override via env)
EXECUTION_TIMEOUT_SEC = int(os.environ.get("EXECUTION_TIMEOUT_SEC", "2"))
CONTAINER_MEMORY_MB = int(os.environ.get("CONTAINER_MEMORY_MB", "256"))
CONTAINER_PIDS_LIMIT = int(os.environ.get("CONTAINER_PIDS_LIMIT", "256"))
GO_EXECUTION_TIMEOUT_SEC = int(os.environ.get("GO_EXECUTION_TIMEOUT_SEC", "4"))
GO_WARMUP_TIMEOUT_SEC = int(os.environ.get("GO_WARMUP_TIMEOUT_SEC", "20"))
CSHARP_EXECUTION_TIMEOUT_SEC = int(os.environ.get("CSHARP_EXECUTION_TIMEOUT_SEC", "12"))
# Java: JVM startup + compile can exceed default 2s
JAVA_EXECUTION_TIMEOUT_SEC = int(os.environ.get("JAVA_EXECUTION_TIMEOUT_SEC", "10"))


def _ensure_dir(path: str, mode: int = 0o777) -> None:
    os.makedirs(path, exist_ok=True)
    try:
        os.chmod(path, mode)
    except Exception:
        pass


def _is_dir_empty(path: str) -> bool:
    try:
        return not any(os.scandir(path))
    except Exception:
        return True


def _timeout_for_language(language: Language, base_timeout: int, go_cache_dir: str = "") -> int:
    timeout = base_timeout
    if language == Language.CSHARP:
        return max(timeout, CSHARP_EXECUTION_TIMEOUT_SEC)
    if language == Language.JAVA:
        return max(timeout, JAVA_EXECUTION_TIMEOUT_SEC)
    if language == Language.GO:
        timeout = max(timeout, GO_EXECUTION_TIMEOUT_SEC)
        if go_cache_dir and _is_dir_empty(go_cache_dir):
            timeout = max(timeout, GO_WARMUP_TIMEOUT_SEC)
    return timeout


def _docker_available() -> bool:
    """Check if Docker is available (socket or DOCKER_HOST)."""
    try:
        r = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _local_python_available() -> bool:
    """Check if Python is available: use same interpreter as this process (sys.executable) or python3 in PATH."""
    # Backend is running in Python, so we always have an interpreter
    if sys.executable:
        try:
            r = subprocess.run(
                [sys.executable, "-c", "print(1)"],
                capture_output=True,
                timeout=5,
            )
            if r.returncode == 0:
                return True
        except Exception:
            pass
    try:
        r = subprocess.run(
            ["python3", "-c", "print(1)"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _local_node_available() -> bool:
    """Check if node is available on the host (dev fallback when Docker unavailable)."""
    try:
        r = subprocess.run(
            ["node", "-e", "console.log(1)"],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def _run_local_python(
    code: str,
    input_data: str,
    timeout_sec: int,
) -> Tuple[str, str, int]:
    """Run Python code in a temp file via same interpreter as backend (or python3). Dev fallback when Docker/images unavailable."""
    work_dir = tempfile.mkdtemp(prefix="ifelse_run_")
    code_path = os.path.join(work_dir, "code.py")
    python_bin = sys.executable if sys.executable else "python3"
    try:
        with open(code_path, "w") as f:
            f.write(code)
        proc = subprocess.run(
            [python_bin, code_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=work_dir,
        )
        return proc.stdout or "", proc.stderr or "", proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Time Limit Exceeded", -1
    finally:
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass


def _run_local_javascript(
    code: str,
    input_data: str,
    timeout_sec: int,
) -> Tuple[str, str, int]:
    """Run JavaScript code in a temp file via node. Dev fallback when Docker/images unavailable."""
    work_dir = tempfile.mkdtemp(prefix="ifelse_run_")
    code_path = os.path.join(work_dir, "code.js")
    try:
        with open(code_path, "w") as f:
            f.write(code)
        proc = subprocess.run(
            ["node", code_path],
            input=input_data,
            capture_output=True,
            text=True,
            timeout=timeout_sec,
            cwd=work_dir,
        )
        return proc.stdout or "", proc.stderr or "", proc.returncode
    except subprocess.TimeoutExpired:
        return "", "Time Limit Exceeded", -1
    finally:
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass


def run_in_docker(
    code: str,
    input_data: str,
    language: Language,
    timeout_sec: int = EXECUTION_TIMEOUT_SEC,
) -> Tuple[str, str, int]:
    """
    Run user code in a fresh container, or via local python3/node when Docker/images unavailable (dev fallback).
    Returns (stdout, stderr, exit_code).
    """
    image = RUNNER_IMAGES.get(language)
    if not image:
        raise ValueError(f"Unsupported language for Docker runner: {language}")

    # Optional opt-in: force local Python execution for offline batch tooling
    # (e.g. test-case generation scripts). This does not affect normal API runtime
    # unless the env var is explicitly set.
    if (
        language == Language.PYTHON
        and str(os.environ.get(FORCE_LOCAL_PYTHON_EXECUTION_ENV, "")).strip() == "1"
        and _local_python_available()
    ):
        logger.info("Running Python via forced local execution")
        return _run_local_python(code, input_data, timeout_sec)

    # Use local fallback when Docker image is missing but host has python3/node (dev only)
    use_docker = _docker_available() and _image_available(image)
    if not use_docker:
        if language == Language.PYTHON and _local_python_available():
            logger.info("Running Python via local fallback (Docker/image not available)")
            return _run_local_python(code, input_data, timeout_sec)
        if language == Language.JAVASCRIPT and _local_node_available():
            logger.info("Running JavaScript via local fallback (Docker/image not available)")
            return _run_local_javascript(code, input_data, timeout_sec)
        # No Docker and no local fallback for this language
        raise RuntimeError(
            "Code execution is not available: Docker runner images are required. "
            "Ensure Docker is running, build runners (./scripts/build-runners.sh from repo root), then restart the backend. "
            "See backend/CODE_RUNTIMES.md. Python/JavaScript have a local fallback when python3/node is installed."
        )

    source_file = RUNNER_SOURCE_FILES[language]
    base_dir = os.environ.get(RUNNER_WORKSPACE_ENV) or tempfile.gettempdir()
    work_dir = tempfile.mkdtemp(prefix="ifelse_run_", dir=base_dir)
    code_path = os.path.join(work_dir, source_file)
    use_shared_volume = bool(os.environ.get(RUNNER_VOLUME_ENV))
    subdir = os.path.basename(work_dir)
    go_cache_dir = ""

    try:
        with open(code_path, "w") as f:
            f.write(code)
        try:
            os.chmod(work_dir, 0o755)
            os.chmod(code_path, 0o644)
        except Exception:
            pass

        # When backend runs in Docker, use shared volume so the runner container sees the same files
        if use_shared_volume:
            volume_name = os.environ.get(RUNNER_VOLUME_ENV)
            mount_arg = f"{volume_name}:/workspace"
            run_cmd = _container_cmd_for_volume(language, subdir)
            # Java/C++/C/C# use ENTRYPOINT scripts; override with sh so our -c "cd ..." runs
            entrypoint_langs = (Language.JAVA, Language.CPP, Language.C, Language.CSHARP)
            cmd = [
                "docker", "run", "--rm",
                "-v", mount_arg,
                "-i",
                "--network=none",
                f"--memory={CONTAINER_MEMORY_MB}m",
                f"--pids-limit={CONTAINER_PIDS_LIMIT}",
                "--tmpfs", "/tmp:rw,noexec,nosuid,size=64m",
                "--security-opt=no-new-privileges",
                "--user=10000:10000",
            ]
            if language != Language.CSHARP:
                cmd += ["--read-only"]
            if language in entrypoint_langs and run_cmd[0] == "sh" and run_cmd[1] == "-c":
                cmd += ["--entrypoint", "sh", image, "-c", run_cmd[2]]
            else:
                cmd += [image] + run_cmd
        else:
            tmpfs_opt = "/tmp:rw,noexec,nosuid,size=64m"
            if language == Language.GO:
                # Go uses temporary executable artifacts while running `go run`.
                tmpfs_opt = "/tmp:rw,exec,nosuid,size=64m"
            cmd = [
                "docker", "run", "--rm",
                "-v", f"{work_dir}:/workspace",
                "-i",
                "--network=none",
                f"--memory={CONTAINER_MEMORY_MB}m",
                f"--pids-limit={CONTAINER_PIDS_LIMIT}",
                "--tmpfs", tmpfs_opt,
                "--security-opt=no-new-privileges",
                "--user=10000:10000",
            ]
            if language != Language.CSHARP:
                cmd += ["--read-only"]  # root fs read-only; /workspace is mounted writable
            if language == Language.GO:
                go_cache_dir = os.environ.get(GO_RUNNER_CACHE_DIR_ENV) or os.path.join(tempfile.gettempdir(), "ifelse_go_cache")
                _ensure_dir(go_cache_dir, 0o777)
                cmd += [
                    "-v", f"{go_cache_dir}:/gocache",
                    "-e", "GOCACHE=/gocache",
                    "-e", "GOTMPDIR=/tmp",
                    "-e", "HOME=/tmp",
                    image, "sh", "-c", "go run /workspace/main.go",
                ]
            else:
                cmd += [image]

        effective_timeout = _timeout_for_language(language, timeout_sec, go_cache_dir)
        logger.info(
            "Running container language=%s image=%s timeout=%ds",
            language.value, image, effective_timeout,
        )
        proc = subprocess.run(
            cmd,
            input=input_data,
            capture_output=True,
            text=True,
            timeout=effective_timeout + 2,  # small buffer over expected runtime
            cwd=None,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        if language == Language.CSHARP and stdout:
            lines = stdout.splitlines()
            lines = [line for line in lines if line.strip() != CSHARP_WORKLOAD_NOTICE]
            if lines:
                stdout = "\n".join(lines)
                if proc.stdout.endswith("\n"):
                    stdout += "\n"
            else:
                stdout = ""
        logger.info(
            "Container finished language=%s exit_code=%s",
            language.value, proc.returncode,
        )
        return stdout, stderr, proc.returncode
    except subprocess.TimeoutExpired as e:
        logger.warning("Container timeout language=%s", language.value)
        # Try to kill any leftover container (best-effort)
        try:
            subprocess.run(
                ["docker", "kill", "--signal=KILL", e.cmd[2] if len(e.cmd) > 2 else ""],
                capture_output=True,
                timeout=2,
            )
        except Exception:
            pass
        return "", "Time Limit Exceeded", -1
    except Exception as e:
        logger.exception("Docker run failed language=%s", language.value)
        raise
    finally:
        try:
            shutil.rmtree(work_dir, ignore_errors=True)
        except Exception:
            pass


def _image_available(image: str) -> bool:
    """Check if a Docker image exists locally."""
    try:
        r = subprocess.run(
            ["docker", "image", "inspect", image],
            capture_output=True,
            timeout=5,
        )
        return r.returncode == 0
    except Exception:
        return False


def get_runner_images_status() -> dict:
    """Return which runner images are available (Docker images or local dev fallback for Python/JS)."""
    docker_ok = _docker_available()
    result = {}
    for lang, image in RUNNER_IMAGES.items():
        if docker_ok and _image_available(image):
            result[lang.value] = True
        elif lang == Language.PYTHON and _local_python_available():
            result[lang.value] = True  # dev fallback
        elif lang == Language.JAVASCRIPT and _local_node_available():
            result[lang.value] = True  # dev fallback
        else:
            result[lang.value] = False
    return result
