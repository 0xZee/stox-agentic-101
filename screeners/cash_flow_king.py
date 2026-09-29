import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, (fcf / market_cap) * 100 as fcf_yield, ev_ebitda, profit_margin FROM {table_name} WHERE market_cap > 0 AND (fcf / market_cap) > 0.05 AND ev_ebitda < 15 AND profit_margin > 0 ORDER BY fcf_yield DESC"""
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
    print("💰 The Cash Flow King (FCF Yield)")
    print("Criteria: FCF Yield > 5%, EV/EBITDA < 15, Profitable\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
