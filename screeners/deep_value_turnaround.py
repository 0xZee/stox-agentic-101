import sqlite3
import pandas as pd
import sys
import numpy as np

def run_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""SELECT ticker, name, price, (SQRT(22.5 * CASE WHEN eps_trailing > 0 THEN eps_trailing ELSE 0 END * CASE WHEN book_value > 0 THEN book_value ELSE 0 END)) as graham_number, f_score, oper_cashflow FROM {table_name} WHERE eps_trailing > 0 AND book_value > 0 AND price < (SQRT(22.5 * eps_trailing * book_value)) AND f_score >= 6 AND oper_cashflow > 0 ORDER BY (price / (SQRT(22.5 * eps_trailing * book_value))) ASC"""
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
    print("📉 The Deep Value Turnaround (Graham Number Edge)")
    print("Criteria: Price < Graham Number, F-Score >= 6, Positive Operating Cash Flow\n")
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        run_screener(t)
