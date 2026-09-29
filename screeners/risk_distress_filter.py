import sqlite3
import pandas as pd
import sys


def risk_distress_filter(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Filter for companies in financial distress or with weak quality scores
    query = f"""
    SELECT 
        ticker, 
        name, 
        altman_status, 
        f_score, 
        debt_equity, 
        current_ratio
    FROM {table_name} 
    WHERE altman_status = 'Distress' 
       OR f_score <= 3 
       OR debt_equity > 2.0
    ORDER BY f_score ASC, debt_equity DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("⚠️ Risk & Financial Distress Filter")
    print("Flagging: Altman Distress, F-Score <= 3, or Debt/Equity > 2.0\n")
    if df.empty:
        print("No high-risk companies identified. (All clear!)")
    else:
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            risk_distress_filter(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
