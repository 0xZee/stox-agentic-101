import sqlite3
import sys
from ticker_info import get_ticker_info

# Mapping of (Category, Key in ticker_info) -> (DB Column Name, SQL Type)
METRIC_MAP = {
    # Profile
    ("🏢 Company Profile", "Symbol"): ("ticker", "TEXT PRIMARY KEY"),
    ("🏢 Company Profile", "Long Name"): ("name", "TEXT"),
    ("🏢 Company Profile", "Sector"): ("sector", "TEXT"),
    ("🏢 Company Profile", "Industry"): ("industry", "TEXT"),
    ("🏢 Company Profile", "Full Time Employees"): ("employees", "REAL"),
    ("🏢 Company Profile", "City"): ("city", "TEXT"),
    ("🏢 Company Profile", "State"): ("state", "TEXT"),
    ("🏢 Company Profile", "Country"): ("country", "TEXT"),
    ("🏢 Company Profile", "Website"): ("website", "TEXT"),

    # Market Data
    ("📊 Market Data", "Market State"): ("market_state", "TEXT"),
    ("📊 Market Data", "Pre-Market Change %"): ("pre_market_chg_pct", "REAL"),
    ("📊 Market Data", "Current Price"): ("price", "REAL"),
    ("📊 Market Data", "Previous Close"): ("prev_close", "REAL"),
    ("📊 Market Data", "Open"): ("open", "REAL"),
    ("📊 Market Data", "Day Low"): ("day_low", "REAL"),
    ("📊 Market Data", "Day High"): ("day_high", "REAL"),
    ("📊 Market Data", "52W Low"): ("fifty_two_w_low", "REAL"),
    ("📊 Market Data", "52W High"): ("fifty_two_w_high", "REAL"),
    ("📊 Market Data", "Bid"): ("bid", "REAL"),
    ("📊 Market Data", "Ask"): ("ask", "REAL"),
    ("📊 Market Data", "Market Cap"): ("market_cap", "REAL"),
    ("📊 Market Data", "Enterprise Value"): ("enterprise_value", "REAL"),
    ("📊 Market Data", "52 Week Range"): ("fifty_two_w_range", "TEXT"),

    # Volume
    ("🔊 Volume & Liquidity", "Volume"): ("volume", "REAL"),
    ("🔊 Volume & Liquidity", "Avg Vol (10d)"): ("avg_vol_10d", "REAL"),
    ("🔊 Volume & Liquidity", "Avg Vol (3m)"): ("avg_vol_3m", "REAL"),
    ("🔊 Volume & Liquidity", "Avg Daily Vol (10d)"): ("avg_daily_vol_10d", "REAL"),
    ("🔊 Volume & Liquidity", "Bid Size"): ("bid_size", "REAL"),
    ("🔊 Volume & Liquidity", "Ask Size"): ("ask_size", "REAL"),

    # Performance
    ("📈 Price Performance", "1 Week"): ("perf_1w", "REAL"),
    ("📈 Price Performance", "1 Month"): ("perf_1m", "REAL"),
    ("📈 Price Performance", "3 Months"): ("perf_3m", "REAL"),
    ("📈 Price Performance", "6 Months"): ("perf_6m", "REAL"),
    ("📈 Price Performance", "Year to Date"): ("perf_ytd", "REAL"),
    ("📈 Price Performance", "52W Change %"): ("perf_52w", "REAL"),
    ("📈 Price Performance", "S&P 52W Change %"): ("perf_sp52w", "REAL"),
    ("📈 Price Performance", "Beta (5Y)"): ("beta", "REAL"),

    # Technicals
    ("🌡️ Technical Indicators", "RSI (14d)"): ("rsi", "REAL"),
    ("🌡️ Technical Indicators", "Volatility (Ann)"): ("volatility", "REAL"),
    ("🌡️ Technical Indicators", "From 52W High"): ("dist_52w_high", "REAL"),
    ("🌡️ Technical Indicators", "From 52W Low"): ("dist_52w_low", "REAL"),
    ("🌡️ Technical Indicators", "50 Day Average"): ("avg_50d", "REAL"),
    ("🌡️ Technical Indicators", "200 Day Average"): ("avg_200d", "REAL"),
    ("🌡️ Technical Indicators", "50D Avg Change"): ("avg_50d_chg", "REAL"),
    ("🌡️ Technical Indicators", "200D Avg Change"): ("avg_200d_chg", "REAL"),

    # Valuation
    ("⚖️ Valuation Multiples", "Trailing P/E"): ("pe_trailing", "REAL"),
    ("⚖️ Valuation Multiples", "Forward P/E"): ("pe_forward", "REAL"),
    ("⚖️ Valuation Multiples", "PEG Ratio"): ("peg", "REAL"),
    ("⚖️ Valuation Multiples", "Price to Sales"): ("p_sales", "REAL"),
    ("⚖️ Valuation Multiples", "Price to Book"): ("p_book", "REAL"),
    ("⚖️ Valuation Multiples", "EV to Revenue"): ("ev_rev", "REAL"),
    ("⚖️ Valuation Multiples", "EV to EBITDA"): ("ev_ebitda", "REAL"),
    ("⚖️ Valuation Multiples", "Book Value"): ("book_value", "REAL"),

    # Efficiency
    ("🔄 Efficiency & Return", "Return on Equity"): ("roe", "REAL"),
    ("🔄 Efficiency & Return", "Return on Assets"): ("roa", "REAL"),
    ("🔄 Efficiency & Return", "Gross Margins"): ("gross_margin", "REAL"),
    ("🔄 Efficiency & Return", "Operating Margins"): ("oper_margin", "REAL"),
    ("🔄 Efficiency & Return", "Profit Margin"): ("profit_margin", "REAL"),
    ("🔄 Efficiency & Return", "EBITDA Margins"): ("ebitda_margin", "REAL"),
    ("🔄 Efficiency & Return", "Revenue per Share"): ("rev_per_share", "REAL"),
    ("🔄 Efficiency & Return", "Cash per Share"): ("cash_per_share", "REAL"),

    # Growth
    ("🚀 Growth Estimates", "Revenue Growth"): ("rev_growth", "REAL"),
    ("🚀 Growth Estimates", "Earnings Growth"): ("earn_growth", "REAL"),
    ("🚀 Growth Estimates", "Quarterly Earn Growth"): ("earn_growth_q", "REAL"),
    ("🚀 Growth Estimates", "Trailing EPS"): ("eps_trailing", "REAL"),
    ("🚀 Growth Estimates", "Forward EPS"): ("eps_forward", "REAL"),
    ("🚀 Growth Estimates", "EPS Next Year"): ("eps_next_year", "REAL"),

    # Financial Health
    ("🏥 Financial Health", "Total Cash"): ("total_cash", "REAL"),
    ("🏥 Financial Health", "Total Debt"): ("total_debt", "REAL"),
    ("🏥 Financial Health", "Operating Cashflow"): ("oper_cashflow", "REAL"),
    ("🏥 Financial Health", "Free Cashflow"): ("fcf", "REAL"),
    ("🏥 Financial Health", "Current Ratio"): ("current_ratio", "REAL"),
    ("🏥 Financial Health", "Quick Ratio"): ("quick_ratio", "REAL"),
    ("🏥 Financial Health", "Debt to Equity"): ("debt_equity", "REAL"),
    ("🏥 Financial Health", "Revenue"): ("total_revenue", "REAL"),

    # Share Statistics
    ("🌊 Share Statistics", "Shares Outstanding"): ("shares_out", "REAL"),
    ("🌊 Share Statistics", "Float Shares"): ("float_shares", "REAL"),
    ("🌊 Share Statistics", "Implied Shares"): ("implied_shares", "REAL"),
    ("🌊 Share Statistics", "Held by Insiders"): ("held_insiders", "REAL"),
    ("🌊 Share Statistics", "Held by Institutions"): ("held_institutions", "REAL"),

    # Short Squeeze
    ("🩳 Short Squeeze Indicators", "Short Ratio"): ("short_ratio", "REAL"),
    ("🩳 Short Squeeze Indicators", "Short % of Float"): ("short_pct_float", "REAL"),
    ("🩳 Short Squeeze Indicators", "Short % of Shares"): ("short_pct_shares", "REAL"),
    ("🩳 Short Squeeze Indicators", "Short % Change"): ("short_pct_chg", "REAL"),
    ("🩳 Short Squeeze Indicators", "Shares Short"): ("shares_short", "REAL"),
    ("🩳 Short Squeeze Indicators", "Prior Month Short"): ("short_prior", "REAL"),

    # Dividends
    ("💰 Dividends", "Dividend Yield"): ("div_yield", "REAL"),
    ("💰 Dividends", "Dividend Rate"): ("div_rate", "REAL"),
    ("💰 Dividends", "Payout Ratio"): ("payout_ratio", "REAL"),
    ("💰 Dividends", "5 Yr Avg Yield"): ("div_yield_5y", "REAL"),
    ("💰 Dividends", "Trailing Div Yield"): ("div_yield_trailing", "REAL"),
    ("💰 Dividends", "Trailing Div Rate"): ("div_rate_trailing", "REAL"),
    ("💰 Dividends", "Next Earnings"): ("next_earnings", "TEXT"),
    ("💰 Dividends", "Dividend Date"): ("div_date", "TEXT"),
    ("💰 Dividends", "Ex-Dividend Date"): ("ex_div_date", "TEXT"),

    # Analyst
    ("🎯 Analyst Sentiment", "Analyst Consensus"): ("consensus", "TEXT"),
    ("🎯 Analyst Sentiment", "Number of Opinions"): ("opinions", "REAL"),
    ("🎯 Analyst Sentiment", "Target Low"): ("target_low", "REAL"),
    ("🎯 Analyst Sentiment", "Target High"): ("target_high", "REAL"),
    ("🎯 Analyst Sentiment", "Target Mean"): ("target_mean", "REAL"),
    ("🎯 Analyst Sentiment", "Target Median"): ("target_median", "REAL"),
    ("🎯 Analyst Sentiment", "Implied Upside"): ("upside", "REAL"),

    # Risk
    ("🛡️ Risk & Governance", "Overall Risk (1-10)"): ("risk_overall", "REAL"),
    ("🛡️ Risk & Governance", "Audit Risk"): ("risk_audit", "REAL"),
    ("🛡️ Risk & Governance", "Board Risk"): ("risk_board", "REAL"),
    ("🛡️ Risk & Governance", "Compensation Risk"): ("risk_comp", "REAL"),
    ("🛡️ Risk & Governance", "Shareholder Rights"): ("risk_rights", "REAL"),
    ("🛡️ Risk & Governance", "ESG Score"): ("esg_score", "TEXT"),

    # Scores
    ("💎 Premium Analyst Metrics", "Altman Z-Score"): ("z_score", "REAL"),
    ("💎 Premium Analyst Metrics", "Piotroski F-Score"): ("f_score", "REAL"),
    ("💎 Premium Analyst Metrics", "Altman Status"): ("altman_status", "TEXT"),
    ("💎 Premium Analyst Metrics", "F-Score Rating"): ("f_score_rating", "TEXT"),

    # Portfolio
    ("💼 Portfolio", "Allocation"): ("allocation", "REAL"),
}

