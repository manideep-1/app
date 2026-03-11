"""
Code execution via Docker runners only. No host PATH or host-installed runtimes.
Java, Python, C++, C, and JavaScript run inside isolated containers.
"""
import logging
import os
import time
from typing import Dict, Any, List

from models import Language, SubmissionStatus, TestCase

from docker_executor import (
    run_in_docker,
    get_runner_images_status,
    EXECUTION_TIMEOUT_SEC,
)
from output_compare import compare_outputs

logger = logging.getLogger(__name__)

# When Docker/runner is unavailable (e.g. image not built)
DOCKER_UNAVAILABLE_MSG = (
    "Code execution is not available: Docker runner images are required. "
    "1) Ensure Docker is running. "
    "2) From repo root run: ./scripts/build-runners.sh (or: docker-compose build runner-python runner-javascript runner-java runner-cpp runner-c runner-go runner-csharp runner-typescript). "
    "3) Restart the backend after building. "
    "Verify images: docker images | grep ifelse-runner. See backend/CODE_RUNTIMES.md."
)


def get_available_runtimes() -> Dict[str, bool]:
    """Return which language runtimes are available (Docker runner images). No host PATH used."""
    return get_runner_images_status()


def _wrap_javascript_stdin(code: str) -> str:
    """If JS code does not handle stdin, wrap with readline so input is read from stdin."""
    if "readline" in code or "process.stdin" in code:
        return code
    return f"""
const readline = require('readline');
const rl = readline.createInterface({{ input: process.stdin, output: process.stdout }});
let input = '';
rl.on('line', (line) => {{ input += line + '\\n'; }});
rl.on('close', () => {{
    {code}
}});
"""


class CodeExecutor:
    """Executes user code only inside Docker containers. No host-based execution."""

    def __init__(self):
        self.timeout = EXECUTION_TIMEOUT_SEC

    def execute_code(
        self,
        code: str,
        language: Language,
        test_cases: List[TestCase],
        visible_only: bool = False,
    ) -> Dict[str, Any]:
        """Execute code against test cases. All execution runs in Docker."""
        if visible_only:
            test_cases = [tc for tc in test_cases if not tc.is_hidden]
        results = []
        passed = 0
        total = len(test_cases)
        if total == 0:
            return {
                "status": SubmissionStatus.ACCEPTED,
                "passed": 0,
                "total": 0,
                "test_results": [],
                "runtime": 0,
                "memory": None,
            }

        runtimes = get_available_runtimes()
        if not runtimes.get(language.value, False):
            return self._runtime_unavailable_result(language, test_cases, total)

        total_runtime_ms = 0.0
        for idx, test_case in enumerate(test_cases):
            run_code = code
            if language in (Language.JAVASCRIPT, Language.TYPESCRIPT) and ("readline" not in code and "process.stdin" not in code):
                run_code = _wrap_javascript_stdin(code)
            try:
                start_time = time.time()
                output = self._run_code(run_code, test_case.input, language)
                runtime_ms = (time.time() - start_time) * 1000
                total_runtime_ms += runtime_ms

                output_clean = output.strip()
                is_custom = (test_case.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__"
                if is_custom:
                    is_correct = True
                    passed += 1
                else:
                    expected_clean = (test_case.expected_output or "").strip()
                    is_correct, _ = compare_outputs(output_clean, expected_clean)
                    if is_correct:
                        passed += 1

                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": test_case.expected_output if not test_case.is_hidden and not is_custom else ("Hidden" if test_case.is_hidden else ""),
                    "output": output_clean,
                    "passed": is_correct,
                    "runtime": round(runtime_ms, 2),
                    "hidden": test_case.is_hidden,
                    "custom": is_custom,
                })
            except Exception as e:
                err_msg = str(e)
                if "Time Limit Exceeded" in err_msg:
                    results.append(self._result_row(idx, test_case, "Time Limit Exceeded", False, self.timeout * 1000))
                elif "memory" in err_msg.lower() or "OOM" in err_msg or "MemoryLimit" in err_msg:
                    results.append(self._result_row(idx, test_case, f"Memory Limit Exceeded: {err_msg}", False, 0))
                else:
                    results.append(self._result_row(idx, test_case, f"Runtime Error: {err_msg}", False, 0))

        if passed == total:
            status = SubmissionStatus.ACCEPTED
        elif any("Time Limit Exceeded" in (r.get("output") or "") for r in results):
            status = SubmissionStatus.TIME_LIMIT_EXCEEDED
        elif any("Memory Limit Exceeded" in (r.get("output") or "") for r in results):
            status = SubmissionStatus.MEMORY_LIMIT_EXCEEDED
        elif any(
            "Compil" in (r.get("output") or "") or "error CS" in (r.get("output") or "")
            for r in results
        ):
            status = SubmissionStatus.COMPILE_ERROR
        elif any("Runtime Error" in (r.get("output") or "") for r in results):
            status = SubmissionStatus.RUNTIME_ERROR
        else:
            status = SubmissionStatus.WRONG_ANSWER

        return {
            "status": status,
            "passed": passed,
            "total": total,
            "test_results": results,
            "runtime": round(total_runtime_ms, 2),
            "memory": None,
        }

    def _result_row(self, idx: int, tc: TestCase, output: str, passed: bool, runtime: float) -> Dict[str, Any]:
        is_custom = (tc.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__"
        return {
            "test_case": idx + 1,
            "input": tc.input if not tc.is_hidden else "Hidden",
            "expected": "" if is_custom else (tc.expected_output if not tc.is_hidden else "Hidden"),
            "output": output,
            "passed": passed,
            "runtime": runtime,
            "hidden": tc.is_hidden,
            "custom": is_custom,
        }

    def _runtime_unavailable_result(
        self, language: Language, test_cases: List[TestCase], total: int
    ) -> Dict[str, Any]:
        return {
            "status": SubmissionStatus.RUNTIME_ERROR,
            "passed": 0,
            "total": total,
            "test_results": [
                {
                    "test_case": i + 1,
                    "input": tc.input if not tc.is_hidden else "Hidden",
                    "expected": tc.expected_output if not tc.is_hidden else "Hidden",
                    "output": f"Runtime Error: {DOCKER_UNAVAILABLE_MSG}",
                    "passed": False,
                    "runtime": 0,
                    "hidden": tc.is_hidden,
                    "custom": (tc.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__",
                }
                for i, tc in enumerate(test_cases)
            ],
            "runtime": 0,
            "memory": None,
        }

    def _run_code(self, code: str, input_data: str, language: Language) -> str:
        """Run code in Docker. Returns stdout; raises on failure or TLE."""
        stdout, stderr, exit_code = run_in_docker(
            code, input_data, language, timeout_sec=self.timeout
        )
        if exit_code == -1 and "Time Limit Exceeded" in stderr:
            raise RuntimeError("Time Limit Exceeded")
        if exit_code != 0:
            raise RuntimeError(stderr.strip() or stdout.strip() or "Execution failed")
        return stdout
