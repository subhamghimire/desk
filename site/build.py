#!/usr/bin/env python3
"""build.py — render the teaching workspaces into a static, read-only site.

    python3 site/build.py          (from the repo root; Netlify runs the same)

Output goes to site/dist/:
  - every subject's lessons/reference/projects/tools docs (html, pdf, pictures)
    plus subject and shared assets, mirrored so relative links keep working
  - index.html — Home: everything ACTIVE across all subjects, a chip per subject
  - <subject>/index.html — the subject page: that subject's shelves, one tab
    each: Now / Tools / Reference / Projects / Lessons
  - <subject>/tools/<name>.html for every view (tools/<name>.view.json): a tool
    generated from the TABLES of markdown files the view names (the reading list)

Deliberately excluded — agent-facing material the teaching method depends on
the learner not reading: state.json `note` fields, NOTES.md, MISSION.md, RESOURCES.md,
learning-records/, and every other .md file's prose. Only pipe-table rows are
ever lifted from markdown, and only from tables a view explicitly names.
"""

import html
import importlib.util
import json
import os
import re
import shutil
import sys
from datetime import date
from importlib.machinery import SourceFileLoader

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "site", "dist")

# Never copied into the site.
SKIP_EXTS = (".md", ".mscz", ".view.json")
KIND_LABEL = {"lesson": "lesson", "ref": "reference", "project": "project", "tool": "tool"}

VIEW_SUFFIX = ".view.json"
# Never a view source, whatever a view file asks for: tables in these are agent-facing too.
AGENT_ONLY = ("notes.md", "mission.md", "resources.md")
AGENT_ONLY_DIRS = ("learning-records",)

# The subject page's shelves, in tab order. A tab exists only when its shelf is non-empty.
SHELVES = (("now", "Now"), ("tools", "Tools"), ("reference", "Reference"),
           ("projects", "Projects"), ("lessons", "Lessons"))


def load_lessons_module():
    """The `lessons` CLI owns scanning and ordering — reuse it, one implementation."""
    path = os.path.join(ROOT, "lessons")
    spec = importlib.util.spec_from_loader("lessons_cli", SourceFileLoader("lessons_cli", path))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def warn(msg):
    sys.stderr.write("build: " + msg + "\n")


# ---------------------------------------------------------------- copy ----


def copy_tree(src, dst):
    """Copy a directory, skipping dotfiles and SKIP_EXTS. Returns file count."""
    n = 0
    for dirpath, dirnames, filenames in os.walk(src):
        dirnames[:] = [d for d in dirnames if not d.startswith(".")]
        rel = os.path.relpath(dirpath, src)
        for f in filenames:
            if f.startswith(".") or f.lower().endswith(SKIP_EXTS):
                continue
            out_dir = os.path.join(dst, rel) if rel != "." else dst
            os.makedirs(out_dir, exist_ok=True)
            shutil.copy2(os.path.join(dirpath, f), os.path.join(out_dir, f))
            n += 1
    return n


def copy_content(subjects):
    n = 0
    shared = os.path.join(ROOT, "assets")
    if os.path.isdir(shared):
        n += copy_tree(shared, os.path.join(DIST, "assets"))
    for subject in subjects:
        for d in ("lessons", "reference", "projects", "tools", "assets"):
            src = os.path.join(ROOT, subject, d)
            if os.path.isdir(src):
                n += copy_tree(src, os.path.join(DIST, subject, d))
    return n


# ------------------------------------------------------------ markdown ----

MD_JUNK = [
    (re.compile(r"\[\[([^\]]+)\]\]"), r"\1"),          # [[wikilink]] -> text
    (re.compile(r"\[([^\]]+)\]\([^)]*\)"), r"\1"),      # [text](url) -> text
    (re.compile(r"`([^`]*)`"), r"\1"),                  # `code` -> text
    (re.compile(r"\*\*([^*]+)\*\*"), r"\1"),            # **bold** -> text
    (re.compile(r"\*([^*]+)\*"), r"\1"),                # *em* -> text
]


def clean_cell(s):
    s = s.strip()
    for rx, rep in MD_JUNK:
        s = rx.sub(rep, s)
    return s


