import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, (total_cash / total_debt) as cash_buffer, current_ratio, (total_debt / enterprise_value) as leverage_stress FROM {table_name} WHERE total_debt > 0 AND total_cash > (total_debt * 1.5) AND current_ratio > 1.2 AND enterprise_value > 0 AND (total_debt / enterprise_value) < 0.5 ORDER BY cash_buffer DESC"""
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
    print("🛡️ The Fortress Balance Sheet (Cash Bulwark)")
    print("Criteria: Cash/Debt > 1.5, Current Ratio > 1.2, Debt < 50% of EV\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
