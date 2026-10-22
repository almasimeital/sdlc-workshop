"""Poll logic as plain functions over plain data.

Nothing here touches files or Streamlit. That's what makes it easy to test: every
function takes a poll and returns a value or a new poll.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import TypedDict

UTC_PLUS_3 = timezone(timedelta(hours=3))


class Poll(TypedDict):
    question: str
    options: list[str]
    votes: dict[str, int]


def create_poll(question: str, options: list[str]) -> Poll:
    """Return a new poll with zero votes. Surrounding whitespace and blank options are dropped."""
    question = question.strip()
    cleaned = [option.strip() for option in options if option.strip()]
    if not question:
        raise ValueError("A poll needs a question.")
    if len(cleaned) < 2:
        raise ValueError("A poll needs at least two options.")
    if len(set(cleaned)) != len(cleaned):
        raise ValueError("Options must be unique.")
    return {"question": question, "options": cleaned, "votes": {option: 0 for option in cleaned}}


def vote(poll: Poll, option: str) -> Poll:
    """Return a copy of the poll with one more vote for `option`."""
    if option not in poll["votes"]:
        raise ValueError(f"Unknown option: {option!r}")
    votes = {**poll["votes"], option: poll["votes"][option] + 1}
    return {**poll, "votes": votes}


def tally(poll: Poll) -> list[tuple[str, int]]:
    """Vote counts per option, in the order the options were created."""
    return [(option, poll["votes"][option]) for option in poll["options"]]


def total_votes(poll: Poll) -> int:
    return sum(poll["votes"].values())


class Result(TypedDict):
    option: str
    votes: int
    percent: int


def results(poll: Poll) -> list[Result]:
    """Each option's votes and whole-number share of the total, in creation order.

    Shares round half up (12.5% is 13%) and aren't adjusted to add up to 100%.
    """
    total = total_votes(poll)
    return [
        {"option": option, "votes": votes, "percent": (votes * 200 + total) // (2 * total)}
        for option, votes in tally(poll)
    ]


COLORS = ["blue", "red", "green", "orange", "violet", "yellow", "gray"]
COLOR_SPELLINGS = {"purple": "violet", "grey": "gray"}


def _named_color(option: str) -> str | None:
    name = option.strip().lower()
    name = COLOR_SPELLINGS.get(name, name)
    return name if name in COLORS else None


def option_colors(poll: Poll) -> dict[str, str]:
    """A color name per option.

    An option named after a color gets that color, once. The others take the colors
    left free, in creation order, and start over from the first color when they run out.
    """
    colors: dict[str, str] = {}
    for option in poll["options"]:
        named = _named_color(option)
        if named and named not in colors.values():
            colors[option] = named

    free = [color for color in COLORS if color not in colors.values()] or COLORS
    others = [option for option in poll["options"] if option not in colors]
    for i, option in enumerate(others):
        colors[option] = free[i % len(free)]

    return {option: colors[option] for option in poll["options"]}


def local_time_label(now: datetime) -> str:
    """`now` as a date and time in UTC+3, like "22 Oct 2026, 10:05:09 (UTC+3)"."""
    return f"{now.astimezone(UTC_PLUS_3):%d %b %Y, %H:%M:%S} (UTC+3)"