def md_tables(text):
    """Yield (heading, headers, rows) for every pipe table in `text`.

    Only table ROWS are ever extracted — surrounding prose (which may hold
    agent-facing analysis) is never emitted.
    """
    heading = ""
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"#{1,6}\s+(.*)", line)
        if m:
            heading = clean_cell(m.group(1))
            i += 1
            continue
        if line.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1].strip()):
            headers = [clean_cell(c) for c in line.strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                cells = [clean_cell(c) for c in lines[i].strip().strip("|").split("|")]
                cells += [""] * (len(headers) - len(cells))
                rows.append(cells[: len(headers)])
                i += 1
            if rows:
                yield heading, headers, rows
            continue
        i += 1


# ----------------------------------------------------------------- html ----

PAGE_CSS = """
  :root {
    --bg:#faf8f4; --card:#fff; --ink:#1c1b18; --muted:#726d63; --rule:#e2ddd3;
    --accent:#3b5bdb; --good:#2f9e44; --chip:#f0ece4;
  }
  @media (prefers-color-scheme: dark) {
    :root { --bg:#161513; --card:#211f1c; --ink:#eae6de; --muted:#9c968a;
            --rule:#38352f; --accent:#7b96f2; --good:#69c779; --chip:#2b2925; }
  }
  * { box-sizing:border-box; }
  body { margin:0; background:var(--bg); color:var(--ink);
         font:16px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif;
         -webkit-text-size-adjust:100%; }
  main { max-width:640px; margin:0 auto; padding:1.2rem 1rem 4rem; }
  h1 { font-size:1.5rem; margin:0.4rem 0 0.2rem; }
  .sub { color:var(--muted); font-size:0.85rem; margin:0 0 1.4rem; }
  .nav { display:flex; gap:0.5rem; flex-wrap:wrap; margin:0 0 1.6rem; }
  .nav a { color:var(--accent); text-decoration:none; font-weight:600; font-size:0.9rem;
           background:var(--chip); border:1px solid var(--rule); border-radius:999px;
           padding:0.35em 0.95em; }
  .tabs a { color:var(--muted); }
  .tabs a.on { color:var(--bg); background:var(--accent); border-color:var(--accent); }
  h2 { font-size:0.8rem; letter-spacing:0.12em; text-transform:uppercase;
       color:var(--muted); margin:1.8rem 0 0.6rem; }
  h2 a { color:inherit; text-decoration:none; }
  h2 a::after { content:" ›"; }
  h3 { font-size:0.95rem; margin:1.4rem 0 0.5rem; }
  .js .shelf { display:none; }
  .js .shelf.on { display:block; }
  .js .shelf > h2 { display:none; }
  .js .shelf > h3:first-of-type { margin-top:0; }
  .card { display:block; background:var(--card); border:1px solid var(--rule);
          border-radius:12px; padding:0.75rem 0.95rem; margin-bottom:0.55rem;
          text-decoration:none; color:var(--ink); }
  .card:active { border-color:var(--accent); }
  .card.done { opacity:0.6; }
  .card .t { font-weight:600; }
  .card .m { display:flex; gap:0.6em; align-items:center; color:var(--muted);
             font-size:0.75rem; margin-top:0.25rem; }
  .dot { color:var(--good); }
  .kind { background:var(--chip); border-radius:5px; padding:0.05em 0.5em; }
  .bookcard { background:var(--card); border:1px solid var(--rule); border-radius:12px;
              padding:0.75rem 0.95rem; margin-bottom:0.55rem; }
  .bookcard .t { font-weight:600; }
  .bookcard .row { color:var(--muted); font-size:0.8rem; margin-top:0.2rem; }
  .bookcard .row b { color:var(--ink); font-weight:600; }
  footer { color:var(--muted); font-size:0.75rem; margin-top:2.5rem; }
"""

# Subject-page tabs. Without JS every shelf is simply stacked and the tab bar
# works as jump links; with it, one shelf shows at a time and #tools-style
# hashes are stable, bookmarkable addresses.
TAB_JS = """
(function () {
  var tabs = [].slice.call(document.querySelectorAll(".tabs a")),
      shelves = [].slice.call(document.querySelectorAll(".shelf"));
  if (!tabs.length) return;
  // Drop the ids so arriving on #tools never scrolls past the tab bar.
  shelves.forEach(function (s) { s.setAttribute("data-shelf", s.id); s.removeAttribute("id"); });
  function show(id) {
    if (!tabs.some(function (a) { return a.hash === "#" + id; })) return false;
    tabs.forEach(function (a) { a.classList.toggle("on", a.hash === "#" + id); });
    shelves.forEach(function (s) { s.classList.toggle("on", s.getAttribute("data-shelf") === id); });
    return true;
  }
  function fromHash() { if (!show(location.hash.slice(1))) show(tabs[0].hash.slice(1)); }
  document.documentElement.classList.add("js");
  tabs.forEach(function (a) {
    a.addEventListener("click", function (e) {
      e.preventDefault();
      show(a.hash.slice(1));
      // replaceState, not a new entry: Back leaves the subject page in one step.
      try { history.replaceState(null, "", a.hash); } catch (err) {}
    });
  });
  window.addEventListener("hashchange", fromHash);
  fromHash();
  if (location.hash) window.scrollTo(0, 0);
})();
"""

FAVICON = ("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' "
           "viewBox='0 0 100 100'%3E%3Ctext y='.9em' font-size='90'%3E%F0%9F%8E%93%3C/text%3E%3C/svg%3E")


def page(title, body):
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "<meta name=\"robots\" content=\"noindex\">\n"
        "<title>" + html.escape(title) + "</title>\n"
        "<link rel=\"icon\" href=\"" + FAVICON + "\">\n"
        "<style>" + PAGE_CSS + "</style>\n</head>\n<body>\n<main>\n" + body + "\n</main>\n</body>\n</html>\n"
    )


