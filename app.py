"""
app.py  —  Forex Time Machine
Entry point. Run with:  python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
from datetime import date, timedelta
from pathlib import Path

from config import (
    APP_TITLE, APP_ICON, APP_SUBTITLE,
    ALL_CURRENCIES, DATE_PRESETS, MAJOR_CURRENCIES,
)
from utils.api import (
    get_latest_rate, get_historical_rates,
    get_single_pair_history, APIError,
)
from utils.charts import (
    alert_warn, alert_ok, alert_info,
    render_volatility_bar, volatility_index,
    heatmap_row, detect_ma_crossover, section_label,
)

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title=APP_TITLE,
    page_icon=APP_ICON,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── INJECT CSS ────────────────────────────────────────────────────────────────
css = Path("styles/main.css").read_text()
st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="page-header">
    <div class="page-title">{APP_ICON} {APP_TITLE}</div>
    <div class="page-subtitle">{APP_SUBTITLE}</div>
</div>
""", unsafe_allow_html=True)

today = date.today()

# ── SESSION STATE INIT ────────────────────────────────────────────────────────
if "conversion_history" not in st.session_state:
    st.session_state.conversion_history = []   # Feature 2: history log

# ── TABS ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Historical Rates",
    "💱 Live Converter",
    "🌡️ Rate Heatmap",
    "📊 Moving Average",
    "🧺 Currency Basket",
])

