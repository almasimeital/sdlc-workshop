"""Tests that drive the Streamlit view the way a user would: type, click, vote, reset.
Logic is tested in test_core.py; these only check that the UI is wired to it."""

import json
from pathlib import Path

import pytest
from streamlit.dataframe_util import convert_arrow_bytes_to_pandas_df
from streamlit.testing.v1 import AppTest

from poll import store
from poll.core import create_poll

APP = str(Path(__file__).resolve().parent.parent / "app.py")


@pytest.fixture(autouse=True)
def poll_file(tmp_path, monkeypatch):
    monkeypatch.setattr(store, "DEFAULT_PATH", tmp_path / "poll.json")


def run_app():
    return AppTest.from_file(APP, default_timeout=30).run()


def click(app, label):
    next(button for button in app.button if button.label == label).click().run()


def create(app, question, options):
    app.text_input[0].input(question)
    app.text_area[0].input("\n".join(options))
    click(app, "Create poll")


def cast_vote(app, option):
    app.radio[0].set_value(option)
    click(app, "Vote")


def chart_spec(app):
    return json.loads(app.get("vega_lite_chart")[0].proto.spec)


def chart_votes(app):
    data = app.get("vega_lite_chart")[0].proto.datasets[0].data.data
    table = convert_arrow_bytes_to_pandas_df(data)
    return dict(zip(table["Option"], table["Votes"], strict=True))


def bar_colors(app):
    scale = chart_spec(app)["encoding"]["color"]["scale"]
    return dict(zip(scale["domain"], scale["range"], strict=True))


def result_lines(app):
    return [text.value for text in app.markdown if "votes (" in text.value]


def mark_type(spec):
    mark = spec["mark"]
    return mark["type"] if isinstance(mark, dict) else mark


def pie_chart(app):
    return app.get("vega_lite_chart")[1]


def page_outline(app):
    """The page from top to bottom: each chart by its first mark, result lines, the caption."""
    outline = []
    for node in app.main:
        if node.type == "vega_lite_chart":
            spec = json.loads(node.proto.spec)
            outline.append(mark_type(spec["layer"][0] if "layer" in spec else spec))
        elif node.type == "markdown" and "votes (" in node.value:
            outline.append("line")
        elif node.type == "caption":
            outline.append("caption")
    return outline


def test_the_current_time_in_utc_plus_3_is_shown():
    app = run_app()

    assert any("(UTC+3)" in text.value for text in app.markdown)


def test_create_a_poll_then_vote():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi"])

    assert app.subheader[0].value == "Lunch?"

    cast_vote(app, "Sushi")

    assert store.load()["votes"] == {"Pizza": 0, "Sushi": 1}
    assert "1 votes so far" in app.caption[0].value


def test_a_saved_poll_opens_on_the_vote_screen():
    store.save(create_poll("Lunch?", ["Pizza", "Sushi"]))

    app = run_app()

    assert app.subheader[0].value == "Lunch?"
    assert len(app.text_input) == 0
    assert app.radio[0].options == [":blue[Pizza]", ":red[Sushi]"]


def test_votes_add_up_on_the_chart_and_the_caption():
    app = run_app()
    create(app, "Who will win?", ["Red", "Blue", "Green"])

    cast_vote(app, "Green")
    cast_vote(app, "Green")
    cast_vote(app, "Red")

    assert store.load()["votes"] == {"Red": 1, "Blue": 0, "Green": 2}
    assert chart_votes(app) == {"Red": 1, "Blue": 0, "Green": 2}
    assert "3 votes so far" in app.caption[0].value


def test_results_list_shows_shares_and_the_leader():
    app = run_app()
    create(app, "Who will win?", ["Red", "Blue", "Green"])

    cast_vote(app, "Red")
    cast_vote(app, "Red")
    cast_vote(app, "Blue")

    assert result_lines(app) == [
        "🏆 :red[Red]: 2 votes (67%)",
        ":blue[Blue]: 1 votes (33%)",
        ":green[Green]: 0 votes (0%)",
    ]


