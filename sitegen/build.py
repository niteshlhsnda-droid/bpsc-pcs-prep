#!/usr/bin/env python3
"""
sitegen/build.py -- static site generator for the BPSC PCS Prep GitHub Pages site.

Reads Markdown sources from the repo root, renders them into the shared template,
copies pyq-analysis/index.html through verbatim, and writes a complete static site
back into the repo root (plus .nojekyll to disable Jekyll processing).

Usage:
    python3 sitegen/build.py            # build into the repo root
    python3 sitegen/build.py --out DIR  # build into another directory (for --check)
    python3 sitegen/build.py --check    # verify two consecutive runs are byte-identical

Idempotency: no timestamps, sorted inputs, deterministic rendering. The --check
mode builds twice into temp dirs and diffs the trees; exits 0 only if identical.

Dependencies: Python 3 stdlib only (a small built-in Markdown converter is used,
supporting headings, paragraphs, bold/italic/code, links, lists, tables,
blockquotes, fenced code blocks and horizontal rules).
"""

from __future__ import annotations

import argparse
import difflib
import filecmp
import html
import os
import re
import shutil
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES = os.path.join(REPO, "sitegen", "templates")
BASE = "/bpsc-pcs-prep"  # project-site path on GitHub Pages

# ---------------------------------------------------------------------------
# Page registry: (markdown source, output path, nav section)
# ---------------------------------------------------------------------------
PAGES = [
    ("home.md", "index.html", "home"),
    ("booklist.md", "books/index.html", "books"),
    ("syllabus/prelims.md", "syllabus/prelims/index.html", "syllabus"),
    ("syllabus/mains.md", "syllabus/mains/index.html", "syllabus"),
    ("syllabus/prelims-blueprint.md", "syllabus/prelims-blueprint/index.html", "syllabus"),
    ("notes/bihar-history.md", "notes/bihar-history/index.html", "notes"),
    ("notes/bihar-geography.md", "notes/bihar-geography/index.html", "notes"),
    ("notes/bihar-polity.md", "notes/bihar-polity/index.html", "notes"),
    ("notes/bihar-economy.md", "notes/bihar-economy/index.html", "notes"),
    ("notes/modern-history.md", "notes/modern-history/index.html", "notes"),
    ("notes/polity.md", "notes/polity/index.html", "notes"),
    ("notes/geography.md", "notes/geography/index.html", "notes"),
    ("notes/economy.md", "notes/economy/index.html", "notes"),
    ("notes/environment.md", "notes/environment/index.html", "notes"),
    ("notes/science-tech.md", "notes/science-tech/index.html", "notes"),
    ("notes/prelims-rapid-fire.md", "notes/prelims-rapid-fire/index.html", "notes"),
    ("bihar-gk-rapid-fire.md", "bihar-gk-rapid-fire/index.html", "bihargk"),
    ("pyq/strategy.md", "pyq/strategy/index.html", "pyq"),
    ("strategy/one-attempt-plan.md", "strategy/one-attempt-plan/index.html", "strategy"),
    ("strategy/memorization.md", "strategy/memorization/index.html", "strategy"),
    ("strategy/mains-answer-writing.md", "strategy/mains-answer-writing/index.html", "strategy"),
    ("strategy/mains-gs1.md", "strategy/mains-gs1/index.html", "strategy"),
    ("strategy/mains-gs2.md", "strategy/mains-gs2/index.html", "strategy"),
    ("strategy/mains-hindi-essay.md", "strategy/mains-hindi-essay/index.html", "strategy"),
    ("strategy/topper-methods.md", "strategy/topper-methods/index.html", "strategy"),
    ("strategy/prelims-vs-mains.md", "strategy/prelims-vs-mains/index.html", "strategy"),
]

