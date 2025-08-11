
import os, json, time
import pandas as pd
import streamlit as st
import plotly.express as px

LOG_PATH = os.environ.get("LOG_DIR","./logs")
EVENTS = os.path.join(LOG_PATH, "events.ndjson")

st.set_page_config(page_title="v26meme — Autonomous Desk", layout="wide")

st.title("v26meme — Autonomous Crypto Trading Intelligence")
st.caption("Paper mode by default · 4-Lab learning · Bandit allocator · Policy-as-code risk")

# Sidebar
st.sidebar.header("Controls")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
interval = st.sidebar.slider("Refresh seconds", 1, 15, 3)

def load_events():
    if not os.path.exists(EVENTS): 
        return pd.DataFrame(columns=["ts","type","payload"])
    rows = []
    with open(EVENTS,"r") as f:
        for line in f:
            try:
                evt = json.loads(line)
                rows.append(evt)
            except:
                pass
    df = pd.DataFrame(rows)
    if not df.empty:
        df["ts"] = pd.to_datetime(df["ts"], unit="s")
        df = df.sort_values("ts")
    return df

df = load_events()

col1, col2, col3, col4 = st.columns(4)
if not df.empty:
    end = df[df["type"]=="system.loop_end"]["payload"].tail(1)
    eq = end["equity"].iloc[0] if not end.empty else None
    col1.metric("Final Equity", f"{eq:.2f}" if eq else "—")
    sims = df[df["type"]=="simlab.result"].shape[0]
    col2.metric("SimLab runs", f"{sims}")
    allocs = df[df["type"]=="allocator.weights"].shape[0]
    col3.metric("Allocator updates", f"{allocs}")
    trades = df[df["type"]=="trade.signal"].shape[0]
    col4.metric("Trade decisions", f"{trades}")

st.subheader("SimLab Results")
if not df.empty:
    sims = df[df["type"]=="simlab.result"].copy()
    if not sims.empty:
        rows = []
        for _, r in sims.iterrows():
            p = r["payload"]
            rows.append({"name": p["name"], **p["stats"]})
        sims_df = pd.DataFrame(rows)
        st.dataframe(sims_df)
        fig = px.scatter(sims_df, x="mdd", y="exp", color="name", size="sortino",
                         title="Expectancy vs MDD (size=Sortino)")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No SimLab results yet.")

st.subheader("Allocator Weights (latest)")
if not df.empty:
    alloc = df[df["type"]=="allocator.weights"].tail(1)
    if not alloc.empty:
        weights = alloc["payload"].iloc[0]["weights"]
        aw = pd.DataFrame([{"edge":k,"weight":v} for k,v in weights.items()])
        st.dataframe(aw)
        fig = px.bar(aw, x="edge", y="weight", title="Weights")
        st.plotly_chart(fig, use_container_width=True)

st.subheader("Recent Trade Decisions")
if not df.empty:
    tr = df[df["type"]=="trade.signal"].tail(50)
    if not tr.empty:
        tdf = pd.json_normalize(tr["payload"])
        tdf["ts"] = tr["ts"].values
        st.dataframe(tdf)

if auto_refresh:
    time.sleep(interval)
    st.rerun()
