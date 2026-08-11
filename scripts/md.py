"""Tiny dependency-free Markdown -> HTML renderer.

Scoped to the subset the problem READMEs use: headings, bold, inline code,
fenced code blocks, unordered/ordered lists, blockquotes, tables, horizontal
rules, links, and paragraphs. Not a general Markdown engine — just enough to
render this repo faithfully with zero third-party packages.
"""
import html
import re

_CODE_SPAN = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")


def _inline(text: str) -> str:
    """Escape HTML, then apply inline code / bold / links safely."""
    # Pull code spans out first so their contents are never re-formatted.
    spans: list[str] = []

    def stash(m: re.Match) -> str:
        spans.append(html.escape(m.group(1)))
        return f"\x00{len(spans) - 1}\x00"

    text = _CODE_SPAN.sub(stash, text)
    text = html.escape(text)
    text = _BOLD.sub(r"<strong>\1</strong>", text)
    text = _LINK.sub(r'<a href="\2">\1</a>', text)

    def restore(m: re.Match) -> str:
        return f"<code>{spans[int(m.group(1))]}</code>"

    return re.sub(r"\x00(\d+)\x00", restore, text)


def render(md: str) -> str:
    lines = md.split("\n")
    out: list[str] = []
    i = 0
    n = len(lines)

    def close_para(buf: list[str]) -> None:
        if buf:
            out.append(f"<p>{_inline(' '.join(buf))}</p>")
            buf.clear()

    para: list[str] = []
    while i < n:
        line = lines[i]

        # fenced code block
        if line.lstrip().startswith("```"):
            close_para(para)
            lang = line.lstrip()[3:].strip()
            code: list[str] = []
            i += 1
            while i < n and not lines[i].lstrip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1  # skip closing fence
            text = html.escape("\n".join(code))
            if lang in ("diagram", "viz", "trace"):
                # A "whiteboard" panel for ASCII drawings/traces, styled apart
                # from source code so the visual explanation stands out.
                out.append(f'<pre class="diagram">{text}</pre>')
            else:
                cls = f' class="lang-{html.escape(lang)}"' if lang else ""
                out.append(f"<pre><code{cls}>{text}</code></pre>")
            continue

        stripped = line.strip()

        # blank line
        if not stripped:
            close_para(para)
            i += 1
            continue

        # heading
        m = re.match(r"(#{1,6})\s+(.*)", stripped)
        if m:
            close_para(para)
            level = len(m.group(1))
            out.append(f"<h{level}>{_inline(m.group(2))}</h{level}>")
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped):
            close_para(para)
            out.append("<hr>")
            i += 1
            continue

        # table (header row followed by a |---|--- separator)
        if stripped.startswith("|") and i + 1 < n and re.match(
            r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]
        ) and "-" in lines[i + 1]:
            close_para(para)
            def cells(row: str) -> list[str]:
                return [c.strip() for c in row.strip().strip("|").split("|")]
            header = cells(stripped)
            i += 2  # skip header + separator
            rows: list[list[str]] = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(cells(lines[i]))
                i += 1
            thead = "".join(f"<th>{_inline(c)}</th>" for c in header)
            tbody = "".join(
                "<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in r) + "</tr>"
                for r in rows
            )
            out.append(f"<table><thead><tr>{thead}</tr></thead><tbody>{tbody}</tbody></table>")
            continue

        # blockquote
        if stripped.startswith(">"):
            close_para(para)
            quote: list[str] = []
            while i < n and lines[i].strip().startswith(">"):
                quote.append(lines[i].strip()[1:].strip())
                i += 1
            out.append(f"<blockquote>{_inline(' '.join(quote))}</blockquote>")
            continue

        # lists (unordered or ordered), including simple continuation lines
        m_ul = re.match(r"[-*+]\s+(.*)", stripped)
        m_ol = re.match(r"\d+\.\s+(.*)", stripped)
        if m_ul or m_ol:
            close_para(para)
            ordered = bool(m_ol)
            tag = "ol" if ordered else "ul"
            items: list[str] = []
            pat = r"\d+\.\s+(.*)" if ordered else r"[-*+]\s+(.*)"
            while i < n:
                s = lines[i].strip()
                mm = re.match(pat, s)
                if mm:
                    items.append(mm.group(1))
                    i += 1
                elif s and not re.match(r"(#{1,6}\s|[-*+]\s|\d+\.\s|```|>|\|)", s) \
                        and lines[i].startswith((" ", "\t")):
                    items[-1] += " " + s  # continuation of previous item
                    i += 1
                else:
                    break
            body = "".join(f"<li>{_inline(it)}</li>" for it in items)
            out.append(f"<{tag}>{body}</{tag}>")
            continue

        # ordinary paragraph text
        para.append(stripped)
        i += 1

    close_para(para)
    return "\n".join(out)
