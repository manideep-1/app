import subprocess
import sys
import json
import tempfile
import os
import shutil
import logging
from typing import Dict, Any, List
from models import Language, SubmissionStatus, TestCase
import time

logger = logging.getLogger(__name__)

# User-facing message when Java is not installed (used in _run_java and in API)
JAVA_NOT_INSTALLED_MSG = (
    "Java is not installed or not available in PATH. "
    "Install a JDK (e.g. from https://adoptium.net/) and ensure 'javac' and 'java' commands work in your terminal."
)


def get_available_runtimes() -> Dict[str, bool]:
    """Return which language runtimes are available on this system (for startup log and optional API)."""
    return {
        "python": bool(sys.executable),
        "javascript": bool(shutil.which("node")),
        "java": bool(shutil.which("javac") and shutil.which("java")),
        "cpp": bool(shutil.which("g++")),
        "c": bool(shutil.which("gcc")),
    }


class CodeExecutor:
    def __init__(self):
        self.timeout = 5  # 5 seconds timeout
    
    def execute_code(
        self,
        code: str,
        language: Language,
        test_cases: List[TestCase],
        visible_only: bool = False,
    ) -> Dict[str, Any]:
        """Execute code against test cases. If visible_only=True, run only non-hidden cases (e.g. for Run button)."""
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

        # Fail fast if this language runtime is not available (e.g. Java not installed)
        runtimes = get_available_runtimes()
        if not runtimes.get(language.value, False):
            msg = (
                JAVA_NOT_INSTALLED_MSG
                if language == Language.JAVA
                else f"Runtime for '{language.value}' is not available on this server. Install the required compiler/runtime and ensure it is in PATH."
            )
            return {
                "status": SubmissionStatus.RUNTIME_ERROR,
                "passed": 0,
                "total": total,
                "test_results": [
                    {
                        "test_case": i + 1,
                        "input": tc.input if not tc.is_hidden else "Hidden",
                        "expected": tc.expected_output if not tc.is_hidden else "Hidden",
                        "output": f"Runtime Error: {msg}",
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

        total_runtime_ms = 0.0
        for idx, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                output = self._run_code(code, test_case.input, language)
                runtime_ms = (time.time() - start_time) * 1000
                total_runtime_ms += runtime_ms
                
                output_clean = output.strip()
                is_custom = (test_case.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__"
                if is_custom:
                    expected_clean = ""
                    is_correct = True  # Custom: Passed = execution succeeded (no TLE/error)
                    passed += 1
                else:
                    expected_clean = (test_case.expected_output or "").strip()
                    is_correct = output_clean == expected_clean
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
            except subprocess.TimeoutExpired:
                is_custom = (test_case.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__"
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": "" if is_custom else (test_case.expected_output if not test_case.is_hidden else "Hidden"),
                    "output": "Time Limit Exceeded",
                    "passed": False,
                    "runtime": self.timeout * 1000,
                    "hidden": test_case.is_hidden,
                    "custom": is_custom,
                })
            except Exception as e:
                is_custom = (test_case.expected_output or "").strip() == "__CUSTOM_OUTPUT_ONLY__"
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": "" if is_custom else (test_case.expected_output if not test_case.is_hidden else "Hidden"),
                    "output": f"Runtime Error: {str(e)}",
                    "passed": False,
                    "runtime": 0,
                    "hidden": test_case.is_hidden,
                    "custom": is_custom,
                })
        
        # Status: all cases (including custom) must pass for ACCEPTED
        if passed == total:
            status = SubmissionStatus.ACCEPTED
        elif any("Time Limit Exceeded" in (r.get("output") or "") for r in results):
            status = SubmissionStatus.TIME_LIMIT_EXCEEDED
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
            "memory": None,  # Optional: would need memory profiling
        }
    
    def _run_code(self, code: str, input_data: str, language: Language) -> str:
        """Run code with given input and return output"""
        if language == Language.PYTHON:
            return self._run_python(code, input_data)
        elif language == Language.JAVASCRIPT:
            return self._run_javascript(code, input_data)
        elif language == Language.JAVA:
            return self._run_java(code, input_data)
        elif language == Language.CPP:
            return self._run_cpp(code, input_data)
        elif language == Language.C:
            return self._run_c(code, input_data)
        else:
            raise ValueError(f"Unsupported language: {language}")
    
    def _run_python(self, code: str, input_data: str) -> str:
        """Run Python code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            f.flush()
            temp_file = f.name
        
        try:
            result = subprocess.run(
                [sys.executable, temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode != 0:
                raise Exception(result.stderr)
            
            return result.stdout
        finally:
            os.unlink(temp_file)
    
    def _run_javascript(self, code: str, input_data: str) -> str:
        """Run JavaScript code using Node.js. If code already handles stdin (readline/process.stdin), run as-is; else wrap."""
        run_code = code
        if "readline" not in code and "process.stdin" not in code:
            run_code = f"""
