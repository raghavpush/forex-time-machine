# 💱 Forex Time Machine

> Travel back in time to see how currency rates changed — pick any date range, compare multiple currencies, and download the data!

---

## ✨ Features

- 📅 **Preset date buttons** — Last 7 days, 30 days, 6 months, 1 year
- 🌍 **Multi currency compare** — Compare base currency against multiple targets at once
- 📊 **Chart type toggle** — Switch between Line, Bar, and Area charts
- 🔔 **Rate alert** — Set a threshold and get notified if rate dropped below it
- 📈 **Quick stats** — Highest, Lowest, Average, and Total Change for each currency pair
- 📥 **Download CSV** — Export data with a smart filename
- 🌙 **Dark / Light mode** — Toggle from the sidebar

---

## 🖼️ Preview

```
From: USD  →  To: INR, EUR, GBP
Date Range: Last 30 days
Chart: Area | Stats | Alert | Download
```

---

## 🚀 Run Locally

```bash
git clone https://github.com/raghavpush/forex-time-machine
cd forex-time-machine
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Deploy on Streamlit Cloud

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Select this repo and deploy!

---

## 🌍 Supported Currencies

| Code | Currency |
|------|----------|
| USD  | US Dollar |
| INR  | Indian Rupee |
| EUR  | Euro |
| GBP  | British Pound |
| JPY  | Japanese Yen |
| AUD  | Australian Dollar |
| CAD  | Canadian Dollar |
| CHF  | Swiss Franc |
| CNY  | Chinese Yuan |
| SGD  | Singapore Dollar |

---

## 🛠️ Built With

- [Streamlit](https://streamlit.io) — UI framework
- [Pandas](https://pandas.pydata.org) — Data handling
- [Frankfurter API](https://frankfurter.app) — Free historical exchange rates, no API key needed

---

## 📁 File Structure

```
forex-time-machine/
│
├── app.py            # Main Streamlit app
├── requirements.txt  # Dependencies
└── README.md         # This file
```

---

## 🤝 Contributing

Pull requests are welcome! Feel free to open an issue for suggestions or bugs.

---

## 📄 License

MIT — free to use and modify.