import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, (market_cap / total_revenue) as ps_ratio, rev_growth, (total_cash / ABS(oper_cashflow)) as runway_years FROM {table_name} WHERE total_revenue > 0 AND (market_cap / total_revenue) > 5.0 AND rev_growth > 0.30 AND oper_cashflow < 0 AND (total_cash / ABS(oper_cashflow)) > 2 ORDER BY rev_growth DESC"""
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
    print("🧪 The AI/Innovation Speculator (High Risk/High Reward)")
    print("Criteria: High P/S (> 5), Rev Growth > 30%, 2+ Year Cash Runway\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
