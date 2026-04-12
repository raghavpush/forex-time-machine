# ─────────────────────────────────────────────
#  utils/charts.py  —  Forex Time Machine
#  Chart rendering + stats helper functions
# ─────────────────────────────────────────────

import pandas as pd
import streamlit as st


# ── STAT CARDS ───────────────────────────────────────────────────────────────

def render_stat_grid(stats: list[dict]) -> None:
    """
    Renders a row of stat boxes.
    Each dict: {"label": str, "value": str, "cls": str}
    cls options: "high", "low", "avg", "chg"
    """
    boxes = "".join(
        f'<div class="stat-box {s["cls"]}">'
        f'<div class="stat-label">{s["label"]}</div>'
        f'<div class="stat-value">{s["value"]}</div>'
        f'</div>'
        for s in stats
    )
    st.markdown(f'<div class="stat-grid">{boxes}</div>', unsafe_allow_html=True)


# ── VOLATILITY BAR ────────────────────────────────────────────────────────────

def volatility_index(series: pd.Series) -> int:
    """Returns a 0-100 volatility score based on coefficient of variation."""
    if series.mean() == 0:
        return 0
    return min(int((series.std() / series.mean()) * 1000), 100)


def render_volatility_bar(score: int) -> str:
    return (
        f'<div class="vol-wrap">'
        f'<div class="stat-label">Volatility Index</div>'
        f'<div class="vol-track"><div class="vol-fill" style="width:{score}%"></div></div>'
        f'<div style="color:#8A7050;font-size:0.72rem;margin-top:3px;">{score} / 100</div>'
        f'</div>'
    )


# ── ALERT BANNERS ─────────────────────────────────────────────────────────────

def alert_warn(msg: str) -> None:
    st.markdown(f'<div class="alert-warn">{msg}</div>', unsafe_allow_html=True)

def alert_ok(msg: str) -> None:
    st.markdown(f'<div class="alert-ok">{msg}</div>', unsafe_allow_html=True)

def alert_info(msg: str) -> None:
    st.markdown(f'<div class="alert-info">{msg}</div>', unsafe_allow_html=True)


# ── CARD WRAPPERS ─────────────────────────────────────────────────────────────

def card(header: str, body_html: str) -> str:
    return (
        f'<div class="card">'
        f'<div class="card-header">{header}</div>'
        f'{body_html}'
        f'</div>'
    )


def section_label(text: str, tag: str = "") -> str:
    tag_html = f'<span class="tag">{tag}</span>' if tag else ""
    return f'<div class="section-label">{text} {tag_html}</div>'


# ── HEATMAP ROW BUILDER ───────────────────────────────────────────────────────

def heatmap_row(pair: str, op: float, cl: float, hi: float, lo: float, avg: float) -> str:
    chg  = cl - op
    pct  = (chg / op) * 100 if op else 0
    inten = min(abs(pct) * 8, 60)
    bg   = f"rgba(50,140,50,{inten/200})" if pct >= 0 else f"rgba(180,40,40,{inten/200})"
    cls  = "gain" if pct >= 0 else "loss"
    sign = "+" if pct >= 0 else ""
    return (
        f'<tr style="background:{bg}">'
        f'<td style="font-weight:600;color:#2C2010;">{pair}</td>'
        f'<td>{op:.4f}</td><td>{cl:.4f}</td>'
        f'<td class="{cls}">{sign}{chg:.4f}</td>'
        f'<td class="{cls}">{sign}{pct:.2f}%</td>'
        f'<td class="gain">{hi:.4f}</td>'
        f'<td class="loss">{lo:.4f}</td>'
        f'<td class="neutral">{avg:.4f}</td>'
        f'</tr>'
    )


# ── MOVING AVERAGE SIGNALS ────────────────────────────────────────────────────

def detect_ma_crossover(df: pd.DataFrame, rate_col: str = "Rate") -> str | None:
    """
    Returns 'golden', 'death', or None based on latest MA crossover.
    Requires at least 30 rows.
    """
    if len(df) < 30:
        return None
    ma7  = df[rate_col].rolling(7).mean().dropna()
    ma30 = df[rate_col].rolling(30).mean().dropna()
    com  = ma7.index.intersection(ma30.index)
    if len(com) < 2:
        return None
    dn = ma7[com[-1]]  - ma30[com[-1]]
    dp = ma7[com[-2]]  - ma30[com[-2]]
    if dp < 0 and dn >= 0:
        return "golden"
    if dp > 0 and dn <= 0:
        return "death"
    return None
