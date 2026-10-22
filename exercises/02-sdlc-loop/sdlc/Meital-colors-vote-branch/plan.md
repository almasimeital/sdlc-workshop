# Plan: Vote share and leader

Spec: [spec.md](spec.md)

## Approach

The rules (percentages, rounding, who leads) are business logic, so they live in
`poll/core.py` as one pure function next to `tally`:

```python
class Result(TypedDict):
    option: str
    votes: int
    percent: int
    leader: bool

def results(poll: Poll) -> list[Result]: ...
```

- Creation order comes from `poll["options"]`, like `tally`.
- Round half up with integer arithmetic, `(votes * 200 + total) // (2 * total)`, so there are
  no float surprises and no banker's rounding (`round(12.5) == 12`).
- `leader` is true for every option with the top count, and false for all of them when
  there are no votes.
- Builds a new list, and doesn't touch the poll.

`app.py` only renders: under the chart, one `st.markdown` line per result, like
`🏆 :{color}[{option}]: {votes} votes ({percent}%)`, using the existing `option_colors`. It uses
`st.markdown`, not `st.caption`, so the existing `app.caption[0]` "N votes so far" checks keep
pointing at the same element.

No new dependencies, no storage changes.

**Pie chart (spec revision, criteria 9–12).** No new rules, so `poll/core.py` doesn't change:
the pie is drawn in `app.py` from the same `results(poll)` the list uses. It's an Altair
`mark_arc` (theta = votes) layered with a `mark_text` that shows `{percent}%`, using the
same `color_scale` as the bar chart and a tooltip of option, votes and percent. It is
rendered between the bar chart and the list, and only `if total_votes(poll)`. Slices with 0
votes get no text label, because they have no visible slice and a stray `0%` would sit at
the edge of a neighbor.

## Tasks

### Task 1: Each option's rounded share of the vote

- Acceptance criteria: spec #1 (whole percentages, rounded half up), #2 (33/33/33 = 99%,
  not adjusted).
- Test that proves it: in `tests/test_core.py`, written first:
  `test_results_give_each_option_its_rounded_share` (2 of 3 → 67%),
  `test_half_a_percent_rounds_up` (1 of 8 → 13%),
  `test_shares_are_not_forced_to_add_up_to_100`.
- Files: `poll/core.py`, `tests/test_core.py`.

### Task 2: No votes, creation order, poll unchanged

- Acceptance criteria: spec #3 percentage part (zero votes → 0%, no division by zero),
  #6 (creation order), #7 (poll not mutated).
- Test that proves it: in `tests/test_core.py`, written first:
  `test_results_with_no_votes_are_all_zero_percent` (red until the zero guard exists),
  `test_results_keep_the_creation_order`, `test_results_do_not_change_the_poll`. The last two
  may already pass after Task 1; they stay as guards, and the build log says so.
- Files: `poll/core.py`, `tests/test_core.py`.

### Task 3: Mark the leader, including ties

- Acceptance criteria: spec #3 leader part (zero votes → no leader), #4 (single leader only),
  #5 (all tied leaders, and only them).
- Test that proves it: in `tests/test_core.py`, written first:
  `test_the_option_with_most_votes_leads`, `test_every_option_tied_for_the_lead_leads`,
  `test_nobody_leads_a_poll_with_no_votes`.
- Files: `poll/core.py`, `tests/test_core.py`.

### Task 4: Show the results list under the chart

- Acceptance criteria: spec #8 (list under the chart, `🏆 <option>: <n> votes (<p>%)`
  format, name in its chart color).
- Test that proves it: in `tests/test_app.py` (wiring only):
  `test_results_list_shows_shares_and_the_leader`, which votes 2/1/0 on Red/Blue/Green and
  checks for the markdown lines `🏆 :red[Red]: 2 votes (67%)`, `:blue[Blue]: 1 votes (33%)` and
  `:green[Green]: 0 votes (0%)`.
- Files: `app.py`, `tests/test_app.py`.
- Manual check: refresh the running app and vote a few times, including a tie.

