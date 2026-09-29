import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, dist_52w_high, rsi, upside * 100 as analyst_upside FROM {table_name} WHERE dist_52w_high < -40 AND rsi < 35 AND upside > 0.20 ORDER BY upside DESC"""
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
    print("📉 The Contrarian Bounce (Oversold Reversal)")
    print("Criteria: Drawdown > 40%, RSI < 35, Analyst Upside > 20%\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
