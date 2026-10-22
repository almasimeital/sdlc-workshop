# Spec: Vote share and leader

Status: Approved (2026-10-22)

## Objective

Everyone watching the poll can see, at a glance, each option's share of the vote and which
option is leading, without reading bar heights off the chart.

## Scope

In scope:
- A results list under the bar chart, one line per option, like `🏆 Pizza: 5 votes (42%)`.
- Each option's name in its chart color, so a line matches its bar.
- The 🏆 icon on the leading option (or options, on a tie).
- The share and leader logic as a pure function in `poll/core.py`, tested first in
  `tests/test_core.py`; `app.py` only renders it.

Out of scope:
- Any change to the bar chart (no labels or tooltip changes).
- Sorting the list by votes.
- Forcing the percentages to add up to exactly 100%.
- Decimal percentages.
- Showing shares or the icon in the voting radio.
- Any change to how voting, creating or resetting a poll works.

## Success criteria

1. Given a poll with votes, when the results are computed, then each option gets a
   whole-number percentage equal to its votes / total votes × 100, rounded half up
   (e.g. 1 of 8 = 12.5% → 13%).
2. Given three options with one vote each, then each shows 33% and the total is 99%; the
   shares are not adjusted to sum to 100%.
3. Given a poll with zero votes, then every option shows `0 votes (0%)` and no option is
   marked as the leader.
4. Given a single option with the most votes, then only that option is marked with 🏆.
5. Given two or more options tied for the most votes (e.g. 3 / 3 / 1), then every tied
   option is marked with 🏆 and the others are not.
6. The results are listed in the order the options were created, whatever the vote counts.
7. The computation does not mutate the poll it is given.
8. In the app, the results list appears under the chart, one line per option in the format
   `🏆 <option>: <n> votes (<p>%)` (no 🏆 for non-leaders), with the option name in its
   chart color.

## Edge cases and decisions

| Case | Decision | Why |
|---|---|---|
| Where the shares appear | A text list under the chart; chart unchanged | Easy to read and to test through `poll.core`; the radio is for voting |
| Rounding | Whole numbers, round half up (12.5% → 13%) | Simple and honest; Python's banker's rounding would show 12%, which looks like a bug |
| Shares don't sum to 100% | Allowed (99% or 101%) | Forcing 100% favors one option for no visible reason |
| Zero votes | Every option `0 votes (0%)`, no 🏆 | Nobody leads yet; the list keeps the same shape before and after the first vote |
| Tie for the lead | Every tied leader gets 🏆 | Picking one would be arbitrary and look unfair |
| Order | Creation order, same as the chart | Lines align with bars and don't jump around as votes arrive |
| The "special icon" | 🏆 | Agreed in the grilling |
| Singular "vote" | Out of scope; always "votes" | Matches the existing "N votes so far" caption |

## Open questions

- None.

## Decisions

- None needing an ADR.