Checkpoint after Task 4: both checks green (`uv run python -m pytest -q`,
`uv run python -m ruff check .`) and the app looks right in the browser.

### Task 5: Rounding guards from the test pass

- Acceptance criteria: spec #1 (29 of 200 → 15%, no float error), #2 (1 / 1 / 6 → 13 / 13 /
  75, a 101% total).
- Test that proves it: in `tests/test_core.py`:
  `test_an_exact_half_percent_rounds_up_without_float_error` (29 / 171 → `[15, 86]`),
  `test_shares_may_add_up_to_more_than_100` (`[13, 13, 75]`). The code is already correct,
  so these will pass on first run. They are guards against a float or "force 100%" rewrite,
  and the log says so. To show they test something, temporarily swap in the float formula,
  watch the first one fail, then put the integer formula back.
- Files: `tests/test_core.py`.

### Task 6: Results list wiring gaps

- Acceptance criteria: spec #3 in the UI (zero-vote lines, no 🏆), #5 in the UI (both tied
  leaders get 🏆), #8 (name in its chart color when names aren't colors).
- Test that proves it: in `tests/test_app.py` (wiring only):
  `test_results_list_before_and_after_the_first_vote` on Pizza / Sushi: first
  `[":blue[Pizza]: 0 votes (0%)", ":red[Sushi]: 0 votes (0%)"]`, then after one Sushi vote
  `[":blue[Pizza]: 0 votes (0%)", "🏆 :red[Sushi]: 1 votes (100%)"]`, and
  `test_every_tied_leader_gets_the_trophy` (Pizza / Sushi / Salad with one vote each for Pizza
  and Sushi). These may already pass, and are kept as guards.
- Files: `tests/test_app.py`.

### Task 7: Pie chart under the bar chart

- Acceptance criteria: spec #9 (bar, pie, list, caption order), #10 (slice colors and
  percent labels match the list), #11 (tooltip has option, votes and percent).
- Test that proves it: in `tests/test_app.py`, written first:
  `test_a_pie_chart_shows_each_options_share` (votes 2 / 1 / 0 on Red / Blue / Green: a second
  `vega_lite_chart` exists, is an arc, uses the same color domain and range as the bars,
  labels read `67%` and `33%` with no `0%`, and the tooltip fields are option, votes and
  percent), and `test_the_page_reads_bar_chart_pie_list_caption` (element order in
  `app.main`).
- Files: `app.py`, `tests/test_app.py`.

### Task 8: No pie chart before the first vote

- Acceptance criteria: spec #12 (zero votes: no pie and no placeholder, while the bar chart
  and list still show).
- Test that proves it: in `tests/test_app.py`, written first:
  `test_no_pie_chart_before_the_first_vote` (a fresh poll has exactly one `vega_lite_chart`,
  plus the zero-vote list lines). Red against a pie that always renders, if Task 7 draws it
  unconditionally; otherwise this is a guard, and the log says so.
- Files: `app.py`, `tests/test_app.py`.
- Manual check: refresh http://localhost:8503 and look at a fresh poll, one vote, and a tie.

Checkpoint after Task 8: both checks green, and the page reads bar, pie, list, caption in the
browser.

## Risks

- **Float rounding.** `votes / total * 100` can land just under a half (for example
  `0.285 * 100`). Integer arithmetic avoids that, and the 1-of-8 test catches a regression.
- **Shares that total 99% or 101% look like a bug to viewers.** This is accepted by the
  spec, and the 33/33/33 test pins it down so nobody "fixes" it later.
- **Option names containing Markdown** (`*`, `[`, `]`) could render oddly. The voting radio
  already has the same behavior, so this is out of scope; flag it in review if it shows up.
- **App tests find elements by position.** The clock is also markdown, so the app test looks
  for the result lines by content, not by index.
- **Two charts on the page.** Existing app tests read `app.get("vega_lite_chart")[0]` and
  expect it to be the bar chart. Because the pie is rendered after the bar chart, index 0
  stays the bar chart; Task 7's order test pins that down.
