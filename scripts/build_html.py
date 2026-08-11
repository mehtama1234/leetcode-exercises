"""Generate a browsable static HTML site from the problem folders.

Reads each problem's README.md (rendered via the local md.py) and its
solution.py, and writes:
  site/index.html                      landing + full index
  site/<chapter>/index.html            chapter page
  site/<chapter>/<problem>.html        problem page (notes + solution code)
  site/assets/styles.css               theme
"""
import html
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manifest import CHAPTERS, slugify, total_count  # noqa: E402
from md import render  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "docs"  # served by GitHub Pages (main branch /docs)
GH = "https://github.com/mehtama1234/leetcode-exercises/blob/main"


def shell(title: str, body: str, prefix: str, sidebar: str = "") -> str:
    layout = "with-sidebar" if sidebar else "plain"
    side = f'<aside class="sidebar">{sidebar}</aside>' if sidebar else ""
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<link rel="stylesheet" href="{prefix}assets/styles.css">
</head>
<body>
<header class="topbar">
  <a class="brand" href="{prefix}index.html">LeetCode · First Principles</a>
  <a class="ghlink" href="https://github.com/mehtama1234/leetcode-exercises">GitHub</a>
</header>
<div class="layout {layout}">
{side}
<main>{body}</main>
</div>
</body>
</html>"""


def sidebar_html(prefix: str, active_path: str = "") -> str:
    parts = ['<nav class="side-nav">']
    for ch_no, ch_title, ch_slug, problems in CHAPTERS:
        parts.append(f'<details{" open" if any(f"{ch_slug}/{slugify(nn,tt)}"==active_path for nn,tt in problems) else ""}>')
        parts.append(f'<summary>{ch_no}. {html.escape(ch_title)}</summary><ul>')
        for num, title in problems:
            slug = slugify(num, title)
            path = f"{ch_slug}/{slug}"
            cls = ' class="active"' if path == active_path else ""
            parts.append(
                f'<li{cls}><a href="{prefix}{ch_slug}/{slug}.html">'
                f'{num} · {html.escape(title)}</a></li>')
        parts.append("</ul></details>")
    parts.append("</nav>")
    return "".join(parts)


def build():
    (SITE / "assets").mkdir(parents=True, exist_ok=True)
    (SITE / "assets" / "styles.css").write_text(STYLES, encoding="utf-8")
    viz_js = (Path(__file__).resolve().parent / "assets" / "viz.js").read_text(encoding="utf-8")
    (SITE / "assets" / "viz.js").write_text(viz_js, encoding="utf-8")
    for _, _, ch_slug, _ in CHAPTERS:
        (SITE / ch_slug).mkdir(parents=True, exist_ok=True)

    # landing page
    hero = f"""<section class="hero">
  <h1>LeetCode, from first principles</h1>
  <p class="lead">Every problem worked out the same honest way: what we're really
  solving for, why it matters and where the pattern shows up in real systems, the
  brute-force starting point, the waste that reveals the trick, and a clean
  self-testing solution.</p>
  <p class="counts">{total_count()} problems · {len(CHAPTERS)} pattern chapters ·
  each with a conceptual writeup and verified Python.</p>
</section>
<section class="chapter-grid">"""
    cards = []
    for ch_no, ch_title, ch_slug, problems in CHAPTERS:
        items = "".join(
            f'<li><a href="{ch_slug}/{slugify(num,title)}.html">'
            f'<span class="num">{num}</span> {html.escape(title)}</a></li>'
            for num, title in problems)
        cards.append(f"""<article class="chapter-card">
  <div class="ch-head"><a href="{ch_slug}/index.html"><h2>{ch_no}. {html.escape(ch_title)}</h2></a>
  <span class="pill">{len(problems)}</span></div>
  <ul>{items}</ul>
