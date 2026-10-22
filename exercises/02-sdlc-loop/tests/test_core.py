from datetime import datetime, timedelta, timezone

import pytest

from poll.core import COLORS, create_poll, local_time_label, option_colors, tally, total_votes, vote


def make_poll():
    return create_poll("Lunch?", ["Pizza", "Sushi", "Salad"])


def test_create_poll_starts_with_zero_votes():
    poll = make_poll()

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi", "Salad"]
    assert poll["votes"] == {"Pizza": 0, "Sushi": 0, "Salad": 0}


def test_create_poll_trims_whitespace_and_drops_blank_options():
    poll = create_poll("  Lunch?  ", [" Pizza ", "", "   ", "Sushi"])

    assert poll["question"] == "Lunch?"
    assert poll["options"] == ["Pizza", "Sushi"]


def test_create_poll_needs_a_question():
    with pytest.raises(ValueError, match="question"):
        create_poll("   ", ["Pizza", "Sushi"])


def test_create_poll_needs_two_options():
    with pytest.raises(ValueError, match="two options"):
        create_poll("Lunch?", ["Pizza", ""])


def test_create_poll_rejects_duplicate_options():
    with pytest.raises(ValueError, match="unique"):
        create_poll("Lunch?", ["Pizza", "Pizza"])


def test_vote_adds_one_vote_to_the_option():
    poll = vote(make_poll(), "Sushi")

    assert poll["votes"]["Sushi"] == 1
    assert poll["votes"]["Pizza"] == 0


def test_vote_leaves_the_original_poll_unchanged():
    original = make_poll()

    vote(original, "Pizza")

    assert original["votes"]["Pizza"] == 0


def test_vote_for_an_unknown_option_raises():
    with pytest.raises(ValueError, match="Unknown option"):
        vote(make_poll(), "Burgers")


def test_tally_keeps_the_order_options_were_created_in():
    poll = vote(vote(make_poll(), "Salad"), "Salad")

    assert tally(poll) == [("Pizza", 0), ("Sushi", 0), ("Salad", 2)]


def test_total_votes_counts_every_vote():
    poll = vote(vote(vote(make_poll(), "Pizza"), "Sushi"), "Pizza")

    assert total_votes(poll) == 3


def test_total_votes_is_zero_for_a_new_poll():
    assert total_votes(make_poll()) == 0


def test_option_colors_gives_each_option_its_own_color_in_order():
    assert option_colors(make_poll()) == {"Pizza": "blue", "Sushi": "red", "Salad": "green"}


def test_option_colors_starts_over_when_there_are_more_options_than_colors():
    options = [f"Option {n}" for n in range(len(COLORS) + 1)]

    colors = option_colors(create_poll("Which?", options))

    assert colors[f"Option {len(COLORS)}"] == COLORS[0]


def test_an_option_named_after_a_color_gets_that_color():
    poll = create_poll("Who will win?", ["Red", "Blue", "Green"])

    assert option_colors(poll) == {"Red": "red", "Blue": "blue", "Green": "green"}


def test_color_names_match_ignoring_case_and_common_spellings():
    poll = create_poll("Which?", ["PURPLE", "grey", "Yellow"])

    assert option_colors(poll) == {"PURPLE": "violet", "grey": "gray", "Yellow": "yellow"}


def test_other_options_get_the_colors_named_options_left_free():
    poll = create_poll("Which?", ["Pizza", "Blue", "Sushi"])

    assert option_colors(poll) == {"Pizza": "red", "Blue": "blue", "Sushi": "green"}


def test_a_color_name_is_claimed_only_once():
    poll = create_poll("Which?", ["Red", "red"])

    assert option_colors(poll) == {"Red": "red", "red": "blue"}


def test_local_time_label_shows_utc_time_three_hours_ahead_with_seconds():
    now = datetime(2026, 10, 22, 7, 5, 9, tzinfo=timezone.utc)

    assert local_time_label(now) == "22 Oct 2026, 10:05:09 (UTC+3)"


def test_local_time_label_rolls_over_to_the_next_day():
    now = datetime(2026, 12, 31, 22, 30, tzinfo=timezone.utc)

    assert local_time_label(now) == "01 Jan 2027, 01:30:00 (UTC+3)"


def test_local_time_label_converts_from_any_time_zone():
    now = datetime(2026, 10, 22, 8, 0, tzinfo=timezone(timedelta(hours=2)))

    assert local_time_label(now) == "22 Oct 2026, 09:00:00 (UTC+3)"
