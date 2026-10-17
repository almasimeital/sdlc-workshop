# Agentic engineering workshop: exercises

Hands-on exercises for the agentic engineering workshop. Each exercise is a small,
self-contained Python project in its own folder.

| # | Folder | Module | What you practice |
|---|---|---|---|
| 1 | [`exercises/01-agent-basics`](exercises/01-agent-basics) | 1 · Basics | Plain prompts, no skills: watch how an agent reasons, picks tools and checks its own work. |
| 2 | [`exercises/02-sdlc-loop`](exercises/02-sdlc-loop) | 2 · Agentic SDLC | One small feature through the whole loop, `/sdlc:spec` to `/sdlc:pr`, with the [agentic-sdlc](https://github.com/haco29/agentic-sdlc) kit. |

## Before you start

- **Set up first: [SETUP.md](SETUP.md).** Git, uv, Claude Code and the GitHub CLI, on Windows
  or macOS. uv brings its own Python. No GitHub account? SETUP.md shows the way without one.
- **Start Claude Code inside the exercise's folder**, not at the repo root. Exercise 2
  carries its own instructions for the agent. Exercise 1 deliberately has none, and
  neither does the root. For exercise 1, from the `sdlc-workshop` folder:

  ```bash
  cd exercises/01-agent-basics
  claude
  ```

- **Exercise 1 runs without the SDLC kit.** If you're doing both, do exercise 1 first and
  install the kit only when exercise 2 tells you to.

The prompts for exercise 1 are in [PROMPTS.md](PROMPTS.md). Open it in your browser or an
editor, not in Claude Code. Exercise 2 has its own playbook:
[WORKSHOP.md](exercises/02-sdlc-loop/WORKSHOP.md).

## Checks

```bash
cd exercises/<exercise>
uv run pytest -q
uv run ruff check .
```

Dummy data only, in every exercise.

## License

MIT
