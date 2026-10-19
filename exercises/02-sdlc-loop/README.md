# 🗳️ Live Poll: SDLC workshop starter

A tiny Streamlit app: create a poll, vote, and watch the results. It exists so a whole
room, backend, frontend and QA alike, can practice the same agentic SDLC end to end by
adding one small feature:

```text
/sdlc:spec  →  /sdlc:plan  →  /sdlc:build  →  /sdlc:test  →  /sdlc:review  →  /sdlc:code-simplify  →  /sdlc:pr
```

> **Running the workshop?** Read [WORKSHOP.md](WORKSHOP.md), or start Claude Code in this
> folder and run **`/start-workshop`**. The features to build are in [FEATURES.md](FEATURES.md).
> When you're done, **`/sdlc-score`** grades how closely you followed the loop.

The commands come from the [agentic-sdlc](https://github.com/haco29/agentic-sdlc) plugin.

## Quick start

From this folder, `exercises/02-sdlc-loop`:

```bash
uv run python -m pytest -q              # should be green
uv run python -m streamlit run app.py   # opens the poll in your browser
```

Votes are stored in a local `poll.json`. **Reset poll** starts over.

## Layout

```text
app.py               Streamlit view. Thin: load state, call poll.core, render.
poll/core.py         Pure poll logic: create, vote, tally. No I/O.
poll/store.py        Load and save poll.json. The only module that touches the disk.
tests/test_core.py   Tests for the logic: your TDD template.
tests/test_store.py  Tests for saving and loading.
tests/test_app.py    A smoke test that the UI is wired to the logic.
CLAUDE.md            The conventions the agent follows in this repo.
```

**The important idea:** a feature's logic goes in `poll/core.py` as plain functions over
plain data. That's what makes it testable. Test it with `uv run python -m pytest`, then wire
it into `app.py`.

## Checks

```bash
uv run python -m pytest -q
uv run python -m ruff check .
```

## License

MIT
