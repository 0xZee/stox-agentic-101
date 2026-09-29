import sqlite3
import sys
from add_to_portfolio import METRIC_MAP, clean_val
from ticker_info import get_ticker_info

def sync_watchlist_ticker(symbol):
    print(f"🔄 Syncing watchlist data for {symbol}...")
    data = get_ticker_info(symbol)
    if "error" in data:
        print(f"❌ Error for {symbol}: {data['error']}")
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

    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(watchlist)")
    table_cols = {row[1] for row in cursor.fetchall()}
    
    # Filter db_data to only include columns present in the table
    final_data = {k: v for k, v in db_data.items() if k in table_cols}
    
    columns = ", ".join(final_data.keys())
    placeholders = ", ".join(["?"] * len(final_data))
    values = list(final_data.values())
    
    sql = f"INSERT OR REPLACE INTO watchlist ({columns}) VALUES ({placeholders})"
    conn.execute(sql, values)
    conn.commit()
    conn.close()
    print(f"✅ {symbol} watchlist sync complete.")

def sync_all_watchlist():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM watchlist")
    tickers = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if not tickers:
        print("📭 Watchlist is empty.")
        return

    for ticker in tickers:
        sync_watchlist_ticker(ticker)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        sync_watchlist_ticker(sys.argv[1].upper())
    else:
        sync_all_watchlist()
