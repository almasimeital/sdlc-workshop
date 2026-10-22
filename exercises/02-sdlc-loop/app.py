"""Streamlit view. Keep it thin: load state, call poll.core, render."""

import re
from datetime import datetime, timezone

import altair as alt
import pandas as pd
import streamlit as st

from poll import store
from poll.core import (
    create_poll,
    local_time_label,
    option_colors,
    results,
    tally,
    total_votes,
    vote,
)

# Streamlit's own shades of each color name, so the bars match the colored labels.
BAR_COLORS = {
    "blue": "#1c83e1",
    "red": "#ff4b4b",
    "green": "#21c354",
    "orange": "#ff8700",
    "violet": "#803df5",
    "yellow": "#faca2b",
    "gray": "#808495",
}


def plain(text: str) -> str:
    """Escape Markdown, so a question or option like `a]b` or `![x](url)` shows as typed."""
    return re.sub(r"([\\`*_\[\]()!$#<>~|])", r"\\\1", text)


st.set_page_config(page_title="Live Poll", page_icon="🗳️")
st.title("🗳️ Live Poll")


# A fragment reruns on its own, so the clock ticks without reloading the poll below it.
@st.fragment(run_every=1)
def clock():
    st.markdown(f"🕒 {local_time_label(datetime.now(timezone.utc))}")


clock()

poll = store.load()

if poll is None:
    st.subheader("Create a poll")
    with st.form("create"):
        question = st.text_input("Question")
        options_text = st.text_area("Options, one per line")
        submitted = st.form_submit_button("Create poll")
    if submitted:
        try:
            store.save(create_poll(question, options_text.splitlines()))
        except ValueError as err:
            st.error(str(err))
        else:
            st.rerun()
    st.stop()

st.subheader(plain(poll["question"]))
colors = option_colors(poll)
# One set of numbers for the pie and the list, so they can't disagree.
poll_results = results(poll)

with st.form("vote"):
    choice = st.radio(
        "Your vote",
        poll["options"],
        format_func=lambda option: f":{colors[option]}[{plain(option)}]",
    )
    if st.form_submit_button("Vote"):
        store.save(vote(poll, choice))
        st.rerun()

chart_data = pd.DataFrame(tally(poll), columns=["Option", "Votes"])
# Pin each option to its color and keep the poll's order; Vega would sort both otherwise.
color_scale = alt.Scale(
    domain=poll["options"], range=[BAR_COLORS[colors[option]] for option in poll["options"]]
)
chart = (
    alt.Chart(chart_data)
    .mark_bar()
    .encode(
        x=alt.X("Option", sort=poll["options"]),
        y=alt.Y("Votes", axis=alt.Axis(tickMinStep=1)),
        color=alt.Color("Option", scale=color_scale, legend=None),
        tooltip=["Option", "Votes"],
    )
)
st.altair_chart(chart)

# A pie of nothing looks broken, so it only appears once someone has voted. Options without
# votes have no slice, so they're left out instead of showing a stray "0%".
if total_votes(poll):
    pie_data = pd.DataFrame(
        {
            "Option": result["option"],
            "Votes": result["votes"],
            "Percent": result["percent"],
            "Label": f"{result['percent']}%",
        }
        for result in poll_results
        if result["votes"]
    )
    pie = alt.Chart(pie_data).encode(
        theta=alt.Theta("Votes", stack=True),
        color=alt.Color("Option", scale=color_scale, legend=None),
    )
    slices = pie.mark_arc(outerRadius=110).encode(
        tooltip=["Option", "Votes", alt.Tooltip("Label", title="Percent")]
    )
    labels = pie.mark_text(radius=135).encode(text="Label")
    st.altair_chart(slices + labels)

for result in poll_results:
    trophy = "🏆 " if result["leader"] else ""
    st.markdown(
        f"{trophy}:{colors[result['option']]}[{plain(result['option'])}]: "
        f"{result['votes']} votes ({result['percent']}%)"
    )
st.caption(f"{total_votes(poll)} votes so far")

if st.button("Reset poll"):
    store.clear()
    st.rerun()
