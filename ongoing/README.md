# Ongoing

Subjects you are still learning, and do not want on GitHub, go here. One folder per subject, same shape as a published one:

```
ongoing/<subject>/
  lessons/    0001-<name>.html
  reference/
  projects/
  tools/
  assets/
  MISSION.md  NOTES.md  RESOURCES.md
```

`lessons` lists these beside the published subjects. Git ignores everything in this folder except this file and `.gitkeep`.

A lesson here is one directory deeper than `redshift/` or `swimming/`, so shared files are three levels up: `../../../assets/teach.css` and `../../../assets/quiz.js`. The subject stylesheet stays `../assets/<subject>.css`.
