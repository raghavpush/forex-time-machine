# ─────────────────────────────────────────────
#  utils/api.py  —  Forex Time Machine
#  All Frankfurter API calls in one place
# ─────────────────────────────────────────────

import requests
import pandas as pd
from config import API_BASE, TIMEOUT


class APIError(Exception):
    """Raised when the Frankfurter API returns an unexpected response."""


def _get(url: str) -> dict:
    """Raw GET with timeout; raises APIError on bad status or missing data."""
    try:
        r = requests.get(url, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.Timeout:
        raise APIError("Request timed out. Please try again.")
    except requests.exceptions.ConnectionError:
        raise APIError("No internet connection or API is unreachable.")
    except Exception as e:
        raise APIError(str(e))


def get_latest_rate(base: str, targets: list[str]) -> dict:
    """
    Returns the latest rates from `base` to each currency in `targets`.
    Response: {"date": "YYYY-MM-DD", "rates": {"EUR": 0.91, ...}}
    """
    to = ",".join(targets)
    data = _get(f"{API_BASE}/latest?from={base}&to={to}")
    if "rates" not in data:
        raise APIError("API did not return rates.")
    return data


def get_historical_rates(base: str, targets: list[str], start: str, end: str) -> pd.DataFrame:
    """
    Returns a DataFrame indexed by date with one column per target currency.
    Dates are parsed as pd.Timestamp.
    """
    to   = ",".join(targets)
    data = _get(f"{API_BASE}/{start}..{end}?from={base}&to={to}")
    if "rates" not in data:
        raise APIError("No data returned for that date range.")
    rows = [{"Date": d, **r} for d, r in data["rates"].items()]
    df   = pd.DataFrame(rows).set_index("Date")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def get_single_pair_history(base: str, target: str, start: str, end: str) -> pd.DataFrame:
    """
    Returns a DataFrame with a single 'Rate' column for one currency pair.
    """
    data = _get(f"{API_BASE}/{start}..{end}?from={base}&to={target}")
    if "rates" not in data:
        raise APIError("No data returned for that date range.")
    rows = [{"Date": d, "Rate": r[target]} for d, r in data["rates"].items() if target in r]
    df   = pd.DataFrame(rows).set_index("Date")
    df.index = pd.to_datetime(df.index)
    df = df.sort_index()
    return df


def get_available_currencies() -> list[str]:
    """Fetches the list of currencies supported by the API."""
    data = _get(f"{API_BASE}/currencies")
    return sorted(data.keys())
