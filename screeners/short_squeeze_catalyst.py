import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, short_pct_float * 100 as short_intensity, (volume / avg_vol_3m) as vol_shock, short_ratio FROM {table_name} WHERE short_pct_float > 0.15 AND (volume / avg_vol_3m) > 1.5 ORDER BY short_intensity DESC"""
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
    print("🧨 The Short Squeeze Catalyst (Squeeze Probability)")
    print("Criteria: Short Intensity > 15%, Volume Shock > 1.5x, High Short Ratio\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
