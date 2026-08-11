"""Run every problem's solution.py and report pass/fail.

Each solution.py is expected to exit 0 when run directly (its `_test()` asserts
its LeetCode example cases). This is the correctness gate for the whole repo.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    solutions = sorted(ROOT.glob("[0-9]*/*/solution.py"))
    passed, failed, empty = [], [], []
    for sol in solutions:
        rel = sol.relative_to(ROOT)
        if sol.stat().st_size == 0:
            empty.append(rel)
            continue
        result = subprocess.run(
            [sys.executable, sol.name], cwd=sol.parent,
            capture_output=True, text=True, timeout=60,
        )
        if result.returncode == 0:
            passed.append(rel)
        else:
            failed.append((rel, result.stdout + result.stderr))

    print(f"passed: {len(passed)}   failed: {len(failed)}   "
          f"empty/todo: {len(empty)}   total: {len(solutions)}")
    for rel, out in failed:
        print(f"\nFAILED {rel}\n{out.strip()[-800:]}")
    if empty:
        print("\nnot yet implemented:")
        for rel in empty:
            print(f"  {rel}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
