#!/usr/bin/env python3
"""
Automated Test Runner & Pipeline Quality Gate
Module: question-2-automated-testing/run_tests.py
Description: Runs unit and integration tests using pytest, produces test reports,
             and acts as the CI gate preventing deployment if tests fail.
"""

import os
import sys
import subprocess
import time
from datetime import datetime, timezone

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TESTS_DIR = os.path.join(BASE_DIR, "tests")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
EVIDENCE_DIR = os.path.join(BASE_DIR, "evidence")
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(EVIDENCE_DIR, exist_ok=True)

def run_tests():
    print("=" * 70)
    print(" CI/CD PIPELINE: AUTOMATED TEST EXECUTION GATE")
    print(f" Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)

    report_xml = os.path.join(REPORTS_DIR, "test-report.xml")
    report_txt = os.path.join(REPORTS_DIR, "test-summary.txt")

    cmd = [
        sys.executable, "-m", "pytest",
        TESTS_DIR,
        "-v",
        f"--junitxml={report_xml}"
    ]

    print(f"Executing: {' '.join(cmd)}\n")
    start_time = time.time()
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    duration = time.time() - start_time

    print(result.stdout)

    # Save summary report
    with open(report_txt, "w", encoding="utf-8") as f:
        f.write(result.stdout)

    print("=" * 70)
    if result.returncode == 0:
        print(f" [QUALITY GATE: PASSED] All automated tests passed in {duration:.2f}s.")
        print(" PIPELINE PROCEEDING: Deployment gate unlocked.")
        print("=" * 70)
        return 0
    else:
        print(f" [QUALITY GATE: FAILED] Tests failed with exit code {result.returncode} in {duration:.2f}s.")
        print(" PIPELINE HALTED: Deployment gate BLOCKED.")
        print("=" * 70)
        return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)