# Section index pages generated from card data: (section dir, title, nav, cards)
# cards: (card title, url path relative to BASE, blurb)
SECTIONS = [
    ("syllabus", "Syllabus", "syllabus", [
        ("Prelims Syllabus", "syllabus/prelims/", "One paper, 150 MCQs — full topic-wise syllabus for the screening stage."),
        ("Mains Syllabus", "syllabus/mains/", "Hindi (qualifying) + GS-I + GS-II + Optional + Essay — the 71st-pattern syllabus."),
        ("Prelims Topic-wise Blueprint", "syllabus/prelims-blueprint/", "Decade weightage → study priority: what to study first, with must-know facts per subject."),
    ]),
    ("notes", "Notes", "notes", [
        ("Bihar History", "notes/bihar-history/", "Ancient to modern Bihar — Nalanda, Sher Shah, Champaran and more."),
        ("Bihar Geography", "notes/bihar-geography/", "Rivers, floods, soils, agriculture and districts of Bihar."),
        ("Bihar Polity", "notes/bihar-polity/", "Bihar's governance, panchayats, and state institutions."),
        ("Bihar Economy", "notes/bihar-economy/", "Bihar's economy, budget, schemes and economic survey highlights."),
        ("Modern Indian History", "notes/modern-history/", "Freedom struggle and modern India, BPSC-oriented."),
        ("Indian Polity", "notes/polity/", "Constitution, articles and institutions — the Laxmikanth companion."),
        ("Indian Geography", "notes/geography/", "Physical and Indian geography with map-work focus."),
        ("Indian Economy", "notes/economy/", "Concepts BPSC repeats — GDP, inflation, GST and more."),
        ("Environment & Ecology", "notes/environment/", "Ecology, laws and conventions, BPSC-oriented."),
        ("Science & Technology", "notes/science-tech/", "Everyday science plus tech from current affairs."),
        ("Prelims Rapid-Fire One-Liners", "notes/prelims-rapid-fire/", "High-yield facts for Bihar, Science and Current Affairs — the heaviest Prelims blocks."),
    ]),
    ("pyq", "Previous-Year Questions", "pyq", [
        ("PYQ Strategy", "pyq/strategy/", "How to mine previous-year papers: theme tagging, drills and the one-attempt PYQ calendar."),
        ("10-Year PYQ Analysis", "pyq-analysis/", "Which topics the last 10 years of papers actually reward — weightage tables and trend charts."),
    ]),
    ("strategy", "Study Strategy", "strategy", [
        ("One-Attempt Plan", "strategy/one-attempt-plan/", "The 12-month timetable to crack BPSC CCE in one attempt."),
        ("Memorization System", "strategy/memorization/", "Active recall, spaced repetition and mnemonics that make one attempt enough."),
        ("Mains Answer-Writing Frameworks", "strategy/mains-answer-writing/", "The IBC skeleton, examiner's checklist and worked model answers with diagrams."),
        ("Mains GS-I Topic Guides", "strategy/mains-gs1/", "History, national movement, geography and polity — Bihar-anchored, with maps and timelines."),
        ("Mains GS-II Topic Guides", "strategy/mains-gs2/", "Economy, science-tech, environment and the 30–40% Bihar Special block."),
        ("Mains Hindi + Essay", "strategy/mains-hindi-essay/", "The qualifying paper you can't ignore + the 150-mark essay framework."),
        ("What Toppers Do Differently", "strategy/topper-methods/", "Consensus habits from BPSC topper interviews — distilled, no copying."),
        ("Prelims vs Mains", "strategy/prelims-vs-mains/", "One preparation, two skills: what overlaps and what needs separate training."),
    ]),
]

# Files copied through byte-for-byte (self-contained pages).
VERBATIM = [
    ("pyq-analysis/index.html", "pyq-analysis/index.html"),
]


# ---------------------------------------------------------------------------
# Homepage: hero + stat strip + grouped entry cards.
# home.md holds the remaining body content (exam snapshot); everything
# structural lives here so the homepage stays data-driven and idempotent.
# ---------------------------------------------------------------------------
HOME_TITLE = "Crack BPSC CCE in One Attempt"

HOME_HERO = """<section class="hero">
<p class="kicker">Bihar Public Service Commission · Combined Competitive Examination</p>
<h1>BPSC PCS Prep</h1>
<p class="tagline">Everything you need to crack the BPSC CCE in one attempt — syllabus,
Bihar-first notes, ten years of PYQ analysis, the right books, and a 12-month plan.
Original summaries, free forever.</p>
<div class="cta-row">
<a class="btn primary" href="{BASE}/strategy/one-attempt-plan/">Start with the 12-month plan</a>
<a class="btn" href="{BASE}/pyq-analysis/">See what 10 years of papers reward</a>
</div>
</section>"""

