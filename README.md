# desk

A place to sit down and study: one folder per subject, the lesson that is currently live, and a phone site that follows.

You ask an LLM for one move. It writes a single HTML lesson and a short drill. A `lessons` command opens whatever is in progress. The next lesson waits until you have done the drill.

Redshift query design and swimming are the two subjects in this repo. Anything you want to keep on your machine goes in `ongoing/`.

## Setup

You need git and Python 3. The `lessons` command opens HTML with macOS `open`.

```bash
git clone git@github.com:subhamghimire/desk.git
cd desk
mkdir -p ~/.local/bin
ln -sf "$PWD/lessons" ~/.local/bin/lessons
```

`~/.local/bin` has to be on your `PATH`. Open a new terminal and check:

```bash
lessons ls
```

You should see the Redshift lesson and the swimming lesson, both active. Open them:

```bash
lessons
```

That opens every active lesson in the browser. To open one, run `lessons ui`, move to it, and press `o`. Or open the file directly:

```bash
open swimming/lessons/0001-blow-the-air-out.html
```

Read the page, then answer the drill at the bottom.

## Start something new

Open this repo in Cursor (the whole `desk` folder, not only a subject folder) and say what you want to learn:

```
teach me guitar
```

The model adds one subject and one lesson. Personal subjects go in `ongoing/<subject>/`. Git ignores that folder except `ongoing/README.md`, so the new subject stays on your machine. `lessons` still lists it, because status for those subjects lives in `ongoing/state.json`, which is also ignored.

When the lesson file is there:

```bash
lessons ls
lessons
```

A subject you are happy to publish is a folder next to `redshift/` and `swimming/` instead. Same shape either way.

Do the drill, then come back and say how it went. The next lesson is written after that, not before.

## Commands

```
lessons                  open every active item
lessons ls               list, no browser
lessons ui               pick, toggle, open
lessons set <frag> done  e.g. lessons set redshift/0001 done
lessons tools            list skill pages
lessons tools <frag>     open one
```

A fragment matches a path or a title: `redshift/0001` and `same slice` find the same lesson. Lessons and projects start active. Reference starts done. Skill pages in `tools/` are never tracked in `state.json`.

## Layout

```
lessons              CLI: what is active, and open it
state.json           status for published subjects only
ongoing/state.json   status for private subjects (not in git)
assets/              shared lesson engines
site/                static build
ongoing/<subject>/   private study, same shape as a published subject
<subject>/
  lessons/           0001-<name>.html, one thing each
  reference/         cards and glossaries
  projects/          <yyyymmdd>-<name>/ with a plan and steps
  tools/             skill pages, replayable
  assets/            that subject's stylesheet
```

A lesson under `ongoing/` is one directory deeper, so it links shared engines with `../../../assets/`. A published lesson uses `../../assets/`.

## Site

```bash
python3 site/build.py
```

Output is `site/dist/`. Netlify runs the same command. HTML lessons and tools are copied through. Markdown is not: `NOTES.md`, `MISSION.md`, `RESOURCES.md`, and `learning-records/` stay in git and off the site. Private subjects are not on GitHub, so they are not on the published site either.