# ═══════════════════════════════════════════════
# TAB 1 — HISTORICAL RATES
# ═══════════════════════════════════════════════
with tab1:
    c1, c2 = st.columns(2)
    base    = c1.selectbox("Base Currency", ALL_CURRENCIES, index=0, key="h_base")
    targets = c2.multiselect("Compare With", [c for c in ALL_CURRENCIES if c != base], default=["INR"], key="h_tgts")

    st.markdown(section_label("Date Range"), unsafe_allow_html=True)
    qc = st.columns(len(DATE_PRESETS))
    for i, (lbl, days) in enumerate(DATE_PRESETS):
        if qc[i].button(lbl, key=f"h_p{i}"):
            st.session_state["h_start"] = today - timedelta(days=days)
            st.session_state["h_end"]   = today

    d1, d2 = st.columns(2)
    start = d1.date_input("Start Date", value=st.session_state.get("h_start", today - timedelta(days=30)), key="h_sd")
    end   = d2.date_input("End Date",   value=st.session_state.get("h_end",   today),                      key="h_ed")

    a1, a2 = st.columns(2)
    alert_val  = a1.number_input(f"Alert if {base}/{targets[0] if targets else 'INR'} drops below:", min_value=0.0, value=0.0, step=0.01, key="h_alert")
    chart_type = a2.radio("Chart Style", ["Line", "Area", "Bar"], horizontal=True, key="h_ct")

    if st.button("Fetch Historical Data", key="h_go"):
        if not targets:
            st.warning("Select at least one target currency.")
        elif start >= end:
            st.error("Start date must be before end date.")
        else:
            with st.spinner("Fetching data..."):
                try:
                    df = get_historical_rates(base, targets, str(start), str(end))

                    st.markdown(section_label("Exchange Rates", f"{start} to {end}"), unsafe_allow_html=True)
                    if chart_type == "Line":  st.line_chart(df, use_container_width=True, height=300)
                    elif chart_type == "Bar": st.bar_chart(df,  use_container_width=True, height=300)
                    else:                     st.area_chart(df, use_container_width=True, height=300)

                    st.markdown(section_label("Statistics per Pair"), unsafe_allow_html=True)
                    for tgt in targets:
                        if tgt not in df.columns:
                            continue
                        s    = df[tgt]
                        chg  = s.iloc[-1] - s.iloc[0]
                        pct  = (chg / s.iloc[0]) * 100
                        vn   = volatility_index(s)
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
                            {render_volatility_bar(vn)}
                        </div>""", unsafe_allow_html=True)

                    if alert_val > 0 and targets:
                        ft = targets[0]
                        if ft in df.columns:
                            if df[ft].min() < alert_val:
                                alert_warn(f"Rate Alert: {base}/{ft} dropped below {alert_val}. Lowest: {df[ft].min():.4f}")
                            else:
                                alert_ok(f"Rate Alert: {base}/{ft} stayed above {alert_val}. Lowest: {df[ft].min():.4f}")

                    st.markdown(section_label("Raw Data"), unsafe_allow_html=True)
                    st.dataframe(df.style.format("{:.4f}"), use_container_width=True)
                    st.download_button("Download CSV", df.to_csv(), file_name=f"{base}_rates_{start}_{end}.csv", mime="text/csv")
                except APIError as e:
                    st.error(str(e))

# ═══════════════════════════════════════════════
# TAB 2 — LIVE CONVERTER
# ═══════════════════════════════════════════════
with tab2:
    st.markdown(section_label("Convert Currency"), unsafe_allow_html=True)
    lc1, lc2, lc3 = st.columns([2, 1, 2])
    from_c = lc1.selectbox("From", ALL_CURRENCIES, index=0, key="lc_from")
    lc2.markdown("<div style='height:26px'></div>", unsafe_allow_html=True)
    if lc2.button("⇄ Swap", key="lc_swap"):
        st.rerun()
    to_c = lc3.selectbox("To", ALL_CURRENCIES, index=3, key="lc_to")
    amt  = st.number_input("Amount", min_value=0.01, value=100.0, step=10.0, key="lc_amt")

    if st.button("Convert", key="lc_go"):
        if from_c == to_c:
            st.markdown(f'<div class="rate-result"><div class="rate-main">{amt:,.4f} {to_c}</div><div class="rate-sub">Same currency — no conversion needed.</div></div>', unsafe_allow_html=True)
        else:
            with st.spinner("Fetching live rate..."):
                try:
                    data   = get_latest_rate(from_c, [to_c])
                    rate   = data["rates"][to_c]
                    result = amt * rate
                    inv    = 1 / rate
                    upd    = data.get("date", "today")

                    # ── save to history (Feature 2 hook) ──
                    st.session_state.conversion_history.insert(0, {
                        "from": from_c, "to": to_c, "amount": amt,
                        "result": result, "rate": rate, "date": upd,
                    })
                    st.session_state.conversion_history = st.session_state.conversion_history[:10]

                    st.markdown(f"""
                    <div class="rate-result">
                        <div style="color:#8A7050;font-size:0.85rem;margin-bottom:0.4rem;">{amt:,.2f} {from_c} equals</div>
                        <div class="rate-main">{result:,.4f} {to_c}</div>
                        <div class="rate-sub">1 {from_c} = {rate:.6f} {to_c} &nbsp;|&nbsp; 1 {to_c} = {inv:.6f} {from_c}</div>
                        <div class="rate-sub" style="margin-top:0.3rem;">Rate date: {upd}</div>
                    </div>""", unsafe_allow_html=True)

                    st.markdown(section_label("Reference Table"), unsafe_allow_html=True)
                    mults  = [1, 5, 10, 25, 50, 100, 250, 500, 1000, 5000, 10000]
                    ref_df = pd.DataFrame({from_c: [f"{m:,.2f}" for m in mults], to_c: [f"{m*rate:,.4f}" for m in mults]})
                    st.dataframe(ref_df, use_container_width=True, hide_index=True)

                    st.markdown(section_label(f"Cross Rates for {from_c}"), unsafe_allow_html=True)
                    majors = [c for c in MAJOR_CURRENCIES if c != from_c]
                    cr = get_latest_rate(from_c, majors)
                    if "rates" in cr:
                        cr_df = pd.DataFrame([{"Currency": k, "Rate": f"{v:.6f}", f"100 {from_c}": f"{v*100:.4f}"} for k, v in cr["rates"].items()])
                        st.dataframe(cr_df, use_container_width=True, hide_index=True)
                except APIError as e:
                    st.error(str(e))

    # ── Conversion History Panel ──
    if st.session_state.conversion_history:
        st.markdown(section_label("Recent Conversions"), unsafe_allow_html=True)
        for h in st.session_state.conversion_history:
            st.markdown(f"""
            <div class="history-item">
                <div>
                    <div class="history-pair">{h['from']} → {h['to']}</div>
                    <div class="history-meta">{h['amount']:,.2f} {h['from']} &nbsp;·&nbsp; Rate: {h['rate']:.6f} &nbsp;·&nbsp; {h['date']}</div>
                </div>
                <div class="history-result">{h['result']:,.4f} {h['to']}</div>
            </div>""", unsafe_allow_html=True)
        if st.button("Clear History", key="clear_hist"):
            st.session_state.conversion_history = []
            st.rerun()

# ═══════════════════════════════════════════════
# TAB 3 — RATE HEATMAP
# ═══════════════════════════════════════════════
with tab3:
    st.markdown("""
    <div class="card" style="margin-bottom:1.2rem;">
        <div class="card-header">Rate Heatmap</div>
        <p style="color:#6A5030;font-size:0.88rem;margin:0;">
            See how a base currency performed against multiple targets.
            Green cells = base gained value; red cells = base lost value.
        </p>
    </div>""", unsafe_allow_html=True)

    hm1, hm2 = st.columns(2)
    hm_base    = hm1.selectbox("Base Currency", ALL_CURRENCIES, index=0, key="hm_b")
    hm_targets = hm2.multiselect("Target Currencies", [c for c in ALL_CURRENCIES if c != hm_base],
                                  default=["INR", "EUR", "GBP", "JPY", "AUD"], key="hm_t")
    hd1, hd2 = st.columns(2)
    hm_start = hd1.date_input("Start", value=today - timedelta(days=30), key="hm_s")
    hm_end   = hd2.date_input("End",   value=today,                      key="hm_e")

    if st.button("Generate Heatmap", key="hm_go"):
        if not hm_targets:
            st.warning("Select at least one target.")
        else:
            with st.spinner("Building heatmap..."):
                try:
                    df = get_historical_rates(hm_base, hm_targets, str(hm_start), str(hm_end))
                    rows_html = ""
                    for tgt in hm_targets:
                        if tgt not in df.columns:
                            continue
                        s = df[tgt]
                        rows_html += heatmap_row(
                            f"{hm_base} / {tgt}",
                            s.iloc[0], s.iloc[-1], s.max(), s.min(), s.mean()
                        )
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-header">{hm_base} Performance — {hm_start} to {hm_end}</div>
                        <table class="heatmap-table">
                            <thead><tr><th>Pair</th><th>Open</th><th>Close</th><th>Change</th><th>Change %</th><th>High</th><th>Low</th><th>Average</th></tr></thead>
                            <tbody>{rows_html}</tbody>
                        </table>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(section_label("Rate Chart"), unsafe_allow_html=True)
                    st.line_chart(df, use_container_width=True, height=280)
                except APIError as e:
                    st.error(str(e))

# ═══════════════════════════════════════════════
# TAB 4 — MOVING AVERAGE
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
                df = get_single_pair_history(ma_base, ma_target, str(ma_start), str(ma_end))
                if df.empty:
                    st.error("No data. Try a wider range.")
                else:
                    plot_df = df.copy()
                    if show_7  and len(df) >= 7:  plot_df["MA 7D"]  = df["Rate"].rolling(7).mean()
                    if show_30 and len(df) >= 30: plot_df["MA 30D"] = df["Rate"].rolling(30).mean()

                    st.markdown(section_label("Rate + Moving Averages", f"{ma_base} / {ma_target}"), unsafe_allow_html=True)
                    st.line_chart(plot_df, use_container_width=True, height=320)

                    rate  = df["Rate"]
                    last  = rate.iloc[-1]; first = rate.iloc[0]
                    r7    = rate.tail(7).mean()
                    r30   = rate.tail(30).mean() if len(rate) >= 30 else None
                    trend = "Upward" if last > first else "Downward"
                    tclr  = "#2A6A2A" if last > first else "#8A1A1A"
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

                    if show_7 and show_30:
                        signal = detect_ma_crossover(df)
                        if signal == "golden":
                            alert_ok("Golden Cross detected: 7-day MA crossed above 30-day MA — potential bullish signal.")
                        elif signal == "death":
                            alert_warn("Death Cross detected: 7-day MA crossed below 30-day MA — potential bearish signal.")
                        elif signal is None and len(df) >= 30:
                            alert_info("No crossover event detected in the latest window.")
            except APIError as e:
                st.error(str(e))

# ═══════════════════════════════════════════════
# TAB 5 — CURRENCY BASKET
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
                              default=["EUR", "GBP", "JPY", "AUD"], key="bk_curs")

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
            alert_ok("Allocation balanced at 100%.")
        elif total_pct > 100:
            alert_warn(f"Total is {total_pct:.1f}% — exceeds 100%. Please adjust.")
        else:
            alert_info(f"Total is {total_pct:.1f}% — {100-total_pct:.1f}% unallocated.")

    if st.button("Calculate Basket", key="bk_go"):
        if not bk_curs:
            st.warning("Select at least one currency.")
        elif total_pct <= 0:
            st.warning("Set at least one allocation percentage.")
        else:
            with st.spinner("Fetching live rates..."):
                try:
                    data = get_latest_rate(bk_base, bk_curs)
                    rates = data["rates"]
                    upd   = data.get("date", "today")
                    results = []
                    total_allocated = 0.0
                    for cur in bk_curs:
                        if cur not in rates:
                            continue
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
                            f"Rate (1 {bk_base})":   f"{rate:.6f}",
                        })

                    st.markdown(section_label("Basket Results", f"Rates from {upd}"), unsafe_allow_html=True)
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
                except APIError as e:
                    st.error(str(e))

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center;margin-top:3rem;padding-top:1.5rem;border-top:1px solid #D8C898;color:#A89060;font-size:0.78rem;">
    Powered by Frankfurter API &nbsp;·&nbsp; Rates updated daily on business days &nbsp;·&nbsp; Not financial advice
</div>
""", unsafe_allow_html=True)
