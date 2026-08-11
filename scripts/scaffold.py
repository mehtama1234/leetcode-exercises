"""Create per-problem folders and regenerate the README index + chapters.json.

Idempotent: never overwrites an existing solution.py or README.md inside a
problem folder. Only creates missing folders and rewrites the top-level index.
"""
import json
import os
from pathlib import Path

from manifest import CHAPTERS, slugify, total_count

ROOT = Path(__file__).resolve().parents[1]


def build():
    index_rows = []
    manifest = []
    for ch_no, ch_title, ch_slug, problems in CHAPTERS:
        ch_dir = ROOT / ch_slug
        ch_dir.mkdir(exist_ok=True)
        ch_problems = []
        for num, title in problems:
            slug = slugify(num, title)
            (ch_dir / slug).mkdir(exist_ok=True)
            rel = f"{ch_slug}/{slug}"
            ch_problems.append({"number": num, "title": title, "path": rel})
            index_rows.append((ch_no, ch_title, num, title, rel))
        manifest.append({
            "chapter": ch_no, "title": ch_title, "slug": ch_slug,
            "problems": ch_problems,
        })

    (ROOT / "chapters.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    # README index
    lines = [
        "# LeetCode Exercises — First-Principles Solutions",
        "",
        "**Browse it as a site:** https://mehtama1234.github.io/leetcode-exercises/ "
        "(generated into [`docs/`](docs/); run `python3 scripts/build_html.py` to "
        "rebuild, or serve locally with `python3 -m http.server --directory docs`).",
        "",
        "Every problem gets two things:",
        "",
        "1. **`solution.py`** — a clean, correct, self-testing implementation "
        "(runs its own LeetCode example cases as asserts via `python solution.py`).",
        "2. **`README.md`** — a first-principles writeup: the real problem, the "
        "naive idea and why it falls short, the key insight *derived* rather than "
        "memorized, complexity with reasoning, pitfalls, and the transferable pattern.",
        "",
        "The full course outline is preserved verbatim in "
        "[`CURRICULUM.md`](CURRICULUM.md).",
        "",
        f"**{total_count()} coding problems across {len(CHAPTERS)} pattern chapters.**",
        "",
        "## Index",
        "",
    ]
    current = None
    for ch_no, ch_title, num, title, rel in index_rows:
        if ch_no != current:
            lines.append(f"\n### Chapter {ch_no}: {ch_title}\n")
            current = ch_no
        lines.append(f"- [{num} · {title}]({rel}/) "
                     f"— [solution]({rel}/solution.py) · [notes]({rel}/README.md)")
    lines.append("")
    (ROOT / "README.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"scaffolded {total_count()} problems in {len(CHAPTERS)} chapters")


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    build()
