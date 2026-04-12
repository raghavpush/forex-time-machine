# ─────────────────────────────────────────────
#  config.py  —  Forex Time Machine
#  All constants, settings, and configuration
# ─────────────────────────────────────────────

APP_TITLE    = "Forex Time Machine"
APP_ICON     = "💱"
APP_SUBTITLE = "Historical rates · Live conversion · Trend analysis · Currency basket"

# Frankfurter API (free, no key required)
API_BASE = "https://api.frankfurter.app"
TIMEOUT  = 10  # seconds

# Supported currencies
ALL_CURRENCIES = [
    "USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF",
    "CNY", "SGD", "HKD", "NOK", "SEK", "NZD", "MXN", "ZAR",
    "BRL", "TRY", "KRW", "THB",
]

CURRENCY_NAMES = {
    "USD": "US Dollar",         "EUR": "Euro",
    "GBP": "British Pound",     "INR": "Indian Rupee",
    "JPY": "Japanese Yen",      "AUD": "Australian Dollar",
    "CAD": "Canadian Dollar",   "CHF": "Swiss Franc",
    "CNY": "Chinese Yuan",      "SGD": "Singapore Dollar",
    "HKD": "Hong Kong Dollar",  "NOK": "Norwegian Krone",
    "SEK": "Swedish Krona",     "NZD": "New Zealand Dollar",
    "MXN": "Mexican Peso",      "ZAR": "South African Rand",
    "BRL": "Brazilian Real",    "TRY": "Turkish Lira",
    "KRW": "South Korean Won",  "THB": "Thai Baht",
}

CURRENCY_FLAGS = {
    "USD": "🇺🇸", "EUR": "🇪🇺", "GBP": "🇬🇧", "INR": "🇮🇳",
    "JPY": "🇯🇵", "AUD": "🇦🇺", "CAD": "🇨🇦", "CHF": "🇨🇭",
    "CNY": "🇨🇳", "SGD": "🇸🇬", "HKD": "🇭🇰", "NOK": "🇳🇴",
    "SEK": "🇸🇪", "NZD": "🇳🇿", "MXN": "🇲🇽", "ZAR": "🇿🇦",
    "BRL": "🇧🇷", "TRY": "🇹🇷", "KRW": "🇰🇷", "THB": "🇹🇭",
}

MAJOR_CURRENCIES = ["USD", "EUR", "GBP", "INR", "JPY", "AUD", "CAD", "CHF", "SGD"]

# Quick date range presets (label → days)
DATE_PRESETS = [
    ("7 Days",   7),
    ("30 Days",  30),
    ("90 Days",  90),
    ("6 Months", 180),
    ("1 Year",   365),
]
