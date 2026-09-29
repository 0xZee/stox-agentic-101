import sqlite3
from add_to_portfolio import add_ticker, METRIC_MAP

def fix_schema_and_deduplicate():
    conn = sqlite3.connect("portfolio.db")
    cursor = conn.cursor()
    
    # Get current columns
    cursor.execute("PRAGMA table_info(stox)")
    columns = [row[1] for row in cursor.fetchall()]
    
    if not columns:
        print("❌ stox table does not exist.")
        conn.close()
        return []

    # Prepare schema for new table
    col_defs = []
    for (cat, key), (col_name, col_type) in METRIC_MAP.items():
        if col_name in columns:
            col_defs.append(f"{col_name} {col_type}")
    
    # Add day_change and pre_market_chg_pct if they exist in mapping or were added manually
    if "day_change" not in [c.split()[0] for c in col_defs] and "day_change" in columns:
        col_defs.append("day_change REAL")
    if "pre_market_chg_pct" not in [c.split()[0] for c in col_defs] and "pre_market_chg_pct" in columns:
        col_defs.append("pre_market_chg_pct REAL")

    schema_str = ", ".join(col_defs)
    
    print("🛠️ Fixing schema and deduplicating...")
    cursor.execute(f"CREATE TABLE stox_new ({schema_str})")
    
    col_names_str = ", ".join([c.split()[0] for c in col_defs])
    cursor.execute(f"INSERT OR IGNORE INTO stox_new ({col_names_str}) SELECT {col_names_str} FROM stox")
    
    cursor.execute("DROP TABLE stox")
    cursor.execute("ALTER TABLE stox_new RENAME TO stox")
    
    conn.commit()
    
    # Get unique tickers for update
    cursor.execute("SELECT DISTINCT ticker FROM stox")
    tickers = [row[0] for row in cursor.fetchall() if row[0]]
    conn.close()
    
    print(f"✅ Schema fixed. Found {len(tickers)} unique tickers.")
    return tickers

def batch_generator(iterable, n):
    """Yield successive n-sized chunks from an iterable."""
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]

def update_all_tickers(tickers):
    print(f"🔄 Updating {len(tickers)} tickers in batches of 11...")
    for batch in batch_generator(tickers, 11):
        print(f"📦 Processing Group: {', '.join(batch)}")
        for ticker in batch:
            try:
                add_ticker(ticker)
            except Exception as e:
                print(f"❌ Failed to update {ticker}: {e}")

if __name__ == "__main__":
    tickers = fix_schema_and_deduplicate()
    if tickers:
        update_all_tickers(tickers)
    else:
        print("No tickers to update.")
