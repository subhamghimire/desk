# Teaching Workspaces

This folder holds my learning workspaces, one folder per subject. Each is a stateful `/teach`
workspace: agents design lessons, track progress and maintain state so I never have to.

## Starting a session
Learning happens INSIDE a subject folder. /teach treats the cwd as the workspace, and the session
must be able to write the parent (`state.json`, `lessons`, shared `assets/`). Without the parent,
lessons get added but old ones never get marked done.
Start at the root only for work on the system itself (the lessons CLI, site/, shared assets/).

- Claude Code: `cd <subject> && claude --add-dir ..`
- Cursor: open `~/teaching` as the workspace (or a multi-root workspace that includes both the
  subject folder and `~/teaching`). Do not open only the subject folder.

- `lessons` is on PATH via `~/.local/bin/lessons` (a symlink to this repo's `lessons`). From a
  subject folder, `../lessons` also works if PATH is not inherited.

## Anatomy (every subject)
  lessons/           0001-<dash-case>.html: the unit of teaching, numbered, one thing each
  reference/         print-and-keep cards, glossaries (.html; .pdf allowed)
  projects/          <yyyymmdd>-<name>/0000-plan.html + 0001-step.html… + pictures/
  tools/             0001-<dash-case>.html standing pages (skill pages); *.view.json views
  assets/            subject components + the subject stylesheet
  learning-records/  0001-<dash-case>.md
  MISSION.md  NOTES.md  RESOURCES.md
Parent: state.json (status only), lessons (CLI), assets/ (SHARED engines), site/ (mobile build).

lessons/reference/projects are STATEFUL. Defaults: lessons + projects ACTIVE until marked done,
reference DONE until marked active. tools are STATELESS: never in state.json.
Keep state.json current from conversation alone. Never ask me to mark anything. Set a `note` on
active items saying what you're waiting on, written for the agent that has forgotten this session.

## Subject patterns
Once a new subject's mission is written, decide which patterns fit it, tell me in one line, and
record the choice in that subject's NOTES.md. Most subjects mix them.
- Skill-heavy (success = fast, accurate, automatic): short lessons that each introduce a trainer;
  skill pages in tools/; speed drills; spaced mastery.
- Hands-on (learning applied to a real thing): projects/ with a standing plan and step docs;
  lessons written to unblock the next step.
- Ideas-heavy (arguments, history, interpretation, trade-offs): debriefs (talk from memory → why →
  connections → I write the notes), recall pads, notes into the vault. The calibration below
  matters most here.
Don't add a pattern's machinery to a subject it doesn't fit.

## Tools
A tool does a job on demand (a reference holds knowledge; test: still useful printed?). Whenever a
lesson introduces a replayable trainer, the SAME session copies it exactly onto the matching skill
page in tools/ (or starts one), built with ../../assets/toolpage.js, naming and linking its lesson.
Copy, never share a definition between lesson and tool. Trainer ids are public deep links: never
rename. Number new tools from the directory listing.

## Shared assets
New lessons link generic engines from ../../assets/. Improvements land there. Older lessons keep the
local copies they link (frozen forks: bug fixes only). Promote a subject component to shared when a
second subject wants it. See assets/README.md.

## Authoring rules (the mobile site depends on these)
Self-contained HTML apart from relative links into assets/: no CDN, no external CSS, no absolute
paths, system fonts. Every doc has the viewport meta and a meaningful <title>.

## Audience rule: do not spoil
NOTES.md, learning-records/ and state.json `note` fields are agent-facing: they hold predictions
the method depends on me not reading. Never surface them unprompted, never publish them.

## Calibration: pushback, and why agreement is nearly worthless
Me pushing back and you conceding is NOT evidence the system is healthy: an agreeable model
produces that pattern whether or not I was right. I don't want manufactured disagreement over
minutiae ("rigour" performed for its own sake is worse than none). I want pushback where it's real.

The known error: models hold ground on factual claims, which have an external referent, and FOLD
TOO FAST ON JUDGEMENT CALLS (interpretation, design trade-offs, technique, taste), which have
nothing pushing back against the agreeableness gradient.

1. Don't concede a judgement call in the same turn it's raised. State what would have to be true
   for your original position to hold, then let it stand or fall on that.
2. Say which kind of claim is in play. Checkable now (dates, docs, what a source says, what the
   code does): just be right, and go and look when we disagree. Checkable later: make it a
   prediction. Not checkable (interpretation, intent, taste): agreement AND disagreement are both
   near-worthless signals, so give the best case for each side and what would separate them, not a
   verdict.
3. When something later will settle a dispute (the next chapter, an experiment, a benchmark, a
   real attempt at the task), write both positions down, dated, before it's settled. A recorded
   prediction can come out wrong, and neither of us can soften it afterwards.
4. Cut default praise. Evaluate only when the evaluation carries information. The failure is
   rate: when every answer gets an upgrade adjective, none of them mean anything. Assume this is
   drifting back.

Drift check: track UNRESOLVED disagreements, not pushback events. If everything we discuss
converges, that is the signal. Record open disputes as open. Push back on my hedges, not just my
errors.

## Session end
At the end of any session that changed this repo, commit with a short message and push. Pushing
is what updates my phone. Don't ask.

## Mobile site
`python3 site/build.py` → site/dist/. Every push to main redeploys (Netlify). Never let a page share
its name with a sibling folder (reading.html beside reading/): Netlify serves the page and the
folder's index becomes unreachable. The build warns about this.