def clean_val(val):
    if val is None or val == "N/A":
        return None
    if isinstance(val, str):
        # Check if it's a percentage (e.g., "+10.5%")
        is_pct = "%" in val
        # Remove %, +, $, and whitespace
        clean = val.replace("%", "").replace("+", "").replace("$", "").replace(",", "").strip()
        try:
            num = float(clean)
            return num / 100.0 if is_pct else num
        except ValueError:
            return val
    return val

def sync_schema(conn):
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(stox)")
    existing_cols = {row[1] for row in cursor.fetchall()}
    
    for _, (col_name, col_type) in METRIC_MAP.items():
        if col_name not in existing_cols:
            print(f"➕ Adding column: {col_name} ({col_type})")
            # SQLite ALTER TABLE doesn't support PRIMARY KEY on add,
            # but ticker is already handled or will be handled carefully.
            cursor.execute(f"ALTER TABLE stox ADD COLUMN {col_name} {col_type.split('PRIMARY')[0].strip()}")
    
    # Add calculated 'day_change' if missing
    if "day_change" not in existing_cols:
        cursor.execute("ALTER TABLE stox ADD COLUMN day_change REAL")
    conn.commit()

def add_ticker(symbol):
    print(f"🚀 Fetching data for {symbol}...")
    data = get_ticker_info(symbol)
    if "error" in data:
        print(f"❌ Error: {data['error']}")
        return

    metrics = data["metrics"]
    db_data = {}
    
    for (cat, key), (col_name, _) in METRIC_MAP.items():
        raw_val = metrics.get(cat, {}).get(key)
        db_data[col_name] = clean_val(raw_val)

    # Calculated metrics
    price = db_data.get("price")
    prev_close = db_data.get("prev_close")
    if price and prev_close:
        db_data["day_change"] = (price / prev_close) - 1

    # Database Operations
    conn = sqlite3.connect("portfolio.db")
    sync_schema(conn)
    
    columns = ", ".join(db_data.keys())
    placeholders = ", ".join(["?"] * len(db_data))
    values = list(db_data.values())
    
    sql = f"INSERT OR REPLACE INTO stox ({columns}) VALUES ({placeholders})"
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print(f"✅ {symbol} successfully added/updated in portfolio.db")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python add_to_portfolio.py <TICKER>")
    else:
        add_ticker(sys.argv[1].upper())