HOME_STATS = [
    ("150", "Prelims MCQs · screening only"),
    ("1,050", "Mains merit marks"),
    ("120", "Interview marks"),
    ("⅓", "Negative marking · Prelims only"),
]

# (group title, group blurb, [(card title, url rel to BASE, blurb)])
HOME_GROUPS = [
    ("Learn", "Know the battlefield first.", [
        ("Syllabus", "syllabus/",
         "Prelims + Mains, topic-wise — exactly what BPSC asks."),
        ("Notes", "notes/",
         "Short, original, Bihar-first: history, geography, polity, economy + the GS core."),
    ]),
    ("Practice", "Train on real questions, with the right books.", [
        ("10-Year PYQ Analysis", "pyq-analysis/",
         "Which topics the last decade of papers actually rewards — weightage & trends."),
        ("Books & Question Banks", "books/",
         "One shelf, no more: PYQ compilations, practice sets, Bihar books."),
        ("Bihar GK Rapid-Fire", "bihar-gk-rapid-fire/",
         "High-yield one-liners: firsts, rivers, GI tags, dances, CMs."),
        ("PYQ Strategy", "pyq/strategy/",
         "How to mine previous-year papers the smart way."),
    ]),
    ("Plan", "One attempt. One timetable.", [
        ("12-Month One-Attempt Plan", "strategy/one-attempt-plan/",
         "The full timetable — day one to interview."),
        ("Mains Answer-Writing", "strategy/mains-answer-writing/",
         "Frameworks, diagrams and model answers for GS-I, GS-II, Hindi and Essay."),
        ("Memorization System", "strategy/memorization/",
         "Active recall + spaced repetition that makes one attempt enough."),
    ]),
]

# One-line descriptions shown under section index headings.
SECTION_DESC = {
    "syllabus": "The official battlefield, topic by topic.",
    "notes": "Short, original and BPSC-oriented — Bihar first, then the GS core.",
    "pyq": "Learn from the papers themselves.",
    "strategy": "Timetables and memory systems for a single serious attempt.",
}

# Breadcrumb section labels: nav key -> (label, url rel to BASE).
CRUMB_SECTIONS = {
    "syllabus": ("Syllabus", "syllabus/"),
    "notes": ("Notes", "notes/"),
    "pyq": ("Previous-Year Questions", "pyq/"),
    "strategy": ("Study Strategy", "strategy/"),
}


def build_url_map() -> dict:
    """Map every in-repo link target to its site URL."""
    m = {}
    for src, out, _nav in PAGES:
        m[src] = BASE + "/" + out.rsplit("/index.html", 1)[0].rstrip("/") + "/"
    m["README.md"] = BASE + "/"
    for sec, _t, _n, cards in SECTIONS:
        m[sec + "/"] = BASE + "/" + sec + "/"
        m[sec] = BASE + "/" + sec + "/"
        for _ct, curl, _b in cards:
            m[curl] = BASE + "/" + curl
            m[curl.rstrip("/")] = BASE + "/" + curl
    for src, out in VERBATIM:
        d = out.rsplit("/", 1)[0]
        m[src] = BASE + "/" + d + "/"
        m[d + "/"] = BASE + "/" + d + "/"
        m[d] = BASE + "/" + d + "/"
    return m


URL_MAP = build_url_map()


def rewrite_url(url: str) -> str:
    if url.startswith(("http://", "https://", "mailto:", "#", "data:")):
        return url
    anchor = ""
    if "#" in url:
        url, anchor = url.split("#", 1)
        anchor = "#" + anchor
    key = url[2:] if url.startswith("./") else url
    if key.startswith("assets/"):
        # site assets (diagrams etc.) -> absolute site URL, works from any depth
        return BASE + "/" + key + anchor
    return URL_MAP.get(key, url) + anchor