const readline = require('readline');
const rl = readline.createInterface({{ input: process.stdin, output: process.stdout }});
let input = '';
rl.on('line', (line) => {{ input += line + '\\n'; }});
rl.on('close', () => {{
    {code}
}});
"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(run_code)
            f.flush()
            temp_file = f.name
        try:
            result = subprocess.run(
                ['node', temp_file],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if result.returncode != 0:
                raise Exception(result.stderr or result.stdout or "Execution failed")
            return result.stdout
        finally:
            try:
                os.unlink(temp_file)
            except OSError:
                pass

    def _run_java(self, code: str, input_data: str) -> str:
        """Run Java code. Expects class Main with main(String[] args); reads stdin."""
        if not shutil.which("javac") or not shutil.which("java"):
            raise RuntimeError(JAVA_NOT_INSTALLED_MSG)
        temp_dir = tempfile.mkdtemp()
        temp_java = os.path.join(temp_dir, 'Main.java')
        with open(temp_java, 'w') as f:
            f.write(code)
        try:
            compile_result = subprocess.run(
                ['javac', temp_java],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=temp_dir
            )
            if compile_result.returncode != 0:
                err = (compile_result.stderr or compile_result.stdout or "Compilation failed").strip()
                if "Unable to locate" in err or "Java Runtime" in err or "could not find" in err.lower():
                    raise RuntimeError(JAVA_NOT_INSTALLED_MSG)
                raise Exception(err)
            run_result = subprocess.run(
                ['java', '-cp', temp_dir, 'Main'],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if run_result.returncode != 0:
                err = (run_result.stderr or run_result.stdout or "Execution failed").strip()
                if "Unable to locate" in err or "Java Runtime" in err or "could not find" in err.lower():
                    raise RuntimeError(JAVA_NOT_INSTALLED_MSG)
                raise Exception(err)
            return run_result.stdout
        finally:
            try:
                shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass

    def _run_cpp(self, code: str, input_data: str) -> str:
        """Run C++ code. Compiles with g++ and runs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(code)
            f.flush()
            temp_cpp = f.name
        out_exe = temp_cpp.replace('.cpp', '.out')
        try:
            compile_result = subprocess.run(
                ['g++', '-std=c++17', '-o', out_exe, temp_cpp],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if compile_result.returncode != 0:
                raise Exception(compile_result.stderr or "Compilation failed")
            run_result = subprocess.run(
                [out_exe],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if run_result.returncode != 0:
                raise Exception(run_result.stderr)
            return run_result.stdout
        finally:
            for p in [temp_cpp, out_exe]:
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except Exception:
                        pass

    def _run_c(self, code: str, input_data: str) -> str:
        """Run C code. Compiles with gcc and runs."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            f.flush()
            temp_c = f.name
        out_exe = temp_c.replace('.c', '.out')
        try:
            compile_result = subprocess.run(
                ['gcc', '-o', out_exe, temp_c],
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if compile_result.returncode != 0:
                raise Exception(compile_result.stderr or "Compilation failed")
            run_result = subprocess.run(
                [out_exe],
                input=input_data,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            if run_result.returncode != 0:
                raise Exception(run_result.stderr)
            return run_result.stdout
        finally:
            for p in [temp_c, out_exe]:
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
