"""Run every problem's trace.py to (re)generate its trace.json.

A trace.py mirrors its verified solution and emits the step data the site's
visualizer replays, so the animation stays in sync with the real algorithm.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    traces = sorted(ROOT.glob("[0-9]*/*/trace.py"))
    ok, bad = 0, 0
    for t in traces:
        r = subprocess.run([sys.executable, t.name], cwd=t.parent,
                           capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            ok += 1
            print(f"  {t.relative_to(ROOT)}: {r.stdout.strip()}")
        else:
            bad += 1
            print(f"  FAILED {t.relative_to(ROOT)}\n{r.stderr.strip()[-600:]}")
    print(f"traces built: {ok} ok, {bad} failed")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
