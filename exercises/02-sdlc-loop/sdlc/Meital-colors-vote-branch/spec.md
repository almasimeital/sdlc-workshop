# Spec: Vote share and leader

Status: Approved (2026-10-22)

## Objective

Everyone watching the poll can see, at a glance, each option's share of the vote and which
option is leading, without reading bar heights off the chart: as a pie chart and as a
written list.

## Scope

In scope:
- A pie chart under the existing bar chart: one slice per option, in the option's chart
  color, labeled with its percentage; hovering shows the option, votes and percent.
- A results list under the pie chart, one line per option, like `🏆 Pizza: 5 votes (42%)`.
- Each option's name in its chart color, so a line matches its bar and slice.
- The 🏆 icon on the leading option (or options, on a tie).
- The share and leader logic as a pure function in `poll/core.py`, tested first in
  `tests/test_core.py`; `app.py` only renders it. The pie uses the same numbers.

Out of scope:
- Any change to the bar chart (no labels or tooltip changes).
- Putting the charts side by side.
- A legend, option names on the slices, a donut hole, animation, or a 🏆 on the pie.
- Sorting the list by votes.
- Forcing the percentages to add up to exactly 100%.
- Decimal percentages.
- Showing shares or the icon in the voting radio.
- Any change to how voting, creating or resetting a poll works.

## Success criteria

1. Given a poll with votes, when the results are computed, then each option gets a
   whole-number percentage equal to its votes / total votes × 100, rounded half up
   (e.g. 1 of 8 = 12.5% → 13%, 29 of 200 = 14.5% → 15%), with no float rounding error.
2. The shares are not adjusted to sum to 100%: three options with one vote each show 33%
   each (99%), and 1 / 1 / 6 votes show 13% / 13% / 75% (101%).
3. Given a poll with zero votes, then every option shows `0 votes (0%)` and no option is
   marked as the leader.
4. Given a single option with the most votes, then only that option is marked with 🏆.
5. Given two or more options tied for the most votes (e.g. 3 / 3 / 1), then every tied
   option is marked with 🏆 and the others are not.
6. The results are listed in the order the options were created, whatever the vote counts.
7. The computation does not mutate the poll it is given.
8. In the app, the results list shows one line per option in the format
   `🏆 <option>: <n> votes (<p>%)` (no 🏆 for non-leaders), with the option name in its
   chart color, also when option names are not color names.
9. Given at least one vote, the page shows, top to bottom: the bar chart, the pie chart, the
   results list, then the "N votes so far" caption.
10. Each pie slice has its option's chart color and is labeled with that option's percentage
    from criterion 1, the same number as in the list.
11. Hovering a slice shows the option, its votes and its percentage.
12. Given a poll with zero votes, no pie chart is shown, and no placeholder replaces it; the
    bar chart and the results list still show.

## Edge cases and decisions

| Case | Decision | Why |
|---|---|---|
| Where the shares appear | A pie chart and a text list, both under the bar chart; bar chart unchanged | The user wants both charts; the list keeps the 🏆 and exact numbers |
| Layout | Stacked: bar, pie, list, caption | The user prefers one after the other over side by side |
| Slice labels | The percentage only (`67%`); option, votes and percent on hover | Colors already match the bars and the list, so no legend or names needed |
| Pie numbers | The same rounded percentages as the list | The two must never disagree |
| Zero votes, pie | Not shown, no "No votes yet" note | A pie of nothing looks broken; the bar chart and list already show zeros |
| Zero votes, list | Every option `0 votes (0%)`, no 🏆 | Nobody leads yet; the list keeps the same shape before and after the first vote |
| Tie for the lead | Every tied leader gets 🏆 in the list; the pie marks nobody | Picking one would be arbitrary and look unfair |
| Rounding | Whole numbers, round half up (12.5% → 13%), integer arithmetic | Simple and honest; Python's banker's rounding would show 12%, and floats can land just under a half |
| Shares don't sum to 100% | Allowed (99% or 101%) | Forcing 100% favors one option for no visible reason |
| Order | Creation order, same as the bar chart | Lines align with bars and don't jump around as votes arrive |
| The "special icon" | 🏆 | Agreed in the grilling |
| Singular "vote" | Out of scope; always "votes" | Matches the existing "N votes so far" caption |

## Open questions

- None.

## Decisions

- None needing an ADR.
