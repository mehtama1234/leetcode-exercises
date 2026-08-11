# Enrichment spec — add "Why this matters" to each problem

Goal: each problem README currently explains the algorithm well but doesn't say
*why the problem matters, where the pattern shows up in the real world, or what
we are fundamentally solving for*. Add exactly that.

For each assigned problem folder, open `README.md` and **insert one new section**
immediately AFTER the `## The problem in plain words` section and BEFORE the next
`##` heading. Do not change anything else in the file.

The new section:

```
## Why this matters

<2–4 tight paragraphs or a short mix of prose + bullets, ~120–200 words>
```

It must cover, in plain everyday language:

1. **The deeper problem underneath the puzzle** — the abstract thing this is a
   stand-in for (e.g. Two Sum is really "given a stream/collection, can I answer
   *has the complement been seen?* in O(1)"). Name the fundamental operation.
2. **Where it actually shows up** — 2–4 *concrete, honest* real-world places the
   same pattern is used: real systems, engineering tasks, products, or domains.
   Be specific (databases, deduplication, autocomplete, rate limiting, routing,
   scheduling, compilers, spellcheck, ML feature pipelines, etc.) and only claim
   uses that are genuinely true. No hand-wavy "used everywhere in tech."
3. **What we're solving for** — the resource or constraint the good solution buys
   (time, memory, a single pass over a stream you can't rewind, avoiding a costly
   recompute, staying within a latency budget).

Rules:
- Plain, concrete, honest. No filler, no invented applications, no hype.
- Keep it tight (~120–200 words). This is motivation, not a second essay.
- Only edit the one `README.md` per assigned folder; touch nothing else.
- Do NOT run git.

Report which problems you updated.