def esc(s):
    return html.escape(str(s), quote=True)


def pretty(subject):
    return subject.replace("-", " ").title()


def display_title(it):
    """Prettify bare-filename titles (PDFs and title-less docs)."""
    t = it.title
    base = os.path.basename(it.rel)
    if t == base:
        stem, ext = os.path.splitext(base)
        stem = re.sub(r"^\d+-", "", stem).replace("-", " ").strip().title()
        t = stem + (" (" + ext[1:].upper() + ")" if ext.lower() == ".pdf" else "")
    return t


def shelf_title(it):
    """On its own subject's page an item needn't repeat the subject:
    'Kana · Japanese' -> 'Kana'. The document's <title> keeps it, for tabs and bookmarks."""
    t = display_title(it)
    for sep in (" · ", " — ", " - "):
        suffix = sep + pretty(it.subject)
        if len(t) > len(suffix) and t.lower().endswith(suffix.lower()):
            return t[: -len(suffix)]
    return t


def item_card(it, updated="", prefix="", show_kind=True, done=False, title=None):
    """`prefix` is the path from the page being built to the item's subject folder."""
    meta = []
    if it.status == "active":
        meta.append('<span class="dot">●</span>')
    if show_kind:
        meta.append('<span class="kind">' + esc(KIND_LABEL.get(it.kind, it.kind)) + "</span>")
    if updated:
        meta.append("<span>" + esc(updated) + "</span>")
    return (
        '<a class="card' + (" done" if done else "") + '" href="' + esc(prefix + it.rel) + '">'
        '<span class="t">' + esc(title or display_title(it)) + "</span>"
        + ('<span class="m">' + "".join(meta) + "</span>" if meta else "") + "</a>"
    )


# ----------------------------------------------------------------- home ----


def build_index(mod, items, state, pages):
    """Home answers one question: what is live right now, across every subject."""
    recs = state.get("items", {})
    active = [i for i in items if i.status == "active"]
    body = ["<h1>Teaching</h1>",
            '<p class="sub">' + str(len(active)) + " active · built " + date.today().isoformat() + "</p>"]

    chips = ['<a href="' + esc(s + "/index.html") + '">' + esc(pretty(s)) + "</a>" for s in pages]
    if chips:
        body.append('<div class="nav">' + "".join(chips) + "</div>")

    for subject, group in mod.order(active):
        name = esc(pretty(subject))
        if subject in pages:
            name = '<a href="' + esc(subject + "/index.html") + '">' + name + "</a>"
        body.append("<h2>" + name + "</h2>")
        for it in group:
            body.append(item_card(it, recs.get(it.key, {}).get("updated", ""), prefix=subject + "/"))

    body.append("<footer>Read-only mirror · state is managed from the desktop</footer>")
    return page("Teaching", "\n".join(body))


# --------------------------------------------------------- subject page ----


def project_groups(items):
    """[(label, [Item])] — one group per project folder, newest project first;
    inside a group the standing plan leads, then steps newest first."""
    groups = {}
    for it in items:
        parts = it.rel.split("/")
        groups.setdefault(parts[1] if len(parts) >= 3 else "", []).append(it)
    out = []
    for key in sorted(groups, reverse=True):
        group = sorted(groups[key], key=lambda i: (
            not os.path.basename(i.rel).startswith("0000-"), -i.sort, i.title))
        # The plan's own title names the project ("VSO Setup Bench · Plan & Status");
        # the folder slug is only the fallback, since title-casing it mangles "VSO".
        plan = display_title(group[0]) if os.path.basename(group[0].rel).startswith("0000-") else ""
        label = plan.split(" · ")[0].strip() if " · " in plan else ""
        label = label or re.sub(r"^\d{8}-", "", key).replace("-", " ").strip().title() or "Other"
        out.append((label, group))
    return out


