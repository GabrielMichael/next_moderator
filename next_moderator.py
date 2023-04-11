import random
import pandas as pd
import numpy as np
import streamlit as st
import datetime as dt
import altair as alt

# ===================== #
#  STREAMLIT FUNCTIONS  #
# ===================== #


@st.cache_data
def get_df_mod():
    df_mod = pd.read_csv("moderator_history.csv")
    df_mod["Date"] = pd.to_datetime(df_mod["Date"], format="%Y-%m-%d").dt.date
    return df_mod


def get_nxt_mod(lst_mod, available_team):
    nxt_mod = random.choice(available_team)
    while nxt_mod == lst_mod:
        nxt_mod = random.choice(available_team)
    return nxt_mod


def add_nxt_mod(df_mod, nxt_mod, nxt_dt):
    insert_row = {
        "Date": nxt_dt,
        "Moderator": nxt_mod,
    }
    df_mod = pd.concat([df_mod, pd.DataFrame([insert_row])], ignore_index=True)
    df_mod["Date"] = pd.to_datetime(df_mod["Date"], format="%Y-%m-%d").dt.date
    df_mod.to_csv("moderator_history.csv", encoding="utf-8", index=False)
    return df_mod


def drop_new_rows(df_mod, tdy):
    df_mod = df_mod[df_mod["Date"] <= tdy]
    df_mod.to_csv("moderator_history.csv", encoding="utf-8", index=False)
    return df_mod


# =============== #
#  STREAMLIT APP  #
# =============== #

st.set_page_config(page_title="Next Moderator", page_icon="📣", layout="wide")

customized_button = st.markdown(
    """<style >.stDownloadButton, div.stButton {text-align:center}</style>""",
    unsafe_allow_html=True,
)

hide_table_row_index = """<style> thead tr th:first-child {display:none} tbody th {display:none} </style>"""

col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    st.image("logo.png", width=120)
with col2:
    st.write("")
with col3:
    st.markdown(
        "<p style='text-align: right; font-size: 25px; color: #FFB000'><b>BI Installation's <span style='color: #072543'>Next Moderator</span></b></p>",
        unsafe_allow_html=True,
    )

df_mod = get_df_mod()
lst_mod = df_mod["Moderator"].iloc[-1]
lst_dt = df_mod["Date"].iloc[-1]
tdy = dt.datetime.date(dt.datetime.today())

if tdy.isoweekday() == 6:
    st.markdown(
        "<p style='text-align: center; font-size: 75px; color: #072543'><b>Tool is off on Saturdays.</b></p>",
        unsafe_allow_html=True,
    )
elif tdy.isoweekday() == 7:
    st.markdown(
        "<p style='text-align: center; font-size: 75px; color: #072543'><b>Tool is off on Sundays.</b></p>",
        unsafe_allow_html=True,
    )