</article>""")
    body = hero + "".join(cards) + "</section>"
    (SITE / "index.html").write_text(
        shell("LeetCode · First Principles", body, ""), encoding="utf-8")

    # per-chapter and per-problem pages
    flat = [(ch_no, ch_title, ch_slug, num, title)
            for ch_no, ch_title, ch_slug, problems in CHAPTERS
            for num, title in problems]

    for idx, (ch_no, ch_title, ch_slug, num, title) in enumerate(flat):
        slug = slugify(num, title)
        folder = ROOT / ch_slug / slug
        readme = (folder / "README.md").read_text(encoding="utf-8")
        code = (folder / "solution.py").read_text(encoding="utf-8")
        rel = f"{ch_slug}/{slug}"

        crumbs = (f'<nav class="crumbs"><a href="../index.html">Home</a> / '
                  f'<a href="index.html">{ch_no}. {html.escape(ch_title)}</a> / '
                  f'<span>{num}</span></nav>')
        notes = render(readme)

        viz_html = ""
        trace_path = folder / "trace.json"
        if trace_path.exists():
            raw = trace_path.read_text(encoding="utf-8")
            # keep the inline JSON from prematurely closing the <script>
            safe = raw.replace("</", "<\\/")
            viz_html = (
                '<section class="viz-section"><h2>Watch it run</h2>'
                '<p class="viz-hint">Step through the algorithm one move at a time — '
                'this replays a trace emitted by the verified solution, so it matches '
                'the code exactly.</p>'
                '<div class="viz"><script type="application/json" class="viz-data">'
                + safe + '</script></div></section>'
                '<script src="../assets/viz.js"></script>')

        code_block = (f'<section class="solution"><h2>Solution (Python)</h2>'
                      f'<p class="srcnote">Self-testing — run <code>python3 solution.py</code>. '
                      f'<a href="{GH}/{rel}/solution.py">view on GitHub</a></p>'
                      f'<pre><code>{html.escape(code)}</code></pre></section>')

        prev_next = []
        if idx > 0:
            p = flat[idx - 1]
            prev_next.append(
                f'<a class="pn prev" href="../{p[2]}/{slugify(p[3],p[4])}.html">'
                f'← {p[3]} · {html.escape(p[4])}</a>')
        else:
            prev_next.append("<span></span>")
        if idx < len(flat) - 1:
            nx = flat[idx + 1]
            prev_next.append(
                f'<a class="pn next" href="../{nx[2]}/{slugify(nx[3],nx[4])}.html">'
                f'{nx[3]} · {html.escape(nx[4])} →</a>')
        body = (crumbs + f'<article class="notes">{notes}</article>' + viz_html
                + code_block + f'<nav class="prevnext">{"".join(prev_next)}</nav>')
        page = shell(f"{num}. {title}", body, "../",
                     sidebar=sidebar_html("../", rel))
        (SITE / ch_slug / f"{slug}.html").write_text(page, encoding="utf-8")

    # chapter index pages
    for ch_no, ch_title, ch_slug, problems in CHAPTERS:
        rows = "".join(
            f'<li><a href="{slugify(num,title)}.html"><span class="num">{num}</span>'
            f'{html.escape(title)}</a></li>' for num, title in problems)
        body = (f'<nav class="crumbs"><a href="../index.html">Home</a> / '
                f'<span>{ch_no}. {html.escape(ch_title)}</span></nav>'
                f'<section class="hero"><h1>{ch_no}. {html.escape(ch_title)}</h1>'
                f'<p class="counts">{len(problems)} problems</p></section>'
                f'<ul class="chapter-list">{rows}</ul>')
        (SITE / ch_slug / "index.html").write_text(
            shell(f"{ch_no}. {ch_title}", body, "../",
                  sidebar=sidebar_html("../", f"{ch_slug}/")), encoding="utf-8")

    pages = len(list(SITE.rglob("*.html")))
    print(f"built {pages} html pages into {SITE}")


STYLES = """
:root{
  --bg:#f4efe7; --panel:#fbf8f2; --ink:#2b2620; --muted:#7c7266;
  --line:#e5ddd0; --accent:#b5651d; --accent-soft:#f0e2d2; --code-bg:#2b2620;
  --code-ink:#f0e9dd; --link:#9c5518;
}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
a{color:var(--link);text-decoration:none}
a:hover{text-decoration:underline}
.topbar{position:sticky;top:0;z-index:10;display:flex;justify-content:space-between;
  align-items:center;padding:12px 22px;background:var(--panel);
  border-bottom:1px solid var(--line)}
