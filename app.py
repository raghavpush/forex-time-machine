import streamlit as st
import requests
import pandas as pd
from datetime import date, timedelta

st.set_page_config(
    page_title="Forex Time Machine",
    page_icon="F",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,500;0,600;0,700;1,400&family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.stApp {
    background-color: #B7AEAE;
    background-image:
        radial-gradient(ellipse 70% 50% at 10% 10%, rgba(189, 156, 74, 0.25), transparent),
        radial-gradient(ellipse 60% 40% at 90% 90%, rgba(138, 125, 81, 0.18), transparent);
    color: #61492B;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.8rem; padding-bottom: 3rem; max-width: 1280px; }

.page-header { border-bottom: 2px solid #D4B97A; padding-bottom: 1.2rem; margin-bottom: 2rem; }
.page-title { font-family: 'Lora', serif; font-size: 2.4rem; font-weight: 700; color: #2C2010; letter-spacing: -0.5px; }
.page-subtitle { color: #8A7050; font-size: 0.9rem; margin-top: 0.3rem; }

.stTabs [data-baseweb="tab-list"] {
    background: #F0E8D4; border: 1px solid #D4C49A; border-radius: 10px; padding: 3px; gap: 3px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; border-radius: 8px; color: #8A7050;
    font-weight: 500; font-size: 0.88rem; padding: 7px 18px; border: none;
    font-family: 'DM Sans', sans-serif;
}
.stTabs [aria-selected="true"] {
    background: #FAF6EE !important; color: #3A2810 !important;
    border: 1px solid #C4A860 !important; box-shadow: 0 1px 4px rgba(100,70,20,0.1) !important;
}
.stTabs [data-baseweb="tab-panel"] { padding: 1.5rem 0 0; }

.card {
    background: #FDF9F2; border: 1px solid #D8C898; border-radius: 14px;
    padding: 1.4rem 1.6rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(100,70,20,0.06);
}
.card-header {
    font-family: 'Lora', serif; font-size: 1rem; font-weight: 600; color: #3A2810;
    margin-bottom: 1rem; padding-bottom: 0.6rem; border-bottom: 1px solid #EAD8A8;
}

.stat-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin: 0.8rem 0; }
.stat-box { background: #F5EDD8; border: 1px solid #D8C898; border-radius: 10px; padding: 0.9rem 1rem; text-align: center; }
.stat-label { font-size: 0.68rem; color: #8A7050; text-transform: uppercase; letter-spacing: 0.1em; margin-bottom: 0.35rem; font-weight: 600; }
.stat-value { font-family: 'DM Mono', monospace; font-size: 1.15rem; font-weight: 500; color: #2C2010; }
.stat-box.high .stat-value { color: #3A7A3A; }
.stat-box.low  .stat-value { color: #9A2020; }
.stat-box.avg  .stat-value { color: #2A5A8A; }
.stat-box.chg  .stat-value { color: #7A4A10; }

.rate-result {
    background: #F5EDD8; border: 1px solid #C8A84A; border-radius: 14px;
    padding: 2rem; text-align: center; margin: 1rem 0;
}
.rate-main { font-family: 'Lora', serif; font-size: 2.8rem; font-weight: 700; color: #2C2010; }
.rate-sub { color: #8A7050; font-size: 0.85rem; margin-top: 0.5rem; font-family: 'DM Mono', monospace; }

.alert-warn { background:#FEF0EE; border:1px solid #E8A090; border-left:4px solid #C84030; border-radius:8px; padding:0.8rem 1.1rem; color:#7A2010; font-size:0.88rem; margin:0.5rem 0; }
.alert-ok   { background:#F0F8EE; border:1px solid #90C880; border-left:4px solid #3A7A3A; border-radius:8px; padding:0.8rem 1.1rem; color:#1A4A1A; font-size:0.88rem; margin:0.5rem 0; }
.alert-info { background:#F0F4FC; border:1px solid #90A8D8; border-left:4px solid #2A5A9A; border-radius:8px; padding:0.8rem 1.1rem; color:#1A2A5A; font-size:0.88rem; margin:0.5rem 0; }

.section-label {
    font-family: 'Lora', serif; font-size: 1.05rem; font-weight: 600; color: #3A2810;
    margin: 1.6rem 0 0.7rem; display: flex; align-items: center; gap: 0.6rem;
}
.section-label::after { content:''; flex:1; height:1px; background:#D8C898; margin-left:0.5rem; }
.tag { background:#EDD87A; color:#5A3A00; border-radius:6px; padding:2px 10px; font-size:0.72rem; font-weight:700; letter-spacing:0.06em; font-family:'DM Sans',sans-serif; }

.vol-wrap { margin-top: 0.8rem; }
.vol-track { background:#E8D8A8; border-radius:4px; height:5px; width:100%; margin-top:4px; }
.vol-fill  { height:5px; border-radius:4px; background:linear-gradient(90deg,#C4A030,#9A4A10); }

.heatmap-table { width:100%; border-collapse:collapse; font-size:0.85rem; }
.heatmap-table th { background:#EAD8A8; color:#3A2810; padding:8px 12px; text-align:left; font-weight:600; font-size:0.75rem; text-transform:uppercase; letter-spacing:0.08em; border-bottom:2px solid #D4B97A; }
.heatmap-table td { padding:8px 12px; border-bottom:1px solid #EAD8A8; font-family:'DM Mono',monospace; color:#2C2010; }
.heatmap-table tr:hover td { background:#F5EDD8; }
.gain    { color:#2A6A2A; font-weight:600; }
.loss    { color:#8A1A1A; font-weight:600; }
.neutral { color:#6A5030; }

.stSelectbox label, .stMultiSelect label, .stDateInput label,
.stNumberInput label, .stRadio > label, .stTextInput label {
    color:#6A5030 !important; font-size:0.8rem !important;
    font-weight:600 !important; text-transform:uppercase !important; letter-spacing:0.06em !important;
}
div[data-baseweb="select"] > div { background:#FDF9F2 !important; border-color:#C8B888 !important; border-radius:9px !important; color:#2C2010 !important; }
div[data-baseweb="input"] > div { background:#FDF9F2 !important; border-color:#C8B888 !important; border-radius:9px !important; color:#2C2010 !important; }
div[data-baseweb="input"] input { color:#2C2010 !important; background:#FDF9F2 !important; caret-color:#2C2010 !important; }
input, textarea { color:#2C2010 !important; }

.stButton > button {
    background:#C4A030; color:#FAF6EE; font-weight:700; border:none; border-radius:9px;
    padding:0.55rem 1.5rem; font-size:0.88rem; width:100%;
    font-family:'DM Sans',sans-serif; letter-spacing:0.02em;
    box-shadow:0 2px 6px rgba(100,70,10,0.2); transition:all 0.2s;
}
.stButton > button:hover { background:#AA8A20; transform:translateY(-1px); box-shadow:0 4px 12px rgba(100,70,10,0.25); }
.stDownloadButton > button { background:#FDF9F2 !important; color:#6A4A10 !important; border:1px solid #C8A850 !important; border-radius:9px !important; font-weight:600 !important; }
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; border:1px solid #D8C898 !important; }
.stDivider { border-color:#D8C898 !important; }
.stRadio > div { flex-direction:row; gap:1.2rem; }
</style>
""", unsafe_allow_html=True)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
ALL_CURRENCIES = ["USD","EUR","GBP","INR","JPY","AUD","CAD","CHF","CNY","SGD",
                  "HKD","NOK","SEK","NZD","MXN","ZAR","BRL","TRY","KRW","THB"]

# ── HEADER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <div class="page-title">Forex Time Machine</div>
    <div class="page-subtitle">Historical rates · Live conversion · Trend analysis · Currency basket</div>
</div>
""", unsafe_allow_html=True)

today = date.today()

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Historical Rates",
    "Live Converter",
    "Rate Heatmap",
    "Moving Average",
    "Currency Basket"
])

# ═══════════════════════════════════════════════
# TAB 1 — HISTORICAL RATES
# ═══════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)
    base    = c1.selectbox("Base Currency", ALL_CURRENCIES, index=0, key="h_base")
    targets = c2.multiselect("Compare With", [c for c in ALL_CURRENCIES if c != base], default=["INR"], key="h_tgts")

    st.markdown('<div class="section-label">Date Range</div>', unsafe_allow_html=True)
    qc = st.columns(5)
    for i, (lbl, days) in enumerate([("7 Days",7),("30 Days",30),("90 Days",90),("6 Months",180),("1 Year",365)]):
        if qc[i].button(lbl, key=f"h_p{i}"):
            st.session_state["h_start"] = today - timedelta(days=days)
            st.session_state["h_end"]   = today

    d1, d2 = st.columns(2)
    start = d1.date_input("Start Date", value=st.session_state.get("h_start", today - timedelta(days=30)), key="h_sd")
    end   = d2.date_input("End Date",   value=st.session_state.get("h_end",   today),                      key="h_ed")

    a1, a2 = st.columns(2)
    alert_val  = a1.number_input(f"Alert if {base}/{targets[0] if targets else 'INR'} drops below:", min_value=0.0, value=0.0, step=0.01, key="h_alert")
    chart_type = a2.radio("Chart Style", ["Line","Area","Bar"], horizontal=True, key="h_ct")

    if st.button("Fetch Historical Data", key="h_go"):
        if not targets:
            st.warning("Select at least one target currency.")
        elif start >= end:
            st.error("Start date must be before end date.")
        else:
            with st.spinner("Fetching data..."):
                try:
                    url  = f"https://api.frankfurter.app/{start}..{end}?from={base}&to={','.join(targets)}"
                    data = requests.get(url, timeout=10).json()
                    if "rates" not in data:
                        st.error("No data returned.")
                    else:
                        rows = [{"Date": d, **r} for d, r in data["rates"].items()]
                        df   = pd.DataFrame(rows).set_index("Date")
                        df.index = pd.to_datetime(df.index)

                        st.markdown(f'<div class="section-label">Exchange Rates <span class="tag">{start} to {end}</span></div>', unsafe_allow_html=True)
                        if chart_type == "Line":   st.line_chart(df, use_container_width=True, height=300)
                        elif chart_type == "Bar":  st.bar_chart(df,  use_container_width=True, height=300)
                        else:                      st.area_chart(df, use_container_width=True, height=300)

                        st.markdown('<div class="section-label">Statistics per Pair</div>', unsafe_allow_html=True)
                        for tgt in targets:
                            if tgt not in df.columns: continue
                            s    = df[tgt]
                            chg  = s.iloc[-1] - s.iloc[0]
                            pct  = (chg / s.iloc[0]) * 100
                            vn   = min(int((s.std() / s.mean()) * 1000), 100)
                            sign = "+" if chg >= 0 else ""
                            clr  = "#2A6A2A" if chg >= 0 else "#8A1A1A"
                            st.markdown(f"""
                            <div class="card">
                                <div class="card-header">{base} to {tgt}
                                    <span style="float:right;color:{clr};font-family:'DM Mono',monospace;font-weight:600;">{sign}{pct:.2f}%</span>
                                </div>
                                <div class="stat-grid">
                                    <div class="stat-box high"><div class="stat-label">Highest</div><div class="stat-value">{s.max():.4f}</div></div>
                                    <div class="stat-box low"><div class="stat-label">Lowest</div><div class="stat-value">{s.min():.4f}</div></div>
                                    <div class="stat-box avg"><div class="stat-label">Average</div><div class="stat-value">{s.mean():.4f}</div></div>
                                    <div class="stat-box chg"><div class="stat-label">Net Change</div><div class="stat-value">{sign}{chg:.4f}</div></div>
                                </div>
                                <div class="vol-wrap">
                                    <div class="stat-label">Volatility Index</div>
                                    <div class="vol-track"><div class="vol-fill" style="width:{vn}%"></div></div>
                                    <div style="color:#8A7050;font-size:0.72rem;margin-top:3px;">{vn} / 100</div>
                                </div>
                            </div>""", unsafe_allow_html=True)

                        if alert_val > 0 and targets:
                            ft = targets[0]
                            if ft in df.columns:
                                if df[ft].min() < alert_val:
                                    st.markdown(f'<div class="alert-warn">Rate Alert: {base}/{ft} dropped below {alert_val}. Lowest: {df[ft].min():.4f}</div>', unsafe_allow_html=True)
                                else:
                                    st.markdown(f'<div class="alert-ok">Rate Alert: {base}/{ft} stayed above {alert_val}. Lowest: {df[ft].min():.4f}</div>', unsafe_allow_html=True)

                        st.markdown('<div class="section-label">Raw Data</div>', unsafe_allow_html=True)
                        st.dataframe(df.style.format("{:.4f}"), use_container_width=True)
                        st.download_button("Download CSV", df.to_csv(), file_name=f"{base}_rates_{start}_{end}.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════
# TAB 2 — LIVE CONVERTER
# ═══════════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-label">Convert Currency</div>', unsafe_allow_html=True)
    lc1, lc2, lc3 = st.columns([2,1,2])
    from_c = lc1.selectbox("From", ALL_CURRENCIES, index=0, key="lc_from")
    lc2.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    if lc2.button("Swap", key="lc_swap"):
        st.rerun()
    to_c = lc3.selectbox("To", ALL_CURRENCIES, index=3, key="lc_to")
    amt  = st.number_input("Amount", min_value=0.01, value=100.0, step=10.0, key="lc_amt")

    if st.button("Convert", key="lc_go"):
        if from_c == to_c:
            st.markdown(f'<div class="rate-result"><div class="rate-main">{amt:,.4f} {to_c}</div><div class="rate-sub">Same currency — no conversion needed.</div></div>', unsafe_allow_html=True)
        else:
            with st.spinner("Fetching live rate..."):
                try:
                    data = requests.get(f"https://api.frankfurter.app/latest?from={from_c}&to={to_c}", timeout=8).json()
                    if "rates" in data and to_c in data["rates"]:
                        rate   = data["rates"][to_c]
                        result = amt * rate
                        inv    = 1 / rate
                        upd    = data.get("date","today")
                        st.markdown(f"""
                        <div class="rate-result">
                            <div style="color:#8A7050;font-size:0.85rem;margin-bottom:0.4rem;">{amt:,.2f} {from_c} equals</div>
                            <div class="rate-main">{result:,.4f} {to_c}</div>
                            <div class="rate-sub">1 {from_c} = {rate:.6f} {to_c} &nbsp;|&nbsp; 1 {to_c} = {inv:.6f} {from_c}</div>
                            <div class="rate-sub" style="margin-top:0.3rem;">Rate date: {upd}</div>
                        </div>""", unsafe_allow_html=True)

                        st.markdown('<div class="section-label">Reference Table</div>', unsafe_allow_html=True)
                        mults  = [1,5,10,25,50,100,250,500,1000,5000,10000]
                        ref_df = pd.DataFrame({from_c:[f"{m:,.2f}" for m in mults], to_c:[f"{m*rate:,.4f}" for m in mults]})
                        st.dataframe(ref_df, use_container_width=True, hide_index=True)

                        st.markdown(f'<div class="section-label">Cross Rates for {from_c}</div>', unsafe_allow_html=True)
                        majors = [c for c in ["USD","EUR","GBP","INR","JPY","AUD","CAD","CHF","SGD"] if c != from_c]
                        cr = requests.get(f"https://api.frankfurter.app/latest?from={from_c}&to={','.join(majors)}", timeout=8).json()
                        if "rates" in cr:
                            cr_df = pd.DataFrame([{"Currency":k,"Rate":f"{v:.6f}",f"100 {from_c}":f"{v*100:.4f}"} for k,v in cr["rates"].items()])
                            st.dataframe(cr_df, use_container_width=True, hide_index=True)
                    else:
                        st.error("Could not fetch rate.")
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════
# TAB 3 — RATE HEATMAP  (NEW)
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="card" style="margin-bottom:1.2rem;">
        <div class="card-header">Rate Heatmap</div>
        <p style="color:#6A5030;font-size:0.88rem;margin:0;">
            See how a base currency performed against multiple targets. Green cells = base gained value; red cells = base lost value.
        </p>
    </div>""", unsafe_allow_html=True)

    hm1, hm2 = st.columns(2)
    hm_base    = hm1.selectbox("Base Currency", ALL_CURRENCIES, index=0, key="hm_b")
    hm_targets = hm2.multiselect("Target Currencies", [c for c in ALL_CURRENCIES if c != hm_base],
                                  default=["INR","EUR","GBP","JPY","AUD"], key="hm_t")
    hd1, hd2 = st.columns(2)
    hm_start = hd1.date_input("Start", value=today - timedelta(days=30), key="hm_s")
    hm_end   = hd2.date_input("End",   value=today,                      key="hm_e")

    if st.button("Generate Heatmap", key="hm_go"):
        if not hm_targets:
            st.warning("Select at least one target.")
        else:
            with st.spinner("Building heatmap..."):
                try:
                    data = requests.get(f"https://api.frankfurter.app/{hm_start}..{hm_end}?from={hm_base}&to={','.join(hm_targets)}", timeout=10).json()
                    if "rates" not in data:
                        st.error("No data.")
                    else:
                        rows = [{"Date": d, **r} for d, r in data["rates"].items()]
                        df   = pd.DataFrame(rows).set_index("Date")
                        df.index = pd.to_datetime(df.index)

                        rows_html = ""
                        for tgt in hm_targets:
                            if tgt not in df.columns: continue
                            s    = df[tgt]
                            op   = s.iloc[0]; cl = s.iloc[-1]
                            chg  = cl - op;   pct = (chg/op)*100
                            inten = min(abs(pct)*8, 60)
                            bg   = f"rgba(50,140,50,{inten/200})" if pct >= 0 else f"rgba(180,40,40,{inten/200})"
                            cls  = "gain" if pct >= 0 else "loss"
                            sign = "+" if pct >= 0 else ""
                            rows_html += f"""
                            <tr style="background:{bg}">
                                <td style="font-weight:600;color:#2C2010;">{hm_base} / {tgt}</td>
                                <td>{op:.4f}</td><td>{cl:.4f}</td>
                                <td class="{cls}">{sign}{chg:.4f}</td>
                                <td class="{cls}">{sign}{pct:.2f}%</td>
                                <td class="gain">{s.max():.4f}</td>
                                <td class="loss">{s.min():.4f}</td>
                                <td class="neutral">{s.mean():.4f}</td>
                            </tr>"""

                        st.markdown(f"""
                        <div class="card">
                            <div class="card-header">{hm_base} Performance — {hm_start} to {hm_end}</div>
                            <table class="heatmap-table">
                                <thead><tr><th>Pair</th><th>Open</th><th>Close</th><th>Change</th><th>Change %</th><th>High</th><th>Low</th><th>Average</th></tr></thead>
                                <tbody>{rows_html}</tbody>
                            </table>
                        </div>""", unsafe_allow_html=True)
                        st.markdown('<div class="section-label">Rate Chart</div>', unsafe_allow_html=True)
                        st.line_chart(df, use_container_width=True, height=280)
                except Exception as e:
                    st.error(f"Error: {e}")

# ═══════════════════════════════════════════════
# TAB 4 — MOVING AVERAGE  (NEW)
# ═══════════════════════════════════════════════
with tab4:
    st.markdown("""
    <div class="card" style="margin-bottom:1.2rem;">
        <div class="card-header">Moving Average Analysis</div>
        <p style="color:#6A5030;font-size:0.88rem;margin:0;">
            Overlay 7-day and 30-day moving averages on rate data to identify momentum.
            A Golden Cross (7D crosses above 30D) is a bullish signal; a Death Cross is bearish.
        </p>
    </div>""", unsafe_allow_html=True)

    ma1, ma2 = st.columns(2)
    ma_base   = ma1.selectbox("Base", ALL_CURRENCIES, index=0, key="ma_b")
    ma_target = ma2.selectbox("Target", [c for c in ALL_CURRENCIES if c != ma_base], index=2, key="ma_t")
    md1, md2  = st.columns(2)
    ma_start  = md1.date_input("Start", value=today - timedelta(days=180), key="ma_s")
    ma_end    = md2.date_input("End",   value=today,                        key="ma_e")
    mc1, mc2  = st.columns(2)
    show_7    = mc1.checkbox("7-Day Moving Average",  value=True, key="ma_7")
    show_30   = mc2.checkbox("30-Day Moving Average", value=True, key="ma_30")

    if st.button("Analyse Trend", key="ma_go"):
        with st.spinner("Calculating moving averages..."):
            try:
                data = requests.get(f"https://api.frankfurter.app/{ma_start}..{ma_end}?from={ma_base}&to={ma_target}", timeout=10).json()
                if "rates" not in data:
                    st.error("No data. Try a wider range.")
                else:
                    rows = [{"Date": d, "Rate": r[ma_target]} for d, r in data["rates"].items() if ma_target in r]
                    df   = pd.DataFrame(rows).set_index("Date")
                    df.index = pd.to_datetime(df.index)

                    plot_df = df.copy()
                    if show_7  and len(df) >= 7:  plot_df["MA 7D"]  = df["Rate"].rolling(7).mean()
                    if show_30 and len(df) >= 30: plot_df["MA 30D"] = df["Rate"].rolling(30).mean()

                    st.markdown(f'<div class="section-label">Rate + Moving Averages <span class="tag">{ma_base} / {ma_target}</span></div>', unsafe_allow_html=True)
                    st.line_chart(plot_df, use_container_width=True, height=320)

                    rate    = df["Rate"]
                    last    = rate.iloc[-1]; first = rate.iloc[0]
                    r7      = rate.tail(7).mean()
                    r30     = rate.tail(30).mean() if len(rate) >= 30 else None
                    trend   = "Upward" if last > first else "Downward"
                    tclr    = "#2A6A2A" if last > first else "#8A1A1A"
                    r30_str = f"{r30:.4f}" if r30 else "N/A (need 30+ days)"

                    st.markdown(f"""
                    <div class="card">
                        <div class="card-header">Trend Summary</div>
                        <div class="stat-grid">
                            <div class="stat-box avg"><div class="stat-label">Last Rate</div><div class="stat-value">{last:.4f}</div></div>
                            <div class="stat-box avg"><div class="stat-label">7D Avg</div><div class="stat-value">{r7:.4f}</div></div>
                            <div class="stat-box avg"><div class="stat-label">30D Avg</div><div class="stat-value">{r30_str}</div></div>
                            <div class="stat-box chg"><div class="stat-label">Overall Avg</div><div class="stat-value">{rate.mean():.4f}</div></div>
                        </div>
                        <div style="margin-top:0.8rem;padding:0.7rem 1rem;background:#F5EDD8;border-radius:8px;border:1px solid #D8C898;">
                            <span style="color:#6A5030;font-size:0.8rem;font-weight:600;text-transform:uppercase;letter-spacing:0.08em;">Overall Trend</span>
                            <span style="font-size:1.1rem;font-weight:700;color:{tclr};margin-left:0.8rem;">{trend}</span>
                            <span style="color:#8A7050;font-size:0.82rem;margin-left:0.5rem;">over {len(rate)} trading days</span>
                        </div>
                    </div>""", unsafe_allow_html=True)

                    if show_7 and show_30 and len(df) >= 30:
                        ma7  = df["Rate"].rolling(7).mean().dropna()
                        ma30 = df["Rate"].rolling(30).mean().dropna()
                        com  = ma7.index.intersection(ma30.index)
                        if len(com) >= 2:
                            dn = ma7[com[-1]]  - ma30[com[-1]]
                            dp = ma7[com[-2]]  - ma30[com[-2]]
                            if dp < 0 and dn >= 0:
                                st.markdown('<div class="alert-ok">Golden Cross detected: 7-day MA crossed above 30-day MA — potential bullish signal.</div>', unsafe_allow_html=True)
                            elif dp > 0 and dn <= 0:
                                st.markdown('<div class="alert-warn">Death Cross detected: 7-day MA crossed below 30-day MA — potential bearish signal.</div>', unsafe_allow_html=True)
                            else:
                                st.markdown('<div class="alert-info">No crossover event detected in the latest window.</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"Error: {e}")

# ═══════════════════════════════════════════════
# TAB 5 — CURRENCY BASKET  (NEW)
# ═══════════════════════════════════════════════
with tab5:
    st.markdown("""
    <div class="card" style="margin-bottom:1.2rem;">
        <div class="card-header">Currency Basket Calculator</div>
        <p style="color:#6A5030;font-size:0.88rem;margin:0;">
            Allocate an amount across multiple currencies by percentage and see how much you get in each —
            useful for travel budgets and multi-currency portfolios.
        </p>
    </div>""", unsafe_allow_html=True)

    bk1, bk2 = st.columns(2)
    bk_base = bk1.selectbox("Your Home Currency", ALL_CURRENCIES, index=0, key="bk_base")
    bk_amt  = bk2.number_input("Total Amount", min_value=1.0, value=1000.0, step=100.0, key="bk_amt")

    bk_curs = st.multiselect("Select Currencies for Basket",
                              [c for c in ALL_CURRENCIES if c != bk_base],
                              default=["EUR","GBP","JPY","AUD"], key="bk_curs")

    allocs = {}
    if bk_curs:
        default_p = round(100 / len(bk_curs), 1)
        acols = st.columns(min(len(bk_curs), 5))
        for i, cur in enumerate(bk_curs):
            allocs[cur] = acols[i % 5].number_input(f"{cur} %", min_value=0.0, max_value=100.0,
                                                      value=default_p, step=0.5, key=f"bk_{cur}")

    total_pct = sum(allocs.values()) if allocs else 0
    if total_pct > 0:
        if abs(total_pct - 100) < 0.1:
            st.markdown('<div class="alert-ok">Allocation balanced at 100%.</div>', unsafe_allow_html=True)
        elif total_pct > 100:
            st.markdown(f'<div class="alert-warn">Total is {total_pct:.1f}% — exceeds 100%. Please adjust.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="alert-info">Total is {total_pct:.1f}% — {100-total_pct:.1f}% unallocated.</div>', unsafe_allow_html=True)

    if st.button("Calculate Basket", key="bk_go"):
        if not bk_curs:
            st.warning("Select at least one currency.")
        elif total_pct <= 0:
            st.warning("Set at least one allocation percentage.")
        else:
            with st.spinner("Fetching live rates..."):
                try:
                    data = requests.get(f"https://api.frankfurter.app/latest?from={bk_base}&to={','.join(bk_curs)}", timeout=8).json()
                    if "rates" not in data:
                        st.error("Could not fetch rates.")
                    else:
                        rates   = data["rates"]
                        upd     = data.get("date","today")
                        results = []
                        total_allocated = 0.0
                        for cur in bk_curs:
                            if cur not in rates: continue
                            rate      = rates[cur]
                            pct       = allocs.get(cur, 0)
                            portion   = bk_amt * (pct / 100)
                            converted = portion * rate
                            total_allocated += portion
                            results.append({
                                "Currency":              cur,
                                "Allocation %":          f"{pct:.1f}%",
                                f"Amount ({bk_base})":   f"{portion:,.2f}",
                                f"Converted ({cur})":    f"{converted:,.4f}",
                                f"Rate (1 {bk_base})":   f"{rate:.6f}"
                            })

                        st.markdown(f'<div class="section-label">Basket Results <span class="tag">Rates from {upd}</span></div>', unsafe_allow_html=True)
                        res_df = pd.DataFrame(results)
                        st.dataframe(res_df, use_container_width=True, hide_index=True)

                        st.markdown(f"""
                        <div class="card" style="margin-top:1rem;">
                            <div class="card-header">Summary</div>
                            <div class="stat-grid">
                                <div class="stat-box avg"><div class="stat-label">Total Input</div><div class="stat-value">{bk_amt:,.2f} {bk_base}</div></div>
                                <div class="stat-box chg"><div class="stat-label">Currencies</div><div class="stat-value">{len(results)}</div></div>
                                <div class="stat-box high"><div class="stat-label">Allocated</div><div class="stat-value">{total_allocated:,.2f} {bk_base}</div></div>
                                <div class="stat-box low"><div class="stat-label">Unallocated</div><div class="stat-value">{bk_amt-total_allocated:,.2f} {bk_base}</div></div>
                            </div>
                        </div>""", unsafe_allow_html=True)

                        st.download_button("Download Basket CSV", res_df.to_csv(index=False),
                                           file_name=f"basket_{bk_base}_{upd}.csv", mime="text/csv")
                except Exception as e:
                    st.error(f"Error: {e}")

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #D8C898;color:#A89060;font-size:0.78rem;">
    Powered by Frankfurter API &nbsp;·&nbsp; Rates updated daily on business days &nbsp;·&nbsp; Not financial advice
</div>
""", unsafe_allow_html=True)
