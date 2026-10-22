# Review: Vote share and leader

Reviewer: `sdlc:code-reviewer` agent, fresh context, on `git diff $(git merge-base HEAD main)`
plus `spec.md` and `plan.md`. Date: 2026-10-22.

Verdict: **Approve**, once I1 is fixed or accepted as a known risk. All 12 spec criteria are met,
nothing outside the spec's scope was added after it was written, and `uv run python -m pytest -q`
(55 passed) and `uv run python -m ruff check .` (clean) pass.

Findings marked *(761e2f3)* come from the earlier colors and clock commit, which predates this
spec.

| ID | Severity | Axis | Where | Finding | Fix | Status |
|---|---|---|---|---|---|---|
| I1 | Important | Security, correctness | `app.py:110`, `app.py:65` *(radio: 761e2f3)* | Option names go into `:{color}[{option}]` markdown without escaping: `_`, `*`, `]` and `$` mangle the text, and `![x](https://…)` loads an outside image for every viewer. It isn't XSS, because Streamlit blocks raw HTML. | Escape the markdown characters in option names (and the question) before rendering, with an app wiring test using a name like `a]b` | fixed: `plain()` in `app.py` escapes the question, radio labels and result lines; `test_markdown_in_option_names_and_the_question_shows_as_plain_text` |
| S1 | Suggestion | Architecture | `app.py:21-29` *(761e2f3)* | `BAR_COLORS` must match `core.COLORS` by hand. A new color in core crashes the page with `KeyError`, and no test catches it. | Test that `set(BAR_COLORS) == set(COLORS)` | open |
| S2 | Suggestion | Architecture | `app.py:5`, `pyproject.toml` | `altair` is imported directly but only arrives as a Streamlit dependency, and `alt.Theta` needs altair 4.2 or later | Add `altair>=5` to `dependencies` | open |
| S3 | Suggestion | Correctness | `poll/core.py:12` *(761e2f3)* | The clock is fixed at UTC+3. If it's meant to be Israel time, it will be an hour off after daylight saving ends (about 2026-10-25). The label says "(UTC+3)", so it is never false. | Use `ZoneInfo("Asia/Jerusalem")` plus `tzdata`, or rename the function to `utc_plus_3_label` | open |
| S4 | Suggestion | Performance, readability | `app.py:94`, `app.py:107` | `results(poll)` runs twice and `total_votes` three times per rerun. The cost is trivial; the real point is that one call makes it obvious the pie and the list share numbers. | Compute `poll_results = results(poll)` once and reuse it | open |
| S5 | Suggestion | Readability | `app.py:91-98` | The 4-tuple comprehension that builds `pie_data` is hard to read | Build rows as dicts with named keys, or use `DataFrame(...).assign(Label=…)` | open |
| S6 | Suggestion | Process | *(761e2f3)* | The colors and clock commit has no spec, and its tests landed with the code, so there's no evidence they came first | No code change; say so in the PR description | open |
| N1 | Nit | Readability | `app.py:103` | The tooltip shows `Percent: 67` without `%` | `alt.Tooltip("Label", title="Percent")` | open |
| N2 | Nit | Accessibility | *(761e2f3)* | Yellow (`#faca2b`) text is hard to read on a light background | Out of this spec's scope; a possible follow-up | open |
| N3 | Nit | Correctness | `poll/core.py:66` | `max()` would raise on an empty votes dict. `create_poll` makes that impossible. | Add a comment, or leave it | open |

## Red Queen: proposed rules (not applied)

| Finding | Proposed rule | Where |
|---|---|---|
| I1 | "User-supplied text (questions, option names) passed to `st.markdown` or a markdown-aware widget must be escaped." | `CLAUDE.md`, Conventions |
| S1 | "A view-side lookup keyed by a core constant needs a test that the keys stay in sync." | `CLAUDE.md`, Conventions |
| S2 | "Every module you import directly is listed in `pyproject.toml`." | `CLAUDE.md`, Checks |
