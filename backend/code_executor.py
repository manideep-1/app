import subprocess
import sys
import json
import tempfile
import os
from typing import Dict, Any, List
from models import Language, SubmissionStatus, TestCase
import time


class CodeExecutor:
    def __init__(self):
        self.timeout = 5  # 5 seconds timeout
    
    def execute_code(self, code: str, language: Language, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Execute code against test cases"""
        results = []
        passed = 0
        total = len(test_cases)
        
        for idx, test_case in enumerate(test_cases):
            try:
                start_time = time.time()
                output = self._run_code(code, test_case.input, language)
                runtime = time.time() - start_time
                
                output_clean = output.strip()
                expected_clean = test_case.expected_output.strip()
                
                is_correct = output_clean == expected_clean
                if is_correct:
                    passed += 1
                
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": test_case.expected_output if not test_case.is_hidden else "Hidden",
                    "output": output_clean,
                    "passed": is_correct,
                    "runtime": round(runtime * 1000, 2),  # ms
                    "hidden": test_case.is_hidden
                })
            except subprocess.TimeoutExpired:
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": test_case.expected_output if not test_case.is_hidden else "Hidden",
                    "output": "Time Limit Exceeded",
                    "passed": False,
                    "hidden": test_case.is_hidden
                })
            except Exception as e:
                results.append({
                    "test_case": idx + 1,
                    "input": test_case.input if not test_case.is_hidden else "Hidden",
                    "expected": test_case.expected_output if not test_case.is_hidden else "Hidden",
                    "output": f"Runtime Error: {str(e)}",
                    "passed": False,
                    "hidden": test_case.is_hidden
                })
        
        # Determine overall status
        if passed == total:
            status = SubmissionStatus.ACCEPTED
        elif any("Time Limit Exceeded" in r.get("output", "") for r in results):
            status = SubmissionStatus.TIME_LIMIT_EXCEEDED
        elif any("Runtime Error" in r.get("output", "") for r in results):
            status = SubmissionStatus.RUNTIME_ERROR
        else:
            status = SubmissionStatus.WRONG_ANSWER
        
        return {
            "status": status,
            "passed": passed,
            "total": total,
            "test_results": results
        }
    
    def _run_code(self, code: str, input_data: str, language: Language) -> str:
        """Run code with given input and return output"""
        if language == Language.PYTHON:
            return self._run_python(code, input_data)
        elif language == Language.JAVASCRIPT:
            return self._run_javascript(code, input_data)
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
        """Run JavaScript code using Node.js"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            # Wrap code to handle stdin
            wrapped_code = f"""
const readline = require('readline');
const rl = readline.createInterface({{
    input: process.stdin,
    output: process.stdout
}});

let input = '';
rl.on('line', (line) => {{
    input += line + '\\n';
}});

rl.on('close', () => {{
    {code}
}});
"""
            f.write(wrapped_code)
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
                raise Exception(result.stderr)
            
            return result.stdout
        finally:
            os.unlink(temp_file)
