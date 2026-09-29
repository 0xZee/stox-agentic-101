import sqlite3
import pandas as pd
import sys


def allocation_vs_upside(table_name):
    conn = sqlite3.connect('portfolio.db')
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [row[1] for row in cursor.fetchall()]
    # Fetch allocation and analyst targets
    has_alloc = "allocation" in columns
    query = f"""
    SELECT ticker, {"allocation, " if has_alloc else ""} upside, consensus, opinions FROM {table_name} ORDER BY upside DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No allocations found in the stox table.")
        return

    print("🎯 Portfolio Allocation vs. Analyst Upside")
    print("Identifying potential 'underweight' gems in your current holdings\n")
    
    # Format for display
    df['upside'] = (df['upside'] * 100).round(2).astype(str) + '%'
    
    # Show top 20 by upside
    print(df.head(20).to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            allocation_vs_upside(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
