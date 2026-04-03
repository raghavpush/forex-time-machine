# Forex Time Machine

A Streamlit web app for exploring historical exchange rates, live currency conversion, trend analysis, and multi-currency portfolio planning.

---

## Features

| Tab | Description |
|-----|-------------|
| Historical Rates | Fetch and chart exchange rates for any date range with stats and volatility index |
| Live Converter | Convert any amount in real time with a full reference table and cross rates |
| Rate Heatmap | Color-coded performance table showing gains and losses across multiple pairs |
| Moving Average | Overlay 7-day and 30-day MAs with Golden Cross / Death Cross signal detection |
| Currency Basket | Allocate a budget across multiple currencies by percentage using live rates |

---

## Tech Stack

- **Frontend / UI** — [Streamlit](https://streamlit.io)
- **Rates API** — [Frankfurter API](https://www.frankfurter.app) (free, no key required)
- **Data** — [pandas](https://pandas.pydata.org)
- **HTTP** — [requests](https://docs.python-requests.org)

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/forex-time-machine.git
cd forex-time-machine
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python -m streamlit run app.py
```

The app opens at `http://localhost:8501` in your browser.

---

## Project Structure

```
forex-time-machine/
├── app.py               # Main Streamlit application
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Requirements

```
streamlit
requests
pandas
```

Python 3.8 or higher recommended.

---

## Screenshots

> Add screenshots here after running the app.

---

## API Reference

This project uses the [Frankfurter API](https://www.frankfurter.app) — a free, open-source exchange rate API backed by the European Central Bank.

| Endpoint | Usage |
|----------|-------|
| `/latest` | Current rates |
| `/{date}..{date}` | Historical range |

No API key or account required.

---

## Supported Currencies

USD, EUR, GBP, INR, JPY, AUD, CAD, CHF, CNY, SGD, HKD, NOK, SEK, NZD, MXN, ZAR, BRL, TRY, KRW, THB

---

## Notes

- Rates are updated once daily on business days by the European Central Bank.
- Weekends and public holidays may not have data — the API returns the nearest available date.
- This app is for informational purposes only and does not constitute financial advice.

---

## License

MIT License. Free to use and modify.
