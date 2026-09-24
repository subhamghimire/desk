# Shared engines

Generic drill engines live here and are reused by every subject. Check this directory before writing a new widget. Promote a subject component here when a second subject wants it.

Lessons and skill pages link engines from `../../assets/` (a tool or lesson sits one level under the subject). Domain-specific code stays in the subject's own `assets/`.

## Link order

1. `../assets/<subject>.css` — defines the tokens below
2. `../../assets/teach.css`
3. engine scripts
4. skill pages add `../../assets/toolpage.js` last

Tokens the subject stylesheet must set:

`--accent` `--accent-2` `--good` `--bad` `--ink` `--muted` `--bg` `--bg-sunk` `--rule` `--sans` `--serif`

## Contract

- Items are plain objects with stable string `id`s. Resolve domain specs before handing them to an engine.
- Audio is a function: `play: function () { … }` wrapping the subject's own player. Engines never import an audio library.
- One keyboard, one owner. `drill.js` and `speeddrill.js` share a `TEACH._active` token. Every engine returns an api with `stop()`.
- Closed means stopped. A trainer that holds timers, loops, or document-level key listeners must return `{stop}` from `mount`. `toolpage.js` calls it when the trainer closes.
- Trainer `id`s are public deep links. Never rename one after it is published.
- Copy a trainer onto a skill page. Do not point a lesson and a tool at one shared definition. Older lessons may keep a local fork of an engine; leave those forks alone except for bug fixes.

## Seeded now

- `toolpage.js` — `TEACH.trainer`, the skill-page helper
- `teach.css` — structural styles for `.t-trainer`

`store.js`, `drill.js`, `speeddrill.js`, `quiz.js`, and `recall.js` are written when the first lesson needs them, under `window.TEACH`.
