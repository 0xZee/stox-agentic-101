import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, (rev_growth + profit_margin) * 100 as rule_of_40, rev_growth, profit_margin, fcf FROM {table_name} WHERE (rev_growth + profit_margin) > 0.40 AND rev_growth > 0.20 AND fcf > 0 ORDER BY rule_of_40 DESC"""
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
    print("🚀 The Growth Survivor (Rule of 40 Stars)")
    print("Criteria: Rule of 40 > 40%, Revenue Growth > 20%, Positive Free Cash Flow\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