- **Reading element order in `AppTest`.** Walking `app.main` in document order is less
  common than filtering by type. If it turns out to be awkward, fall back to comparing the
  positions of the chart and markdown elements, and note it in the log.
- **Pie looks empty on a single vote.** One option with 100% is a full circle with one
  `100%` label. That's correct, and the manual check covers it.

## SDLC command coverage

- [x] /sdlc:spec
- [x] /sdlc:plan
- [x] /sdlc:build
- [x] /sdlc:test (12 criteria and 12 decisions mapped by the test-engineer agent; 3 pie gaps closed: labels tied to `results()`, pie colors for non-color names, no placeholder at zero votes. Earlier pass: 6 gaps, closed by tasks 5–8)
- [x] /sdlc:review (10 findings: 6 fixed (I1, S1, S2, N1; S4, S5 in /sdlc:code-simplify), 4 won't fix (S3, S6, N2, N3))
- [x] /sdlc:code-simplify (2 simplifications in `app.py`: results computed once, pie rows as named dicts; no test changed)

## Test evidence

Times marked `~` are estimates. Times without `~` on GREEN and gate lines come from a `date` run right after the command; times on RED and mutation lines before 12:19 were estimated too, within a few minutes.

- 2026-10-22 10:59 · task 1 RED · `uv run python -m pytest tests/test_core.py -q` → collection error: `ImportError: cannot import name 'results' from 'poll.core'` (expected, function doesn't exist)
- 2026-10-22 11:00 · task 1 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 39 passed, all checks passed
- 2026-10-22 11:01 · task 2 RED · `uv run python -m pytest tests/test_core.py -q` → 1 failed, 25 passed: `test_results_with_no_votes_are_all_zero_percent` raised `ZeroDivisionError` (expected). `test_results_keep_the_creation_order` and `test_results_do_not_change_the_poll` passed on first run, as the plan predicted; kept as guards
- 2026-10-22 11:02 · task 2 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 42 passed, all checks passed
- 2026-10-22 11:05 · task 3 RED · `uv run python -m pytest tests/test_core.py -q` → 5 failed, 24 passed: the 3 new leader tests plus the 2 whole-dict tests from tasks 1–2 (updated to include `leader`) all raised `KeyError: 'leader'` (expected)
- 2026-10-22 11:06 · task 3 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 45 passed, all checks passed
- 2026-10-22 11:07 · task 4 RED · `uv run python -m pytest tests/test_app.py -q -k results_list` → 1 failed: `assert [] == ['🏆 :red[Red]: 2 votes (67%)', ...]`, no result lines on the page (expected)
- 2026-10-22 11:08 · task 4 first full run · `uv run python -m pytest -q && uv run python -m ruff check .` → 5 failed, 41 passed; ruff F811. The chart's `results` DataFrame in `app.py` shadowed the imported `results()` (`'DataFrame' object is not callable`). Fixed by renaming the DataFrame to `chart_data`
- 2026-10-22 11:09 · task 4 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 46 passed, all checks passed
- 2026-10-22 11:22 · task 5 guards · `uv run python -m pytest tests/test_core.py -q -k "float_error or more_than_100"` → 2 passed on first run (expected: code already correct)
- 2026-10-22 11:23 · task 5 mutation check · temporarily replaced the integer formula with `int(votes / total * 100 + 0.5)`; `uv run python -m pytest tests/test_core.py -q` → 1 failed, 30 passed: `test_an_exact_half_percent_rounds_up_without_float_error` got `[14, 86]` (only the new test caught it). Integer formula restored; `git diff poll/core.py` empty
- 2026-10-22 11:24 · task 5 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 48 passed, all checks passed
- 2026-10-22 11:25 · task 6 guards · `uv run python -m pytest tests/test_app.py -q -k "results_list or tied_leader"` → 3 passed on first run (expected: view already correct)
- 2026-10-22 11:25 · task 6 mutation check · temporarily colored names with `option.lower()` instead of `colors[option]`; same command → 2 failed, 1 passed: both new tests failed, while the old Red/Blue/Green test still passed (the gap they close). Restored; `git diff app.py` empty
- 2026-10-22 11:25 · task 6 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 50 passed, all checks passed
- 2026-10-22 11:26 · task 7 RED · `uv run python -m pytest tests/test_app.py -q -k "pie_chart_shows or bar_chart_pie"` → 2 failed: `IndexError` (no second chart) and outline `['bar', 'line', 'line', 'caption']` instead of `['bar', 'arc', 'line', 'line', 'caption']` (expected)
- 2026-10-22 11:28 · task 7 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 52 passed, all checks passed; 104 warnings, all Altair `UserWarning: I don't know how to infer vegalite type from 'empty'`, from the pie being drawn with no data before the first vote. Task 8 removes that case
- 2026-10-22 11:29 · task 8 RED · `uv run python -m pytest tests/test_app.py -q -k "no_pie_chart"` → 1 failed: outline `['bar', 'arc', 'line', 'line', 'caption']`, an empty pie drawn before any vote (expected)
- 2026-10-22 11:29 · task 8 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 53 passed, 0 warnings, all checks passed
- 2026-10-22 11:35 · /sdlc:pr gate G4 · `uv run python -m pytest -q && uv run python -m ruff check .` → 53 passed, all checks passed (gates G5, G6 failed; user chose to fix first)
- 2026-10-22 11:40 · /sdlc:test gap tests · `uv run python -m pytest tests/test_app.py -q -k "same_percentages or not_color_names or no_pie_chart"` → 4 passed on first run (no bugs: code already correct)
- 2026-10-22 11:41 · /sdlc:test mutation checks · (a) pie labels from `round(votes / total * 100)` → `test_pie_labels_use_the_same_percentages_as_the_list` failed `['12%', '88%'] == ['13%', '88%']`; (b) `st.markdown("No votes yet")` at zero votes → `test_no_pie_chart_before_the_first_vote` failed `['No votes yet'] == []`; (c) pie colors looked up by option name → `test_pie_colors_match_the_bars_when_options_are_not_color_names` failed while the Red/Blue/Green pie test passed. All restored; `git diff app.py` empty
- 2026-10-22 11:42 · /sdlc:test GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 55 passed, all checks passed

- 2026-10-22 11:59 · /sdlc:pr gate G4 · `uv run python -m pytest -q && uv run python -m ruff check .` → 55 passed, all checks passed
- 2026-10-22 ~12:19 · review I1 RED · `uv run python -m pytest tests/test_app.py -q -k "markdown_in_option"` → 1 failed: `'Fish_and_chips_?' == 'Fish\_and\_chips\_?'`, question rendered unescaped (expected)
- 2026-10-22 12:20 · review I1 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 56 passed, all checks passed
- 2026-10-22 ~12:21 · review S1 guard · `uv run python -m pytest tests/test_app.py -q -k "every_core_color"` → 1 passed on first run (tables are in sync today). Mutation check: added `"pink"` to `COLORS` → 1 failed with `KeyError: 'pink'` from `BAR_COLORS`; restored, `git diff poll/core.py` empty
- 2026-10-22 ~12:21 · review S1 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 57 passed, all checks passed
- 2026-10-22 ~12:22 · review S2 · added `altair>=5` to `pyproject.toml`; `uv lock` → resolved 53 packages, only the direct-dependency entry added (pinned altair 6.2.2 / 6.3.0 unchanged); `uv run python -m pytest -q && uv run python -m ruff check .` → 57 passed, all checks passed
- 2026-10-22 ~12:22 · review N1 RED · `uv run python -m pytest tests/test_app.py -q -k "pie_chart_shows"` → 1 failed: tooltip `('Percent', None) != ('Label', 'Percent')` (expected)
- 2026-10-22 12:22 · review N1 GREEN · `uv run python -m pytest -q && uv run python -m ruff check .` → 57 passed, all checks passed
- 2026-10-22 12:24 · /sdlc:code-simplify · started green (57 passed); after each of 2 simplifications (S4 `poll_results` computed once, S5 pie rows built as named dicts) `uv run python -m pytest -q && uv run python -m ruff check .` → 57 passed, all checks passed; no test edited