.brand{font-weight:700;color:var(--ink);letter-spacing:.2px}
.ghlink{font-size:14px;color:var(--muted)}
.layout{max-width:1180px;margin:0 auto;padding:0 20px}
.layout.with-sidebar{display:grid;grid-template-columns:270px 1fr;gap:34px;align-items:start}
main{padding:26px 0 80px;min-width:0}
.sidebar{position:sticky;top:57px;max-height:calc(100vh - 57px);overflow:auto;
  padding:20px 6px 40px;border-right:1px solid var(--line)}
.side-nav summary{cursor:pointer;font-weight:600;font-size:14px;padding:5px 6px;
  border-radius:6px;color:var(--ink)}
.side-nav summary:hover{background:var(--accent-soft)}
.side-nav ul{list-style:none;margin:2px 0 10px;padding:0 0 0 8px}
.side-nav li a{display:block;font-size:13px;color:var(--muted);padding:3px 8px;
  border-radius:5px;line-height:1.4}
.side-nav li a:hover{color:var(--ink);text-decoration:none;background:var(--accent-soft)}
.side-nav li.active a{color:var(--accent);font-weight:600;background:var(--accent-soft)}
.hero h1{font-size:33px;line-height:1.15;margin:.2em 0 .35em}
.lead{font-size:18px;color:#463f36;max-width:70ch}
.counts{color:var(--muted);font-size:14px}
.chapter-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));
  gap:18px;margin-top:26px}
.chapter-card{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:16px 18px}
.ch-head{display:flex;justify-content:space-between;align-items:center;gap:10px}
.chapter-card h2{font-size:17px;margin:0 0 2px}
.chapter-card a{color:var(--ink)}
.pill{background:var(--accent-soft);color:var(--accent);font-size:12px;font-weight:700;
  border-radius:20px;padding:2px 9px}
