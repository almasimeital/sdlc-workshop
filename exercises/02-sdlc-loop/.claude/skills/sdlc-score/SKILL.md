---
name: sdlc-score
description: Scores how well a workshop participant followed the agentic SDLC loop on their feature branch, out of 100. Grades artifacts, command coverage, loop order, TDD evidence, code placement, and review/simplify/PR discipline from the evidence in the repo, then names the top three things to do differently. Use when the user runs /sdlc-score or asks to grade or score their workshop run.
disable-model-invocation: true
---

# Score the SDLC run

Grade **how they worked**, not how clever the feature is. The rules being scored are the
agentic-sdlc kit's artifacts and gates: `sdlc/<branch>/spec.md`, `plan.md` (with command
coverage and test evidence), `todo.md`, `review.md`, and the PR or `pr.md`.

**Tone:** a workshop scorecard, not a performance review. Be honest, because an inflated
score teaches nothing, but be specific and encouraging. Every lost point comes with the
concrete thing to do differently.

## Step 1: Gather evidence before scoring anything

```bash
BRANCH=$(git rev-parse --abbrev-ref HEAD)
BASE=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null || echo main)
FORK=$(git merge-base HEAD "$BASE")
git log --reverse --format='%h %ad %s' --date=format:'%H:%M' "$FORK..HEAD" --stat
git diff --stat "$FORK..HEAD"
ls -R "sdlc/$BRANCH" 2>/dev/null
```

- On `main`: stop and ask them to check out their feature branch. There's nothing to score.
- Read every file in `sdlc/$BRANCH/`. Note anything missing.
- Read the code diff: what changed in `poll/core.py`, `app.py` and `tests/`.
- Run `uv run python -m pytest -q` and `uv run python -m ruff check .` yourself. Never take "it's green" on faith.
- Look for the PR: `gh pr view --json number,url,isDraft,baseRefName,body 2>/dev/null`,
  else `sdlc/$BRANCH/pr.md`.

## Step 2: Score

Award partial credit. Cite the evidence (a commit, a `file:line`, a command result) for
every line.

### A. Artifacts (25)

| Points | Check |
|---|---|
| 10 | `spec.md` is specific to this feature (no template text), has numbered testable success criteria, records the edge-case decisions, and is `Status: Approved`. A draft or generic spec: about 4. |
| 8 | `plan.md` has small vertical tasks, each with acceptance criteria and the test that proves it. |
| 7 | `todo.md` mirrors the plan, and its ticks match what was really built. |

### B. Command coverage (15)

2.5 points per line of the coverage checklist in `plan.md` (`/sdlc:spec` to `/sdlc:code-simplify`).
A tick is a claim, so look for the evidence:

| Line | Evidence |
|---|---|
| `/sdlc:spec` | an approved, feature-specific `spec.md` |
| `/sdlc:plan` | `plan.md` and `todo.md` with real tasks |
| `/sdlc:build` | implementation commits, and ticks in `todo.md` |
| `/sdlc:test` | tests added in the diff, and a green suite now |
| `/sdlc:review` | `review.md` with a status per finding, and fix commits after it |
| `/sdlc:code-simplify` | a `refactor:` commit with no test changes, or a recorded "nothing to simplify" |

- Ticked with evidence: 2.5. Ticked with no evidence: 0, and say which.
- `skipped: <reason>` with a sensible reason: 1.5. Done but not ticked: 1.5 (the `/sdlc:pr`
  gate needs the tick).
- No coverage section at all: score from the evidence alone, at most 7.5.

### C. Loop order (15)

From the commit order:

- 15: the spec commit comes before the plan commit, which comes before the first code commit.
- 8: mostly in order, with one artifact committed late.
- 3: code first, with the artifacts written afterwards.
- Artifacts never committed: at most 5, and tell them the history can't show the order.

### D. TDD evidence (20)

| Points | Check |
|---|---|
| 8 | New behavior in `poll/core.py` has tests in `tests/`. |
| 6 | Tests came first: RED entries in Test evidence before GREEN, or tests in the same commit as the code, never in a later "add tests" commit. |
| 4 | The spec's edge cases are tested (zero votes, ties, a closed poll, duplicates: whatever the feature implies), not just the happy path. |
| 2 | `uv run python -m pytest -q` and `uv run python -m ruff check .` pass now. |

### E. Code placement (10)

- 6: the feature's logic is in `poll/core.py` as pure functions over plain data.
- 4: `app.py` stayed thin: wiring and rendering, no business rules.

Logic leaking into `app.py` is the most common miss. Point at the exact `file:line`.

### F. Review, simplify and PR (15)

| Points | Check |
|---|---|
| 5 | `review.md` exists, every finding has a status, and the fixes are in commits after it. |
| 4 | A behavior-preserving `refactor:` commit with tests green, or "nothing to simplify" recorded. |
| 6 | A ready PR, or a `pr.md` whose gates all pass, with the gate table and test evidence in the body: 6. GitHub is optional, so `pr.md` alone loses nothing. A draft PR, or a `pr.md` with a failing gate: 4. Neither: 0. |

## Step 3: Report

```markdown
## SDLC score: NN / 100

| Category | Score | Evidence |
|---|---|---|
| A. Artifacts | x / 25 | ... |
| B. Command coverage | x / 15 | ... |
| C. Loop order | x / 15 | ... |
| D. TDD evidence | x / 20 | ... |
| E. Code placement | x / 10 | ... |
| F. Review, simplify, PR | x / 15 | ... |

### Do differently next time
1. ...
2. ...
3. ...

### What went well
- ...
```

Keep the three "do differently" items concrete enough to act on in the next ticket.
