#!/usr/bin/env python3
"""The `lessons` command is a symlink on PATH. It must scan this repo, not the
directory that holds the symlink. Regression for `os.path.abspath(__file__)`,
which left `lessons ls` reporting "No lessons found under ~/.local/bin".
"""

import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPT = os.path.join(REPO, "lessons")


def main():
    with tempfile.TemporaryDirectory() as tmp:
        link = os.path.join(tmp, "lessons")
        os.symlink(SCRIPT, link)
        proc = subprocess.run(
            [link, "ls"],
            cwd=tmp,
            capture_output=True,
            text=True,
        )
        out = proc.stdout + proc.stderr
        # The bug prints "No lessons found under <symlink dir>" and exits 0.
        # A correct run names this repo, whether or not any lesson exists.
        if proc.returncode != 0 or tmp in out or REPO not in out and "Lessons" not in proc.stdout:
            sys.stderr.write(out)
            sys.stderr.write(f"exit {proc.returncode}\n")
            return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
