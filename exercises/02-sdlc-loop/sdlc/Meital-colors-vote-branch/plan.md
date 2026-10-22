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

## Risks

- **Float rounding.** `votes / total * 100` can land just under a half (for example
  `0.285 * 100`). Integer arithmetic avoids that, and the 1-of-8 test catches a regression.
- **Shares that total 99% or 101% look like a bug to viewers.** This is accepted by the
  spec, and the 33/33/33 test pins it down so nobody "fixes" it later.
- **Option names containing Markdown** (`*`, `[`, `]`) could render oddly. The voting radio
  already has the same behavior, so this is out of scope; flag it in review if it shows up.
- **App tests find elements by position.** The clock is also markdown, so the app test looks
  for the result lines by content, not by index.

## SDLC command coverage

- [x] /sdlc:spec
- [x] /sdlc:plan
- [ ] /sdlc:build
- [ ] /sdlc:test
- [ ] /sdlc:review
- [ ] /sdlc:code-simplify

## Test evidence

