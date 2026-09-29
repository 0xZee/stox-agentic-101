import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, (held_institutions / held_insiders) as inst_support, held_institutions, (shares_short / shares_out) as short_pct_out FROM {table_name} WHERE held_insiders > 0 AND (held_institutions / held_insiders) > 10 AND held_institutions > 0.50 AND shares_out > 0 AND (shares_short / shares_out) < 0.10 ORDER BY inst_support DESC"""
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
    print("🤖 The Smart Money Flow (Institutional Support)")
    print("Criteria: Inst/Insider Ratio > 10, Inst Ownership > 50%, Low Short Interest\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
