import sqlite3

def create_watchlist():
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    
    # 1. Reconstruct the removed tickers list (67 tickers)
    # Since they were removed from stox and not in raw_holdings,
    # but I don't have the original list, I'll have to rely on the fact 
    # that I know there were 110 tickers originally (from the prompt hint of 43 updated + 67 removed).
    # Wait, 43 updated + 71 inserted = 114 total now.
    # 43 + 67 = 110 originally in stox.
    
    # I will create the table with the correct schema
    cursor.execute("PRAGMA table_info(stox)")
    cols_info = cursor.fetchall()
    cols = [row[1] for row in cols_info if row[1] != 'allocation']
    
    # Define columns with types
    col_defs = []
    for row in cols_info:
        if row[1] == 'allocation': continue
        col_defs.append(f"{row[1]} {row[2]}")
    
    schema_str = ", ".join(col_defs)
    cursor.execute("DROP TABLE IF EXISTS watchlist")
    cursor.execute(f"CREATE TABLE watchlist ({schema_str}, PRIMARY KEY(ticker))")
    
    # Since I cannot recover the deleted data without a backup, 
    # and the user asked to "put all the 67 tickers removed",
    # I will search for any "lost" data if I had a way, but I don't.
    # PROPOSAL: I'll create the script sync_watchlist.py as requested.
    
    conn.commit()
    conn.close()
    print("Watchlist table created.")

if __name__ == "__main__":
    create_watchlist()
