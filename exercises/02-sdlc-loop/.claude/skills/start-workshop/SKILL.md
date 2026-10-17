---
name: start-workshop
description: Walks a workshop participant through setup for the Live Poll SDLC workshop. It checks the agentic-sdlc kit and the Python environment, runs the tests, creates a feature branch, and helps pick a feature from FEATURES.md. Use when the user runs /start-workshop or asks how to get started with the workshop.
disable-model-invocation: true
---

# Start the workshop

Get the participant from a fresh clone to their first `/sdlc:spec` in about ten minutes. Be
brief and friendly. Do one step at a time, and fix problems before moving on. Never commit
or push in this skill.

## 0. The right folder

Everything in this exercise runs from `exercises/02-sdlc-loop`. Check that `app.py` and
`FEATURES.md` are in the current directory. If they aren't, tell the participant to quit,
`cd exercises/02-sdlc-loop`, and start Claude Code again there.

## 1. The SDLC kit

Check whether the agentic-sdlc commands are installed:

```bash
claude plugin list 2>/dev/null | grep -E '(^|[^-[:alnum:]])sdlc@haco29' \
  || ls ~/.claude/commands/spec.md ~/.cursor/commands/spec.md 2>/dev/null
```

- Found: say so and move on.
- Not found: show the install commands from WORKSHOP.md step 2. Offer to run
  `claude plugin marketplace add haco29/agentic-sdlc` and
  `claude plugin install sdlc@haco29` for them, and only run them on a yes. Remind
  them to restart Claude Code afterwards and to check that `/sdlc:spec` shows up when they type
  `/sdlc`.

## 2. Git

```bash
git config user.name; git config user.email
```

Both must print something, or `/sdlc:build` can't commit. If either is empty, ask for the name
and email they want on their commits, and run `git config --global user.name "…"` and
`git config --global user.email "…"` only after they answer.

Check where `origin` points: `git remote get-url origin`. If it is `haco29/sdlc-workshop` itself
and `gh auth status` succeeds, suggest `gh repo fork --remote`, so `/sdlc:pr` can open a real
pull request in their fork; run it only after they agree. No `gh` or no GitHub: that's fine,
`/sdlc:pr` writes `pr.md` instead.

## 3. Python and tests

```bash
uv --version
uv run pytest -q
uv run ruff check .
```

uv brings its own Python and creates the environment in this folder; never create or
activate a virtualenv by hand. If `uv` isn't found, send them to SETUP.md at the repo root.

Both must be green before anything changes. If something fails, help fix the environment;
don't touch the app's code.

## 4. Feature branch

Ask which feature they'll build (summarize the five in FEATURES.md in one line each, and
recommend #1 when the room builds the same thing). Run `git status` first: if exercise 1
left uncommitted changes, offer `git stash` and only run it on a yes, because `/sdlc:build auto`
needs a clean tree. Then:

```bash
git checkout main && git checkout -b feat/<short-name>
```

## 5. Hand off

Tell them:

- Run `uv run streamlit run app.py` once, to see the app they're changing.
- Their first command is `/sdlc:spec <the feature in a sentence>`, and it will grill them. The
  questions are the point.
- The loop and what to watch for at each step are in WORKSHOP.md step 5.
- `/sdlc-score` at the end grades how they worked.