else:
    if tdy.isoweekday() in [1, 2]:
        nxt_dt_dflt = tdy + dt.timedelta(days=(3 - tdy.isoweekday()))
    elif tdy.isoweekday() in [3, 4]:
        nxt_dt_dflt = tdy + dt.timedelta(days=(5 - tdy.isoweekday()))
    elif tdy.isoweekday() == 5:
        nxt_dt_dflt = tdy + dt.timedelta(days=3)

    st.markdown(
        "<p style='text-align: center; font-size: 25px; color: #FFB000'><b>Today's Moderator</b></p>",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"<p style='text-align: center; font-size: 50px; color: #072543'><b>{lst_mod}</b></p>",
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns([4, 1])
    with col1:
        available_team = st.multiselect(
            "Who is available to moderate?",
            ["Alina", "Christian", "Michael", "Mostafa", "Nived", "Sushant"],
            ["Alina", "Christian", "Michael", "Mostafa", "Nived", "Sushant"],
        )
    with col2:
        nxt_dt = st.date_input("Next Stand-Up's Date", nxt_dt_dflt)

    button_nxt_mod = st.button(label="Get Lucky!")
    st.write("")

    if button_nxt_mod:
        if len(available_team) == 1:
            st.markdown(
                "<p style='text-align: center; font-size: 35px; color: #072543'><b>Well, you're the only one available. Why did you even run this thing?</b></p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                "<p style='text-align: center; font-size: 70px; color: #072543'><b>🤨</b></p>",
                unsafe_allow_html=True,
            )
        else:
            if lst_dt == nxt_dt:
                df_mod = df_mod[df_mod["Date"] < nxt_dt]
                nxt_mod = get_nxt_mod(lst_mod, available_team)
                df_mod = add_nxt_mod(df_mod, nxt_mod, nxt_dt)
            else:
                nxt_mod = get_nxt_mod(lst_mod, available_team)
                df_mod = add_nxt_mod(df_mod, nxt_mod, nxt_dt)

            st.markdown(
                f"<p style='text-align: center; font-size: 25px; color: #FFB000'><b>{nxt_dt} Stand-Up's Moderator</b></p>",
                unsafe_allow_html=True,
            )
            st.markdown(
                f"<p style='text-align: center; font-size: 75px; color: #072543'><b>{nxt_mod}</b></p>",
                unsafe_allow_html=True,
            )
            st.write("")

            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.markdown(
                    f"<p style='text-align: center; font-size: 20px; color: #072543'><b>This Month's Leaderboard</b></p>",
                    unsafe_allow_html=True,
                )
                df_lb_tm = df_mod[
                    (df_mod["Date"] >= dt.date(tdy.year, tdy.month, 1))
                    & (df_mod["Date"] < nxt_dt_dflt)
                ]
                df_lb_tm = df_lb_tm.groupby("Moderator", as_index=False).count()
                df_lb_tm.rename(columns={"Date": "Number of Moderations"}, inplace=True)
                df_lb_tm["Colour"] = np.where(
                    df_lb_tm["Number of Moderations"]
                    == df_lb_tm["Number of Moderations"].max(),
                    "#FFB000",
                    "#072543",
                )
                domain = df_lb_tm["Moderator"].tolist()
                range = df_lb_tm["Colour"].tolist()
                chart_data = (
                    alt.Chart(df_lb_tm)
                    .mark_bar()
                    .encode(
                        x="Moderator",
                        y=alt.Y("Number of Moderations", axis=alt.Axis(tickMinStep=1)),
                        color=alt.Color(
                            "Moderator",
                            scale=alt.Scale(domain=domain, range=range),
                            legend=None,
                        ),
                    )
                )
                st.altair_chart(chart_data, use_container_width=True)
            with col2:
                st.markdown(
                    f"<p style='text-align: center; font-size: 20px; color: #072543'><b>Previous Moderators</b></p>",
                    unsafe_allow_html=True,
                )
                df_mod_dsply = df_mod[df_mod["Date"] < nxt_dt_dflt].iloc[::-1].head(8)
                st.markdown(hide_table_row_index, unsafe_allow_html=True)
                st.table(df_mod_dsply)
            with col3:
                st.markdown(
                    f"<p style='text-align: center; font-size: 20px; color: #072543'><b>All Time Leaderboard</b></p>",
                    unsafe_allow_html=True,
                )
                df_lb = df_mod.groupby("Moderator", as_index=False).count()
                df_lb.rename(columns={"Date": "Number of Moderations"}, inplace=True)
                df_lb["Colour"] = np.where(
                    df_lb["Number of Moderations"]
                    == df_lb["Number of Moderations"].max(),
                    "#FFB000",
                    "#072543",
                )
                domain = df_lb["Moderator"].tolist()
                range = df_lb["Colour"].tolist()
                chart_data = (
                    alt.Chart(df_lb)
                    .mark_bar()
                    .encode(
                        x="Moderator",
                        y=alt.Y("Number of Moderations", axis=alt.Axis(tickMinStep=1)),
                        color=alt.Color(
                            "Moderator",
                            scale=alt.Scale(domain=domain, range=range),
                            legend=None,
                        ),
                    )
                )
                st.altair_chart(chart_data, use_container_width=True)