def test_results_list_before_and_after_the_first_vote():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi"])

    assert result_lines(app) == [":blue[Pizza]: 0 votes (0%)", ":red[Sushi]: 0 votes (0%)"]

    cast_vote(app, "Sushi")

    assert result_lines(app) == [":blue[Pizza]: 0 votes (0%)", "🏆 :red[Sushi]: 1 votes (100%)"]


def test_every_tied_leader_gets_the_trophy():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi", "Salad"])

    cast_vote(app, "Pizza")
    cast_vote(app, "Sushi")

    assert result_lines(app) == [
        "🏆 :blue[Pizza]: 1 votes (50%)",
        "🏆 :red[Sushi]: 1 votes (50%)",
        ":green[Salad]: 0 votes (0%)",
    ]


def test_a_pie_chart_shows_each_options_share():
    app = run_app()
    create(app, "Who will win?", ["Red", "Blue", "Green"])

    cast_vote(app, "Red")
    cast_vote(app, "Red")
    cast_vote(app, "Blue")

    chart = pie_chart(app)
    spec = json.loads(chart.proto.spec)
    slices, labels = spec["layer"]
    assert [mark_type(slices), mark_type(labels)] == ["arc", "text"]
    scale = slices["encoding"]["color"]["scale"]
    assert dict(zip(scale["domain"], scale["range"], strict=True)) == bar_colors(app)
    assert [field["field"] for field in slices["encoding"]["tooltip"]] == [
        "Option",
        "Votes",
        "Percent",
    ]
    table = convert_arrow_bytes_to_pandas_df(chart.proto.datasets[0].data.data)
    assert dict(zip(table["Option"], table["Label"], strict=True)) == {"Red": "67%", "Blue": "33%"}


def test_the_page_reads_bar_chart_pie_list_caption():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi"])

    cast_vote(app, "Pizza")

    assert page_outline(app) == ["bar", "arc", "line", "line", "caption"]


def test_no_pie_chart_before_the_first_vote():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi"])

    assert page_outline(app) == ["bar", "line", "line", "caption"]


def test_each_vote_option_is_labelled_in_its_color():
    app = run_app()
    create(app, "Who will win?", ["Red", "Blue", "Green"])

    assert app.radio[0].options == [":red[Red]", ":blue[Blue]", ":green[Green]"]


def test_each_bar_has_the_color_of_its_option_in_poll_order():
    app = run_app()
    create(app, "Who will win?", ["Red", "Blue", "Green"])

    assert bar_colors(app) == {"Red": "#ff4b4b", "Blue": "#1c83e1", "Green": "#21c354"}
    assert chart_spec(app)["encoding"]["x"]["sort"] == ["Red", "Blue", "Green"]


def test_labels_and_bars_agree_when_options_are_not_color_names():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Blue", "Sushi"])

    assert app.radio[0].options == [":red[Pizza]", ":blue[Blue]", ":green[Sushi]"]
    assert bar_colors(app) == {"Pizza": "#ff4b4b", "Blue": "#1c83e1", "Sushi": "#21c354"}


def test_a_poll_with_more_options_than_colors_still_shows():
    options = [f"Option {n}" for n in range(1, 10)]
    app = run_app()
    create(app, "Which?", options)

    assert not app.exception
    assert len(app.radio[0].options) == 9
    assert list(bar_colors(app)) == options


def test_reset_poll_goes_back_to_the_create_form():
    app = run_app()
    create(app, "Lunch?", ["Pizza", "Sushi"])
    cast_vote(app, "Pizza")

    click(app, "Reset poll")

    assert store.load() is None
    assert app.subheader[0].value == "Create a poll"
    assert len(app.radio) == 0


@pytest.mark.parametrize(
    ("question", "options", "message"),
    [
        ("Lunch?", ["Pizza"], "two options"),
        ("   ", ["Pizza", "Sushi"], "question"),
        ("Lunch?", ["Pizza", "Pizza"], "unique"),
    ],
)
def test_invalid_poll_shows_an_error(question, options, message):
    app = run_app()
    create(app, question, options)

    assert message in app.error[0].value
    assert store.load() is None
