# desk

A place to sit down and study: one folder per subject, the lesson that is currently live, and a phone site that follows.

## Layout

```
lessons              CLI: what is active, and open it
state.json           status only (active / done). The file list comes from disk.
assets/              shared lesson engines
site/                static build (python3 site/build.py → site/dist/)
ongoing/             private subjects. Git keeps the README and ignores the rest.
<subject>/
  lessons/           0001-<name>.html, one thing each
  reference/         cards and glossaries
  projects/          <yyyymmdd>-<name>/ with a plan and steps
  tools/             skill pages, replayable, no status
  assets/            that subject's stylesheet and components
```

Lessons and projects start active. Reference starts done. Tools are never tracked in `state.json`.

Subjects you are happy to publish live next to this file (`redshift/`, `swimming/`). Subjects you want to keep on this machine go in `ongoing/<subject>/`, with the same layout. `lessons` opens both. Git tracks `ongoing/README.md` and ignores everything else in that folder, including `ongoing/state.json`, which holds status for those subjects. The published `state.json` does not. A lesson under `ongoing/` links the shared engines with `../../../assets/`, one level deeper than a published subject.

## Use

`lessons` is this repo's `lessons` script. Symlink it onto your PATH (`~/.local/bin/lessons`) or run it from the repo root.

```
lessons                  open every active item
lessons ls               list, no browser
lessons ui               pick, toggle, open
lessons set <frag> done  e.g. lessons set redshift/0001 done
lessons tools            list skill pages
lessons tools <frag>     open one
```

A fragment matches a path or a title: `redshift/0001` and `same slice` find the same lesson.

## Site

```
python3 site/build.py
```

Netlify runs the same command and publishes `site/dist/`. HTML lessons and tools are copied through. Markdown is not: `NOTES.md`, `MISSION.md`, `RESOURCES.md`, and `learning-records/` stay in git and off the site.
