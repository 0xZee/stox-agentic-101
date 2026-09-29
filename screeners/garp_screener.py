import sqlite3
import pandas as pd
import sys


def garp_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"""
    SELECT 
        ticker, 
        name, 
        peg, 
        roe, 
        rev_growth, 
        pe_forward 
    FROM {table_name} 
    WHERE peg > 0 AND peg < 1.5 
      AND roe > 0.15 
      AND rev_growth > 0.10
    ORDER BY peg ASC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("💎 GARP Screener (Growth at a Reasonable Price)")
    print("Criteria: PEG < 1.5, ROE > 15%, Revenue Growth > 10%\n")
    if df.empty:
        print("No matches found.")
    else:
        # Format percentages for display
        df['roe'] = (df['roe'] * 100).round(2).astype(str) + '%'
        df['rev_growth'] = (df['rev_growth'] * 100).round(2).astype(str) + '%'
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            garp_screener(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
