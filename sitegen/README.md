# sitegen — Python static-site generator for BPSC PCS Prep

GitHub Pages serves only static files, so the website is generated from the repo's
Markdown sources by `build.py` (Python 3, standard library only — no pip dependencies).

## Usage

```bash
# from the repo root:
python3 sitegen/build.py            # regenerate the HTML into the repo root
python3 sitegen/build.py --check    # verify two consecutive builds are byte-identical
python3 sitegen/publish.py          # publish new/changed files to GitHub via the API
```

## How it works

1. **Page registry** (`PAGES` in `build.py`): maps each Markdown source to its output
   HTML path and nav section, e.g. `booklist.md` → `books/index.html`.
2. **Section indexes** (`SECTIONS`): auto-generated card pages for `syllabus/`, `notes/`,
   `pyq/` and `strategy/`.
3. **Markdown converter**: a small built-in converter handles headings, paragraphs,
   bold/italic/code, links, lists (one nesting level), tables, blockquotes, fenced code
   blocks and horizontal rules — everything the repo's Markdown uses.
4. **Link rewriting**: in-repo links to `*.md` files are rewritten to the clean site
   URLs (e.g. `strategy/one-attempt-plan.md` → `/bpsc-pcs-prep/strategy/one-attempt-plan/`).
   External links pass through unchanged.
5. **Verbatim copy**: `pyq-analysis/index.html` (the self-contained analysis page) is
   copied byte-for-byte, so its charts and styling are untouched.
6. **Template**: `templates/base.html` — shared header/nav/footer with embedded CSS.
   `{{TITLE}}`, `{{BASE}}`, `{{CONTENT}}` and `{{NAV_*}}` are substituted per page.
7. **`.nojekyll`**: written at the output root so GitHub Pages serves the files
   statically without Jekyll processing.

## Page map (URLs on the live site)

| URL | Source |
|---|---|
| `/` | `README.md` |
| `/books/` | `booklist.md` |
| `/syllabus/`, `/syllabus/prelims/`, `/syllabus/mains/`, `/syllabus/prelims-blueprint/` | generated index + `syllabus/*.md` |
| `/notes/` + `/notes/<name>/` (11 notes) | generated index + `notes/*.md` |
| `/bihar-gk-rapid-fire/` | `bihar-gk-rapid-fire.md` |
| `/pyq/`, `/pyq/strategy/` | generated index + `pyq/strategy.md` |
| `/pyq-analysis/` | `pyq-analysis/index.html` (verbatim) |
| `/strategy/`, `/strategy/<page>/` (8 pages) | generated index + `strategy/*.md` |
| `/assets/svg/*.svg` | diagrams (copied from `sitegen/assets/`) |

## Conventions

- **Idempotent**: no timestamps or random ordering anywhere; `--check` must pass before
  publishing.
- **Single source of truth**: the `.md` files at the repo root. Never hand-edit the
  generated `.html` — re-run the builder instead.
- **New page**: add the `.md` source, register it in `PAGES` (or `SECTIONS`), rebuild.
