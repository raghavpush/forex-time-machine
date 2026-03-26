import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="Forex Time Machine",
    page_icon="💱",
    layout="wide"
)

# ── SIDEBAR ──────────────────────────────────
st.sidebar.title("⚙️ Settings")
theme = st.sidebar.radio("Theme", ["🌙 Dark", "☀️ Light"])

if theme == "🌙 Dark":
    st.markdown("""
        <style>
        .stApp { background-color: #0e1117; color: white; }
        </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #ffffff; color: black; }
        </style>
    """, unsafe_allow_html=True)

# ── TITLE ────────────────────────────────────
st.title("💱 Forex Time Machine")
st.caption("Travel back in time to see currency rates")

# ── CURRENCY SELECTION ───────────────────────
all_currencies = ["USD", "INR", "EUR", "GBP", "JPY", "AUD", "CAD", "CHF", "CNY", "SGD"]

col1, col2 = st.columns(2)
with col1:
    base = st.selectbox("From Currency", all_currencies, index=0)
with col2:
    targets = st.multiselect(
        "Compare With (select multiple)",
        [c for c in all_currencies if c != base],
        default=["INR"]
    )

# ── PRESET DATE BUTTONS ──────────────────────
st.write("📅 Quick Select:")
c1, c2, c3, c4 = st.columns(4)
today = date.today()

if c1.button("Last 7 days"):
    st.session_state["start"] = today - timedelta(days=7)
    st.session_state["end"]   = today
if c2.button("Last 30 days"):
    st.session_state["start"] = today - timedelta(days=30)
    st.session_state["end"]   = today
if c3.button("Last 6 months"):
    st.session_state["start"] = today - timedelta(days=180)
    st.session_state["end"]   = today
if c4.button("Last 1 year"):
    st.session_state["start"] = today - timedelta(days=365)
    st.session_state["end"]   = today

start = st.date_input("Start Date", value=st.session_state.get("start", today - timedelta(days=30)))
end   = st.date_input("End Date",   value=st.session_state.get("end",   today))

# ── RATE ALERT ───────────────────────────────
st.divider()
alert_val = st.number_input(
    f"🔔 Alert me if {base}/{targets[0] if targets else 'INR'} rate goes below:",
    min_value=0.0, value=0.0, step=0.01
)

# ── CHART TYPE ───────────────────────────────
chart_type = st.radio("📊 Chart Type", ["Line", "Bar", "Area"], horizontal=True)

# ── FETCH DATA ───────────────────────────────
if st.button("⏳ Time Travel!"):
    if not targets:
        st.warning("Please select at least one target currency!")
    elif start >= end:
        st.error("Start date must be before end date!")
    else:
        target_str = ",".join(targets)
        url = f"https://api.frankfurter.app/{start}..{end}?from={base}&to={target_str}"

        with st.spinner("Fetching historical rates..."):
            try:
                res  = requests.get(url)
                data = res.json()

                if "rates" not in data:
                    st.error("No data found. Try a different date range.")
                else:
                    rows = []
                    for d, rates in data["rates"].items():
                        row = {"Date": d}
                        row.update(rates)
                        rows.append(row)

                    df = pd.DataFrame(rows).set_index("Date")
                    df.index = pd.to_datetime(df.index)

                    # ── CHART ────────────────────────────────
                    st.subheader(f"📈 {base} Exchange Rates")
                    if chart_type == "Line":
                        st.line_chart(df)
                    elif chart_type == "Bar":
                        st.bar_chart(df)
                    else:
                        st.area_chart(df)

                    # ── QUICK STATS ──────────────────────────
                    st.divider()
                    st.subheader("📊 Quick Stats")

                    for target in targets:
                        if target in df.columns:
                            st.markdown(f"**{base} → {target}**")
                            s1, s2, s3, s4 = st.columns(4)
                            change = df[target].iloc[-1] - df[target].iloc[0]
                            s1.metric("Highest",      f"{df[target].max():.4f}")
                            s2.metric("Lowest",       f"{df[target].min():.4f}")
                            s3.metric("Average",      f"{df[target].mean():.4f}")
                            s4.metric("Total Change", f"{change:.4f}",
                                      delta=f"{(change/df[target].iloc[0]*100):.2f}%")

                    # ── RATE ALERT ───────────────────────────
                    if alert_val > 0 and targets:
                        first_target = targets[0]
                        if first_target in df.columns:
                            if df[first_target].min() < alert_val:
                                st.error(f"⚠️ {base}/{first_target} dropped below {alert_val} during this period! Lowest was {df[first_target].min():.4f}")
                            else:
                                st.success(f"✅ {base}/{first_target} stayed above {alert_val} throughout this period!")

                    # ── DATA TABLE + DOWNLOAD ────────────────
                    st.divider()
                    st.subheader("🗂️ Raw Data")
                    st.dataframe(df, use_container_width=True)
                    st.download_button(
                        "📥 Download CSV",
                        df.to_csv(),
                        file_name=f"{base}_rates_{start}_{end}.csv",
                        mime="text/csv"
                    )

            except Exception as e:
                st.error(f"Something went wrong: {e}")
