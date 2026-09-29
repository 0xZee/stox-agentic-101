# 📈 Portfolio Intelligence

A lightweight, high-performance quantitative research and portfolio tracking toolkit built in Python and SQLite. Designed for high-conviction, data-driven equity and options analysis.

---

## 🚀 Key Features

- **Portfolio & Watchlist Management**: SQLite-backed local datastore (`portfolio.db`) tracking daily changes, volume, market cap, and performance history.
- **Deep Fundamental Analysis**: Automatic calculation of valuation ratios (P/E, PEG, EV/EBITDA), growth rates, and financial health scores (**Altman Z-Score** and **Piotroski F-Score**).
- **Macro & Sector Snapshots**: Multi-threaded market monitor for major indices (SPY, QQQ, IWM, DIA, VIX), treasury yields (TNX), commodities, and 11 SPDR sectors.
- **Options Intelligence**: Implied Volatility (IV), Put/Call ratios, volume/open-interest skew, and near-term chain analysis.
- **Agentic Workflow Ready**: Native rules and mandates codified in `AGENTS.md` for AI coding assistants (Gemini CLI, Cursor, Claude Code).

---

## 📂 Project Structure

```text
├── market_snapshot.py       # Macro indices, sector heatmaps, and portfolio movers
├── ticker_info.py           # Deep-dive fundamental fetcher & scoring engine
├── analyze_ticker.py        # Database-driven ticker analysis and metrics report
├── ticker_options.py        # Options chain, Greeks, and IV metrics
├── add_to_portfolio.py      # Adds or updates individual tickers in portfolio.db
├── update_db.py             # Batch updates all holdings in the 'stox' table
├── sync_watchlist.py        # Refreshes metrics for all monitored watchlist tickers
├── setup_watchlist.py       # Watchlist table schema builder
├── run_strategies.py        # Strategy execution runner
├── AGENTS.md                # System instructions and heuristics for AI assistants
└── requirements.txt         # Project dependencies
```

---

## 🛠️ Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/<your-username>/stox.git
cd stox
```

### 2. Create and activate a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## 📊 Quick Start

### 1. Initialize Your Database
`portfolio.db` is excluded from version control to protect your private holdings data. To add your first stock and initialize the database:

```bash
# Add stocks to your holdings ('stox' table)
python add_to_portfolio.py AAPL
python add_to_portfolio.py NVDA

# Initialize the watchlist schema
python setup_watchlist.py

# Add tickers to your watchlist
python sync_watchlist.py MSFT
```

### 2. Daily Market Routine
```bash
# Get overall market, sector, and portfolio status
python market_snapshot.py

# Batch refresh all portfolio and watchlist metrics
python update_db.py && python sync_watchlist.py
```

### 3. Single-Stock Research
```bash
# Fetch live fundamentals, margins, and Altman Z / Piotroski F scores
python ticker_info.py PLTR

# Inspect stored fundamentals and historical performance
python analyze_ticker.py PLTR

# Analyze near-term options chain and Implied Volatility
python ticker_options.py PLTR
```

---

## 🔒 Configuration & Security
- Local database files (`portfolio.db`, `*.db`) and `.env` credentials are excluded by `.gitignore`.
- Market data is pulled in real-time via `yfinance`.