# ---------------------------------------------------------------------------
# Minimal Markdown -> HTML converter
# ---------------------------------------------------------------------------
def inline(text: str) -> str:
    text = html.escape(text, quote=False)
    parts = re.split(r"(`[^`\n]+`)", text)
    for j, part in enumerate(parts):
        if part.startswith("`") and part.endswith("`") and len(part) > 2:
            parts[j] = "<code>" + part[1:-1] + "</code>"
        else:
            def link_repl(mo):
                label, href = mo.group(1), mo.group(2).strip()
                return '<a href="' + html.escape(rewrite_url(href), quote=True) + '">' + label + "</a>"
            part = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link_repl, part)
            part = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", part)
            part = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<em>\1</em>", part)
            parts[j] = part
    return "".join(parts)


def strip_md(text: str) -> str:
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"[*_`]", "", text)
    return text.strip()


def is_table_sep(line: str) -> bool:
    s = line.strip().strip("|")
    cells = [c.strip() for c in s.split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{2,}:?", c) for c in cells)


def split_row(line: str):
    s = line.strip()
    if s.startswith("|"):
        s = s[1:]
    if s.endswith("|"):
        s = s[:-1]
    return [c.strip() for c in s.split("|")]


def render_table(header, rows) -> str:
    out = ["<table>", "<thead><tr>" + "".join("<th>" + inline(c) + "</th>" for c in header) + "</tr></thead>"]
    if rows:
        out.append("<tbody>")
        for row in rows:
            # pad short rows so malformed tables don't break layout
            row = row + [""] * (len(header) - len(row))
            out.append("<tr>" + "".join("<td>" + inline(c) + "</td>" for c in row[: len(header)]) + "</tr>")
        out.append("</tbody>")
    out.append("</table>")
    return "\n".join(out)


LIST_ITEM = re.compile(r"^(\s*)([-*+]|\d+[.)])\s+(.*)$")


def render_list(items) -> str:
    """items: list of (indent, marker, text). Supports one nesting level."""
    def kind(marker):
        return "ol" if marker[0].isdigit() else "ul"

    # group into top-level items with optional nested children
    top = []
    for indent, marker, text in items:
        if indent == 0 or not top:
            top.append((marker, text, []))
        else:
            top[-1][2].append((marker, text))
    k = kind(top[0][0])
    out = ["<%s>" % k]
    for marker, text, children in top:
        li = "<li>" + inline(text)
        if children:
            ck = kind(children[0][0])
            li += "<%s>" % ck + "".join("<li>" + inline(t) + "</li>" for _m, t in children) + "</%s>" % ck
        out.append(li + "</li>")
    out.append("</%s>" % k)
    return "\n".join(out)


def md_blocks(src: str):
    """Convert Markdown body to HTML blocks. Returns (title, html)."""
    lines = src.split("\n")
    out = []
    title = None
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        s = line.strip()

        # fenced code block
        if s.startswith("```"):
            buf = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                buf.append(lines[i])
                i += 1
            i += 1  # closing fence
            out.append("<pre><code>" + html.escape("\n".join(buf), quote=False) + "</code></pre>")
            continue

        # ATX heading
        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            text = inline(m.group(2).strip())
            if level == 1 and title is None:
                title = strip_md(m.group(2).strip())
            out.append("<h%d>%s</h%d>" % (level, text, level))
            i += 1
            continue

        # horizontal rule
        if re.fullmatch(r"([-*_]\s*){3,}", s):
            out.append("<hr>")
            i += 1
            continue

        # blockquote
        if s.startswith(">"):
            buf = []
            while i < n and lines[i].strip().startswith(">"):
                buf.append(re.sub(r"^>\s?", "", lines[i].strip()))
                i += 1
            _t, inner = md_blocks("\n".join(buf))
            out.append("<blockquote>\n" + inner + "\n</blockquote>")
            continue

        # table
        if s.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]):
            header = split_row(s)
            i += 2
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                rows.append(split_row(lines[i].strip()))
                i += 1
            out.append(render_table(header, rows))
            continue

        # list
        m = LIST_ITEM.match(line)
        if m:
            items = []
            while i < n:
                m2 = LIST_ITEM.match(lines[i])
                if not m2:
                    break
                items.append((len(m2.group(1)), m2.group(2), m2.group(3)))
                i += 1
            out.append(render_list(items))
            continue

        # blank line
        if not s:
            i += 1
            continue

        # standalone image line -> <figure class="diagram"> (no <p> wrapper)
        m = re.match(r"^!\[([^\]]*)\]\(([^)\s]+)\)\s*$", s)
        if m:
            alt = m.group(1)
            src = rewrite_url(m.group(2).strip())
            out.append('<figure class="diagram"><img src="'
                       + html.escape(src, quote=True) + '" alt="'
                       + html.escape(alt, quote=True)
                       + '" loading="lazy"><figcaption>'
                       + html.escape(alt) + "</figcaption></figure>")
            i += 1
            continue

        # paragraph: gather until blank or block start
        buf = [s]
        i += 1
        while i < n:
            s2 = lines[i].strip()
            if not s2:
                break
            if (s2.startswith("```") or re.match(r"^#{1,6}\s", s2) or s2.startswith(">")
                    or (s2.startswith("|") and i + 1 < n and is_table_sep(lines[i + 1]))
                    or re.fullmatch(r"([-*_]\s*){3,}", s2) or LIST_ITEM.match(lines[i])):
                break
            buf.append(s2)
            i += 1
        out.append("<p>" + inline(" ".join(buf)) + "</p>")

    return title, "\n".join(out)


