import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, price, avg_50d, avg_200d, (perf_52w / perf_sp52w) as relative_momentum FROM {table_name} WHERE price > avg_200d AND avg_50d > avg_200d AND perf_52w > 0 AND perf_sp52w > 0 AND (perf_52w / perf_sp52w) > 1.0 ORDER BY relative_momentum DESC"""
    try:
        df = pd.read_sql_query(query, conn)
        print(f"\n--- {{table_name.upper()}} ---")
        if df.empty:
            print("No matches found.")
        else:
            print(df.to_string(index=False))
    except Exception as e:
        print(f"Error on {{table_name}}: {{e}}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("📈 The Momentum Breakout (MA Golden Cross)")
    print("Criteria: Price > 200D MA, 50D MA > 200D MA, Outperforming S&P 500\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