def build_subject(mod, subject, items, tools, state):
    """The subject page answers the other question: where is that thing?
    Returns None when the subject has nothing to show."""
    recs = state.get("items", {})
    mine = [i for i in items if i.subject == subject]

    def card(it, **kw):
        return item_card(it, recs.get(it.key, {}).get("updated", ""), **kw)

    def is_done(it):
        return it.status != "active"

    ordered = mod.order([i for i in mine if i.status == "active"])
    now = ordered[0][1] if ordered else []
    refs = sorted((i for i in mine if i.kind == "ref"),
                  key=lambda i: (is_done(i), display_title(i).lower()))
    lessons = sorted((i for i in mine if i.kind == "lesson"), key=lambda i: (-i.sort, i.title))
    shelf_tools = sorted((t for t in tools if t.subject == subject),
                         key=lambda t: (-t.sort, display_title(t).lower()))

    projects = []
    for label, group in project_groups([i for i in mine if i.kind == "project"]):
        projects.append("<h3>" + esc(label) + "</h3>")
        projects.extend(card(it, show_kind=False, done=is_done(it)) for it in group)

    content = {
        "now": [card(it) for it in now],
        # Tools are stateless: no dot, no date, nothing to dim.
        "tools": [item_card(it, show_kind=False, title=shelf_title(it)) for it in shelf_tools],
        "reference": [card(it, show_kind=False, title=shelf_title(it)) for it in refs],
        "projects": projects,
        "lessons": [card(it, show_kind=False, done=is_done(it)) for it in lessons],
    }
    shelves = [(sid, label, content[sid]) for sid, label in SHELVES if content[sid]]
    if not shelves:
        return None

    title = pretty(subject)
    body = ['<div class="nav"><a href="../index.html">← Home</a></div>',
            "<h1>" + esc(title) + "</h1>",
            '<p class="sub">built ' + date.today().isoformat() + "</p>"]
    if len(shelves) > 1:
        body.append('<div class="nav tabs">' + "".join(
            '<a href="#' + sid + '">' + esc(label) + "</a>" for sid, label, _ in shelves) + "</div>")
    for sid, label, cards in shelves:
        body.append('<section class="shelf" id="' + sid + '">')
        body.append("<h2>" + esc(label) + "</h2>")
        body.extend(cards)
        body.append("</section>")
    if len(shelves) > 1:
        body.append("<script>" + TAB_JS + "</script>")
    return page(title, "\n".join(body))


# ---------------------------------------------------------------- views ----


def safe_source(subject, rel):
    """Absolute path of a view's markdown source, or None if it may not be read.

    A view can only ever lift tables from a .md file inside its own subject
    folder — and never from the agent-only files, whose tables are as
    do-not-spoil as their prose.
    """
    if not isinstance(rel, str) or not rel.strip():
        return None
    if os.path.isabs(rel) or rel.startswith("~"):
        return None
    parts = [p.lower() for p in rel.replace("\\", "/").split("/")]
    if ".." in parts or any(p in AGENT_ONLY_DIRS for p in parts):
        return None
    if not parts[-1].endswith(".md") or parts[-1] in AGENT_ONLY:
        return None
    base = os.path.realpath(os.path.join(ROOT, subject))
    full = os.path.realpath(os.path.join(base, rel))
    try:
        if os.path.commonpath([base, full]) != base:
            return None
    except ValueError:
        return None
    if os.path.basename(full).lower() in AGENT_ONLY or not os.path.isfile(full):
        return None
    return full


def book_cards(headers, rows):
    out = []
    for row in rows:
        first = row[0] if row else ""
        lines = []
        for h, c in list(zip(headers, row))[1:]:
            if c and c not in ("—", "-"):
                lines.append('<div class="row"><b>' + esc(h) + ":</b> " + esc(c) + "</div>")
        out.append('<div class="bookcard"><div class="t">' + esc(first) + "</div>" + "".join(lines) + "</div>")
    return out