# ---------------------------------------------------------------------------
# Page rendering
# ---------------------------------------------------------------------------
def load_template() -> str:
    with open(os.path.join(TEMPLATES, "base.html"), encoding="utf-8") as fh:
        return fh.read()


NAV_KEYS = ["home", "syllabus", "notes", "bihargk", "books", "pyq", "strategy"]


def render_page(title: str, body_html: str, nav: str, template: str) -> str:
    page = template.replace("{{TITLE}}", html.escape(title, quote=False))
    page = page.replace("{{BASE}}", BASE)
    page = page.replace("{{CONTENT}}", body_html)
    for key in NAV_KEYS:
        page = page.replace("{{NAV_" + key.upper() + "}}",
                            'class="active"' if key == nav else "")
    return page


def section_index_html(sec: str, title: str, cards) -> str:
    out = ["<h1>%s</h1>" % html.escape(title)]
    desc = SECTION_DESC.get(sec)
    if desc:
        out.append('<p class="section-desc">%s</p>' % html.escape(desc))
    out.append('<div class="cards">')
    for ctitle, curl, blurb in cards:
        out.append('<a class="card" href="%s/%s/">\n<h3>%s</h3>\n<p>%s</p>\n</a>'
                   % (BASE, curl.strip("/"), html.escape(ctitle), html.escape(blurb)))
    out.append("</div>")
    return "\n".join(out)


def crumb_html(trail, current: str) -> str:
    """Breadcrumb: Home › [section ›] page. trail = [(label, url-rel-to-BASE)]."""
    bits = ['<nav class="crumbs" aria-label="Breadcrumb">']
    bits.append('<a href="%s/">Home</a>' % BASE)
    for label, url in trail:
        bits.append('<span class="sep">›</span><a href="%s/%s">%s</a>'
                    % (BASE, url, html.escape(label)))
    bits.append('<span class="sep">›</span><span class="here">%s</span>'
                % html.escape(current))
    bits.append("</nav>")
    return "".join(bits)


def render_home(body_html: str) -> str:
    """Compose the homepage: hero + stat strip + grouped entry cards + body."""
    parts = [HOME_HERO.replace("{BASE}", BASE)]
    parts.append('<section class="stats" aria-label="Exam at a glance">')
    for num, label in HOME_STATS:
        parts.append('<div class="stat"><span class="stat-num">%s</span>'
                     '<span class="stat-label">%s</span></div>'
                     % (html.escape(num), html.escape(label)))
    parts.append("</section>")
    for gtitle, gdesc, cards in HOME_GROUPS:
        parts.append('<section class="hgroup"><h2>%s</h2><p class="gdesc">%s</p>'
                     '<div class="cards">'
                     % (html.escape(gtitle), html.escape(gdesc)))
        for ctitle, curl, blurb in cards:
            parts.append('<a class="card" href="%s/%s">\n<h3>%s</h3>\n<p>%s</p>\n</a>'
                         % (BASE, curl, html.escape(ctitle), html.escape(blurb)))
        parts.append("</div></section>")
    parts.append(body_html)
    return "\n".join(parts)