.chapter-card ul{list-style:none;margin:10px 0 0;padding:0}
.chapter-card li a{display:flex;gap:8px;font-size:14px;padding:3px 0;color:#4a4239}
.num{color:var(--accent);font-variant-numeric:tabular-nums;min-width:2.6em}
.chapter-list{list-style:none;padding:0;max-width:60ch}
.chapter-list li a{display:flex;gap:10px;padding:9px 12px;background:var(--panel);
  border:1px solid var(--line);border-radius:9px;margin-bottom:7px;color:#433c33}
.crumbs{font-size:13px;color:var(--muted);margin-bottom:14px}
.crumbs span{color:var(--ink)}
.notes{max-width:74ch}
.notes h1{font-size:30px;line-height:1.15;margin:.1em 0 .5em}
.notes h2{font-size:21px;margin:1.6em 0 .5em;padding-top:.3em;border-top:1px solid var(--line)}
.notes h3{font-size:17px;margin:1.3em 0 .4em}
.notes p{margin:.7em 0}
.notes strong{color:#22201b}
.notes ul,.notes ol{padding-left:1.4em}
.notes li{margin:.3em 0}
.notes blockquote{margin:1em 0;padding:.4em 1em;border-left:3px solid var(--accent);
  background:var(--panel);color:#43392e}
.notes table{border-collapse:collapse;margin:1em 0;font-size:14px;display:block;overflow-x:auto}
.notes th,.notes td{border:1px solid var(--line);padding:6px 11px;text-align:left}
.notes th{background:var(--accent-soft)}
code{background:var(--accent-soft);color:#7a3f12;padding:.1em .35em;border-radius:5px;
  font:14px/1.5 "SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace}
pre{background:var(--code-bg);color:var(--code-ink);padding:16px 18px;border-radius:10px;
  overflow-x:auto;margin:1em 0}
pre code{background:none;color:inherit;padding:0;font-size:13px;line-height:1.6}
pre.diagram{background:#fffdf8;color:#2b2620;border:1px solid #e0d6c4;
  border-left:4px solid var(--accent);border-radius:8px;padding:14px 16px;
  font:13px/1.5 "SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace;
  white-space:pre;box-shadow:0 1px 2px rgba(120,90,50,.06)}
.solution{margin-top:40px}
.solution h2{font-size:21px;border-top:1px solid var(--line);padding-top:1.2em}
.srcnote{font-size:13px;color:var(--muted)}
.prevnext{display:flex;justify-content:space-between;gap:16px;margin-top:44px;
  border-top:1px solid var(--line);padding-top:18px}
.pn{font-size:14px;max-width:46%}
.pn.next{text-align:right;margin-left:auto}
@media(max-width:820px){
  .layout.with-sidebar{grid-template-columns:1fr}
  .sidebar{display:none}
}

/* ---- step-through visualizer ---- */
.viz-section{margin-top:40px;border-top:1px solid var(--line);padding-top:1.2em}
.viz-section h2{font-size:21px;margin:.2em 0 .3em}
.viz-hint{font-size:13px;color:var(--muted);max-width:66ch;margin:0 0 14px}
.viz{background:var(--panel);border:1px solid var(--line);border-radius:12px;
  padding:16px 16px 12px}
.viz-title{font-weight:600;font-size:15px;margin-bottom:10px;color:#22201b}
.viz-acts{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:12px}
.viz-act{font-size:12px;font-family:inherit;padding:4px 10px;border-radius:20px;
  border:1px solid var(--line);background:#fffdf8;color:var(--muted);cursor:pointer;
  transition:background .2s,color .2s,border-color .2s}
.viz-act:hover{border-color:var(--accent);color:var(--accent)}
.viz-act.active{background:var(--accent);color:#fff;border-color:var(--accent);font-weight:600}
.viz-act.done{background:var(--accent-soft);color:var(--accent);border-color:var(--accent-soft)}
.viz-stage{display:flex;gap:16px;align-items:flex-start;flex-wrap:wrap}
.viz-svg-wrap{flex:1 1 340px;min-width:0;overflow-x:auto}
.viz-svg{width:100%;height:auto;min-height:150px}
.viz-cell{fill:#fffdf8;stroke:#d9cdb8;stroke-width:1.5;
  transition:fill .3s ease,stroke .3s ease}
.viz-cell.m-active{fill:var(--accent-soft);stroke:var(--accent);stroke-width:2.5}
.viz-cell.m-good{fill:#dff0e4;stroke:#2f8f5b;stroke-width:2.5}
.viz-cell.m-bad{fill:#f6ddd2;stroke:#c0562f;stroke-width:2.5}
.viz-cell.m-dim{fill:#efe8dc;stroke:#d9cdb8}
.viz-cell-val{font:600 18px "SFMono-Regular",Consolas,monospace;fill:#2b2620}
.viz-cell-idx{font:12px sans-serif;fill:var(--muted)}
.viz-ptr{transition:transform .4s cubic-bezier(.4,0,.2,1)}
.viz-ptr-tri{fill:var(--accent)}
.viz-ptr-name{font:600 12px sans-serif;fill:var(--accent)}
.viz-window{fill:var(--accent);opacity:.1;transition:x .4s ease,width .4s ease,opacity .3s}
.viz-sidebar{flex:0 0 180px;font-size:13px;background:#fffdf8;border:1px solid var(--line);
  border-radius:8px;padding:8px 10px}
.viz-sb-title{font-weight:600;font-size:12px;color:var(--muted);margin-bottom:4px}
.viz-sidebar table{width:100%;border-collapse:collapse}
.viz-sidebar td{padding:2px 6px;border-bottom:1px solid var(--line);
  font-family:"SFMono-Regular",Consolas,monospace}
.viz-edge{stroke:#c9bca6;stroke-width:2}
.viz-ll-edge{fill:none;stroke:var(--accent);stroke-width:2;marker-end:url(#none);
  transition:d .3s ease}
.viz-ll-null{fill:none;stroke:#c0562f;stroke-width:2}
.viz-node{fill:#fffdf8;stroke:#d9cdb8;stroke-width:2;transition:fill .3s,stroke .3s}
.viz-node.active{fill:var(--accent-soft);stroke:var(--accent);stroke-width:3}
.viz-node.resolved{fill:#dff0e4;stroke:#2f8f5b}
.viz-node-val{font:600 16px "SFMono-Regular",Consolas,monospace;fill:#2b2620}
.viz-node-badge{font:700 13px sans-serif;fill:#2f8f5b}
.viz-note{margin:12px 2px 8px;min-height:2.6em;font-size:14px;color:#3a332b;
  background:#fffdf8;border-left:3px solid var(--accent);padding:8px 12px;border-radius:0 6px 6px 0}
.viz-banner{margin:8px 2px 0;font-weight:600;color:#2f6f4a;background:#dff0e4;
  border:1px solid #b6dcc4;border-radius:8px;padding:8px 12px;font-size:14px}
.viz-controls{display:flex;align-items:center;gap:8px;margin-top:12px;flex-wrap:wrap}
.viz-btn{background:var(--panel);border:1px solid var(--line);border-radius:7px;
  padding:5px 11px;font-size:14px;cursor:pointer;color:var(--ink)}
.viz-btn:hover{background:var(--accent-soft);border-color:var(--accent)}
.viz-play{font-weight:600}
.viz-scrub{flex:1 1 120px;accent-color:var(--accent)}
.viz-counter{font-size:13px;color:var(--muted);font-variant-numeric:tabular-nums}
.viz-speed{border:1px solid var(--line);border-radius:7px;padding:4px 6px;background:var(--panel);
  color:var(--ink);font-size:13px;cursor:pointer}
/* two-column: diagram+note on the left, code panel on the right */
.viz-cols{display:grid;grid-template-columns:1fr minmax(0,300px);gap:16px;align-items:start}
.viz-left{min-width:0}
.viz-intro{background:var(--accent);color:#fff;border-radius:8px;padding:8px 12px;
  font-size:13px;margin-bottom:8px}
.viz-invariant{background:#fff8ef;border:1px dashed var(--accent);border-radius:8px;
  padding:6px 12px;font-size:13px;color:#5a463a;margin-bottom:12px}
.viz-invariant b{color:var(--accent)}
.viz-rail{display:flex;flex-direction:column;gap:10px;flex:0 0 180px}
.viz-state{background:#fffdf8;border:1px solid var(--line);border-radius:8px;padding:8px 10px;font-size:13px}
.viz-state-row{display:flex;justify-content:space-between;gap:10px;padding:2px 2px;
  font-family:"SFMono-Regular",Consolas,monospace}
.viz-state-row span{color:var(--muted)}
.viz-state-row b{color:#2b2620}
.viz-state-row.work b{color:var(--accent)}
.viz-arc{fill:none;stroke:var(--accent);stroke-width:2;stroke-dasharray:4 3;
  transition:opacity .25s}
.viz-code{background:var(--code-bg);color:var(--code-ink);border-radius:10px;padding:12px 4px;
  margin:0;overflow-x:auto;font:12.5px/1.7 "SFMono-Regular",Consolas,Menlo,monospace}
.viz-code-line{display:block;padding:1px 12px;white-space:pre;border-left:3px solid transparent}
.viz-code-line.active{background:rgba(181,101,29,.28);border-left-color:var(--accent);color:#fff}
.viz-legend{display:flex;flex-wrap:wrap;gap:14px;margin:10px 2px 0;font-size:12px;color:var(--muted)}
.viz-legend-item{display:flex;align-items:center;gap:5px}
.viz-legend .sw{width:13px;height:13px;border-radius:3px;display:inline-block;
  border:1.5px solid #d9cdb8;background:#fffdf8}
.viz-legend .sw.m-active{background:var(--accent-soft);border-color:var(--accent)}
.viz-legend .sw.m-good{background:#dff0e4;border-color:#2f8f5b}
.viz-legend .sw.m-bad{background:#f6ddd2;border-color:#c0562f}
.viz-legend .sw.m-dim{background:#efe8dc}
@media(max-width:720px){.viz-cols{grid-template-columns:1fr}.viz-stage{flex-direction:column}}
"""


if __name__ == "__main__":
    os.chdir(Path(__file__).resolve().parent)
    build()
