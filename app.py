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
