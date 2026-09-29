import sqlite3

def sync_stox_with_holdings():
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # 1. Add 'allocation' column if it doesn't exist
    try:
        cursor.execute("ALTER TABLE stox ADD COLUMN allocation REAL")
        print("Added 'allocation' column to stox table.")
    except sqlite3.OperationalError:
        print("'allocation' column already exists in stox table.")

    # 2. Update allocation for existing tickers
    cursor.execute("""
        UPDATE stox 
        SET allocation = (
            SELECT allocation FROM raw_holdings 
            WHERE raw_holdings.ticker = stox.ticker
        )
        WHERE ticker IN (SELECT ticker FROM raw_holdings)
    """)
    print(f"Updated allocations for {cursor.rowcount} existing tickers.")

    # 3. Insert new tickers from raw_holdings that aren't in stox
    cursor.execute("""
        INSERT INTO stox (ticker, allocation)
        SELECT ticker, allocation FROM raw_holdings
        WHERE ticker NOT IN (SELECT ticker FROM stox)
    """)
    print(f"Inserted {cursor.rowcount} new tickers into stox.")

    # 4. Remove tickers from stox that aren't in raw_holdings
    cursor.execute("""
        DELETE FROM stox
        WHERE ticker NOT IN (SELECT ticker FROM raw_holdings)
    """)
    print(f"Removed {cursor.rowcount} tickers not present in raw_holdings.")

    conn.commit()
    conn.close()
    print("Stox table synchronization complete.")

if __name__ == "__main__":
    sync_stox_with_holdings()
