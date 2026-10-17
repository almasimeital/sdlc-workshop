# The SDLC workshop: your playbook

Today you'll add one small feature to this poll app. The feature is the excuse. The goal is
to **run the whole loop once, for real**, and to read what every step produces:

```text
/sdlc:spec  →  /sdlc:plan  →  /sdlc:build  →  /sdlc:test  →  /sdlc:review  →  /sdlc:code-simplify  →  /sdlc:pr
```

It doesn't matter whether you're backend, frontend or QA: everyone runs the same loop on
the same app.

> **Shortcut:** start Claude Code in this folder (`exercises/02-sdlc-loop`) and run
> **`/start-workshop`**. It checks your setup, makes your branch, and points you at a feature.

## You need

- Git, uv, Claude Code and the GitHub CLI, set up as in [SETUP.md](../../SETUP.md). uv brings
  its own Python, so you don't need to install it.
- Your own fork of this repo, made during setup with `gh repo fork`, so `/sdlc:pr` can open a
  real pull request. Forked in the browser, without `gh`? `/sdlc:pr` writes `pr.md`: push your
  branch and paste it into a pull request yourself. No GitHub? `pr.md` is your result.

## Step 1: Open the app

You forked and cloned this repo during setup. Coming from exercise 1? Quit Claude Code with `/exit`,
then go to this exercise's folder and check the tests:

```bash
cd ../02-sdlc-loop
uv run pytest -q              # green before you change anything
```

In a new terminal, go to the `sdlc-workshop` folder first, and use
`cd exercises/02-sdlc-loop` instead.

Cloned the original instead of forking? Run `gh repo fork --remote` here: it keeps your
folder and commits and points `origin` at your fork, so `/sdlc:pr` can open a pull request.

Everything from here on runs in `exercises/02-sdlc-loop`, and that's where you start Claude
Code: the agent's instructions for this app and `/start-workshop` live in this folder, and
the loop writes its artifacts to `sdlc/<branch>/` here.

```bash
claude
```

## Step 2: Install the SDLC kit (once)

In the Claude Code you just started:

```text
/plugin marketplace add haco29/agentic-sdlc
/plugin install sdlc@haco29
```

No GitHub on your network? Unzip the kit you got from the facilitator next to
`sdlc-workshop`, so the folder is named `agentic-sdlc`, and add it by path instead:

```text
/plugin marketplace add ../../../agentic-sdlc
/plugin install sdlc@haco29
```

Restart Claude Code and type `/sdlc`: you should see `/sdlc:spec`, `/sdlc:plan`, `/sdlc:build`,
`/sdlc:test`, `/sdlc:review`, `/sdlc:code-simplify` and `/sdlc:pr`. They carry the plugin's
name so they don't clash with Claude Code's own `/plan` and `/review`.

## Step 3: Make a feature branch

If `git status` still shows changes from exercise 1, run `git stash` first. `/sdlc:build auto`
needs a clean working tree.

```bash
git checkout -b feat/<short-name>      # e.g. feat/percentages
```

To see the app you're changing, open a second terminal, go to this exercise's folder as in
step 1, and run `uv run streamlit run app.py` (stop it with Ctrl+C).

Every artifact the loop writes goes to `sdlc/<your-branch>/`, so the branch matters. The
commands refuse to run on `main`.

## Step 4: Pick a feature

Open [FEATURES.md](FEATURES.md) and choose one. Small is the point.

## Step 5: Run the loop, one command at a time

Read what each command produces before you run the next one.

| Command | Produces | Watch for |
|---|---|---|
| `/sdlc:spec <feature>` | `spec.md` | It grills you, one question at a time. Answering well is the most valuable part of the day. |
| `/sdlc:plan` | `plan.md`, `todo.md` | Are the tasks small? Does each one name the test that proves it? |
| `/sdlc:build` | One task, one commit | Logic in `poll/core.py`. The failing test comes first. Run it once per task, or `/sdlc:build auto` for all of them. |
| `/sdlc:test` | Tests for the gaps | Every success criterion and edge case in the spec should map to a test. |
| `/sdlc:review` | `review.md` | A reviewer agent with fresh eyes. Read every finding, and decide fix or won't-fix. |
| `/sdlc:code-simplify` | A `refactor:` commit | Tests stay green the whole time. "Nothing to simplify" is a fine answer. |
| `/sdlc:pr` | A PR, or `pr.md` | It checks six gates first. A failing gate means a draft, not a ready PR. |

## Step 6: Score yourself

```text
/sdlc-score
```

It reads your artifacts, commits, tests and PR, and grades **how you worked** out of 100,
with the three things to do differently next time. Not how clever the feature is.

## Step 7: Debrief

- What did `/sdlc-score` take points off for?
- Where did the `/sdlc:spec` grilling change what you were going to build?
- Which `/sdlc:review` axis found the most?
- Same feature, different roles: how did your specs and tests differ?
- What would you change in the process itself?

## Tips

- Trust the process even when a step feels like overkill for a small feature. That's the
  muscle we're building.
- Stuck? The goal is a complete loop, not a perfect feature. Ask a facilitator.
- Dummy data only.