def view_sections(subject, spec, name):
    """Table rows only — never the prose around them."""
    sections = []
    sources = spec.get("sources")
    for src in sources if isinstance(sources, list) else []:
        rel = src.get("file") if isinstance(src, dict) else None
        path = safe_source(subject, rel)
        if not path:
            warn("%s: source %r is not allowed or not found — skipped" % (name, rel))
            continue
        heads = src.get("headings")  # None = every table; a list = substring match; [] = none
        try:
            with open(path, encoding="utf-8") as fh:
                text = fh.read()
        except OSError:
            continue
        for heading, headers, rows in md_tables(text):
            if heads is not None and not any(str(w).lower() in heading.lower() for w in heads):
                continue
            sections.append("<h2>" + esc(heading or os.path.basename(path)) + "</h2>")
            sections.extend(book_cards(headers, rows))
    return sections


def build_views(mod, subjects):
    """Render every tools/*.view.json into dist. Returns {subject: [Item]} so the
    views sit on the Tools shelf beside the authored tools. A broken view is
    skipped with a warning — it must never fail the deploy."""
    out = {}
    for subject in subjects:
        d = os.path.join(ROOT, subject, mod.TOOLS_DIR)
        if not os.path.isdir(d):
            continue
        for fname in sorted(os.listdir(d)):
            if fname.startswith(".") or not fname.lower().endswith(VIEW_SUFFIX):
                continue
            name = subject + "/" + mod.TOOLS_DIR + "/" + fname
            stem = fname[: -len(VIEW_SUFFIX)]
            try:
                with open(os.path.join(d, fname), encoding="utf-8") as fh:
                    spec = json.load(fh)
            except (OSError, ValueError) as exc:
                warn("%s: unreadable (%s) — skipped" % (name, exc))
                continue
            if not isinstance(spec, dict):
                warn("%s: not a JSON object — skipped" % name)
                continue
            dest = os.path.join(DIST, subject, mod.TOOLS_DIR, stem + ".html")
            if os.path.exists(dest):
                warn("%s: an authored tool already owns %s.html — skipped" % (name, stem))
                continue
            sections = view_sections(subject, spec, name)
            if not sections:
                warn("%s: no table rows matched — skipped" % name)
                continue

            m = re.match(r"(\d+)", stem)
            title = spec.get("title") if isinstance(spec.get("title"), str) else ""
            it = mod.Item(subject, mod.TOOLS_DIR + "/" + stem + ".html", "tool",
                          title.strip() or stem + ".html", "", "", int(m.group(1)) if m else 0)
            body = ['<div class="nav"><a href="../index.html#tools">← ' + esc(pretty(subject)) + "</a></div>",
                    "<h1>" + esc(display_title(it)) + "</h1>",
                    '<p class="sub">built ' + date.today().isoformat() + "</p>"]
            body.extend(sections)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf-8") as fh:
                fh.write(page(display_title(it), "\n".join(body)))
            out.setdefault(subject, []).append(it)
    return out


# ----------------------------------------------------------- collisions ----


def shadowed_folders():
    """Every `<name>.html` in dist that sits beside a folder `<name>/`.

    Netlify answers /<name>/ with <name>.html, not <name>/index.html — so the
    folder's index silently becomes unreachable, and no local server shows it.
    (A root-level reading.html once swallowed the whole Reading subject page.)
    Never generate a page named after a folder at the same level."""
    hits = []
    for dirpath, dirnames, filenames in os.walk(DIST):
        for f in filenames:
            stem, ext = os.path.splitext(f)
            if ext.lower() in (".html", ".htm") and stem in dirnames:
                hits.append(os.path.relpath(os.path.join(dirpath, f), DIST))
    return sorted(hits)


# ----------------------------------------------------------------- main ----


def main():
    mod = load_lessons_module()
    state = mod.load_state()
    items = mod.scan(state)
    tools = mod.scan_tools()
    subjects = mod.subjects()

    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST, exist_ok=True)

    copied = copy_content(subjects)

    views = build_views(mod, subjects)
    for group in views.values():
        tools.extend(group)

    pages = []
    for subject in subjects:
        subject_html = build_subject(mod, subject, items, tools, state)
        if not subject_html:
            continue
        os.makedirs(os.path.join(DIST, subject), exist_ok=True)
        with open(os.path.join(DIST, subject, "index.html"), "w", encoding="utf-8") as fh:
            fh.write(subject_html)
        pages.append(subject)

    with open(os.path.join(DIST, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(build_index(mod, items, state, pages))

    for hit in shadowed_folders():
        warn("%s shadows the folder of the same name on Netlify — its index.html is unreachable" % hit)

    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write("User-agent: *\nDisallow: /\n")

    print("built %s: %d files copied, %d items indexed (%d active), %d tools (%d views), "
          "%d subject pages"
          % (DIST, copied, len(items), sum(1 for i in items if i.status == "active"),
             len(tools), sum(len(g) for g in views.values()), len(pages)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
