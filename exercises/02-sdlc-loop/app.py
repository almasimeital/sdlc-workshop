"""Streamlit view. Keep it thin: load state, call poll.core, render."""

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

st.subheader(poll["question"])
colors = option_colors(poll)

with st.form("vote"):
    choice = st.radio(
        "Your vote", poll["options"], format_func=lambda option: f":{colors[option]}[{option}]"
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
for result in results(poll):
    trophy = "🏆 " if result["leader"] else ""
    st.markdown(
        f"{trophy}:{colors[result['option']]}[{result['option']}]: "
        f"{result['votes']} votes ({result['percent']}%)"
    )
st.caption(f"{total_votes(poll)} votes so far")

if st.button("Reset poll"):
    store.clear()
    st.rerun()
