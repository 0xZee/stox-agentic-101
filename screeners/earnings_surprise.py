import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, day_change * 100 as day_perf, upside * 100 as analyst_upside, next_earnings FROM {table_name} WHERE day_change > 0.03 AND upside > 0.15 ORDER BY day_perf DESC"""
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
    print("⚡ The Earnings Surprise (Pre-Hype)")
    print("Criteria: Day Change > 3%, Analyst Upside > 15%\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
