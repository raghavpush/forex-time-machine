# app.py
import streamlit as st
import requests
import pandas as pd

st.title("💱 Forex Time Machine")
st.caption("Travel back in time to see currency rates")

col1, col2 = st.columns(2)
with col1:
    base = st.selectbox("From", ["USD", "INR", "EUR", "GBP", "JPY"])
with col2:
    target = st.selectbox("To", ["INR", "USD", "EUR", "GBP", "JPY"])

start = st.date_input("Start Date")
end   = st.date_input("End Date")

if st.button("⏳ Time Travel!"):
    url = f"https://api.frankfurter.app/{start}..{end}?from={base}&to={target}"
    data = requests.get(url).json()
    
    df = pd.DataFrame({
        "Date": list(data["rates"].keys()),
        "Rate": [v[target] for v in data["rates"].values()]
    })
    
    st.line_chart(df.set_index("Date"))
    st.dataframe(df)
    st.download_button("📥 Download CSV", df.to_csv(), "rates.csv")


# ── COMPARISON STATS ──────────────────────
st.divider()
st.subheader("📊 Quick Stats")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Highest Rate", f"{df['Rate'].max():.4f}")
with col2:
    st.metric("Lowest Rate", f"{df['Rate'].min():.4f}")
with col3:
    st.metric("Average Rate", f"{df['Rate'].mean():.4f}")
with col4:
    change = df['Rate'].iloc[-1] - df['Rate'].iloc[0]
    st.metric("Total Change", f"{change:.4f}", 
              delta=f"{(change/df['Rate'].iloc[0]*100):.2f}%")
