#!/usr/bin/env python3
"""
Self-validation for containerized code runners.
Run from repo root: python -m backend.scripts.validate_runners
Or from backend/: python scripts/validate_runners.py (after PYTHONPATH includes backend).
"""
import os
import sys

# Allow running as script from backend/ or as module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Language
from docker_executor import run_in_docker, get_runner_images_status, _docker_available


def main():
    print("=== ifelse runner self-validation ===\n")
    if not _docker_available():
        print("FAIL: Docker is not available (docker info failed).")
        return 1
    print("Docker: OK\n")
    status = get_runner_images_status()
    missing = [lang for lang, ok in status.items() if not ok]
    if missing:
        print("Missing runner images:", missing)
        print("Build with: docker-compose build runner-python runner-java runner-cpp runner-c runner-javascript\n")
    else:
        print("All runner images present:", list(status.keys()))

    # 1. Hello World Java
    print("\n1. Hello World (Java)...")
    hello_java = 'public class Main { public static void main(String[] args) { System.out.println("Hello from Java"); } }'
    try:
        out, err, code = run_in_docker(hello_java, "", Language.JAVA, 5)
        if code == 0 and "Hello from Java" in (out or ""):
            print("   OK:", (out or "").strip())
        else:
            print("   FAIL: code=%s out=%r stderr=%r" % (code, out, err))
    except Exception as e:
        print("   FAIL:", e)

    # 2. Two Sum–style Java (read stdin, print result)
    print("\n2. Two Sum–style Java (stdin -> stdout)...")
    two_sum_java = """
public class Main {
    public static void main(String[] args) {
        java.util.Scanner s = new java.util.Scanner(System.in);
        int n = s.nextInt();
        int target = s.nextInt();
        int[] a = new int[n];
        for (int i = 0; i < n; i++) a[i] = s.nextInt();
        for (int i = 0; i < n; i++)
            for (int j = i + 1; j < n; j++)
                if (a[i] + a[j] == target) {
                    System.out.println(i + " " + j);
                    return;
                }
        System.out.println("-1 -1");
    }
}
"""
    try:
        out, err, code = run_in_docker(two_sum_java, "4\n9\n2 7 11 15\n", Language.JAVA, 5)
        if code == 0 and "0 1" in (out or ""):
            print("   OK: output", (out or "").strip())
        else:
            print("   FAIL: code=%s out=%r stderr=%r" % (code, out, err))
    except Exception as e:
        print("   FAIL:", e)

    # 3. Compile error (Java)
    print("\n3. Compile error (Java)...")
    bad_java = "public class Main { public static void main(String[] args) { System.out.println(undefined); } }"
    try:
        out, err, code = run_in_docker(bad_java, "", Language.JAVA, 5)
        if code != 0 and ("error" in (err or "").lower() or "error" in (out or "").lower()):
            print("   OK: compile error detected (exit %s)" % code)
        else:
            print("   FAIL: expected compile error, got code=%s out=%r stderr=%r" % (code, out, err))
    except Exception as e:
        print("   OK: compile error raised as exception:", str(e)[:80])

    # 4. Runtime error (Java)
    print("\n4. Runtime error (Java)...")
    runtime_err_java = 'public class Main { public static void main(String[] args) { int x = 1/0; } }'
    try:
        out, err, code = run_in_docker(runtime_err_java, "", Language.JAVA, 5)
        if code != 0:
            print("   OK: runtime error detected (exit %s)" % code)
        else:
            print("   FAIL: expected non-zero exit, got code=0")
    except Exception as e:
        print("   OK: runtime error raised:", str(e)[:80])

    # 5. Infinite loop / timeout (Python – easier to TLE)
    print("\n5. Timeout (infinite loop)...")
    infinite_py = "while True: pass"
    try:
        out, err, code = run_in_docker(infinite_py, "", Language.PYTHON, 2)
        if code == -1 or "Time Limit Exceeded" in (err or ""):
            print("   OK: timeout enforced")
        else:
            print("   FAIL: expected TLE, got code=%s err=%r" % (code, err))
    except Exception as e:
        if "Timeout" in str(e) or "TLE" in str(e).upper():
            print("   OK: timeout raised")
        else:
            print("   FAIL:", e)

    print("\n=== validation done ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