def build(out_dir: str) -> list:
    """Build the site into out_dir. Returns the list of written relative paths."""
    template = load_template()
    written = []

    def write(rel: str, data: bytes):
        dest = os.path.join(out_dir, rel)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(data)
        written.append(rel)

    # Markdown pages
    for src, out, nav in PAGES:
        with open(os.path.join(REPO, src), encoding="utf-8") as fh:
            md = fh.read()
        title, body = md_blocks(md)
        if not title:
            title = os.path.splitext(os.path.basename(src))[0].replace("-", " ").title()
        if out == "index.html":
            # Homepage: dedicated hero layout, no breadcrumb.
            title = HOME_TITLE
            body = render_home(body)
        elif nav in CRUMB_SECTIONS:
            sec_label, sec_url = CRUMB_SECTIONS[nav]
            body = crumb_html([(sec_label, sec_url)], title) + "\n" + body
        else:
            # Top-level pages (Books, Bihar GK): Home › page.
            body = crumb_html([], title) + "\n" + body
        page = render_page(title, body, nav, template)
        write(out, page.encode("utf-8"))

    # Section index pages
    for sec, title, nav, cards in SECTIONS:
        body = section_index_html(sec, title, cards)
        page = render_page(title, crumb_html([], title) + "\n" + body, nav, template)
        write(sec + "/index.html", page.encode("utf-8"))

    # Verbatim copies
    for src, out in VERBATIM:
        with open(os.path.join(REPO, src), "rb") as fh:
            data = fh.read()
        write(out, data)

    # Static assets (SVG diagrams etc.) copied deterministically, sorted
    assets_src = os.path.join(REPO, "sitegen", "assets")
    if os.path.isdir(assets_src):
        for dirpath, dirnames, filenames in os.walk(assets_src):
            dirnames.sort()
            for fn in sorted(filenames):
                srcp = os.path.join(dirpath, fn)
                rel = os.path.relpath(srcp, assets_src).replace(os.sep, "/")
                with open(srcp, "rb") as fh:
                    data = fh.read()
                write("assets/" + rel, data)

    # Disable Jekyll so Pages serves the static files as-is
    write(".nojekyll", b"")

    return sorted(written)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def check_idempotent() -> bool:
    tmp1 = tempfile.mkdtemp(prefix="sitegen-a-")
    tmp2 = tempfile.mkdtemp(prefix="sitegen-b-")
    try:
        build(tmp1)
        build(tmp2)
        diffs = []
        for dirpath, _dirnames, filenames in os.walk(tmp1):
            for fn in sorted(filenames):
                p1 = os.path.join(dirpath, fn)
                rel = os.path.relpath(p1, tmp1)
                p2 = os.path.join(tmp2, rel)
                if not os.path.exists(p2):
                    diffs.append("missing in second run: " + rel)
                elif not filecmp.cmp(p1, p2, shallow=False):
                    diffs.append("differs: " + rel)
        # check for extra files in second run
        for dirpath, _dirnames, filenames in os.walk(tmp2):
            for fn in sorted(filenames):
                rel = os.path.relpath(os.path.join(dirpath, fn), tmp2)
                if not os.path.exists(os.path.join(tmp1, rel)):
                    diffs.append("extra in second run: " + rel)
        if diffs:
            print("NOT IDEMPOTENT:")
            for d in diffs:
                print("  " + d)
            # show one textual diff for debugging
            return False
        print("OK: two consecutive runs are byte-identical (%d files)." % sum(
            len(f) for _, _, f in os.walk(tmp1)))
        return True
    finally:
        shutil.rmtree(tmp1, ignore_errors=True)
        shutil.rmtree(tmp2, ignore_errors=True)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description="Build the BPSC PCS Prep static site.")
    ap.add_argument("--out", default=REPO, help="output directory (default: repo root)")
    ap.add_argument("--check", action="store_true",
                    help="verify two consecutive builds are byte-identical")
    args = ap.parse_args(argv)

    if args.check:
        return 0 if check_idempotent() else 1

    written = build(args.out)
    print("Wrote %d files to %s" % (len(written), args.out))
    for rel in written:
        print("  " + rel)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
