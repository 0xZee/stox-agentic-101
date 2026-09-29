import sqlite3
import pandas as pd
import sys


def short_squeeze_hunter(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Criteria for high short interest with oversold technicals or high "days to cover"
    query = f"""
    SELECT 
        ticker, 
        name, 
        short_pct_float, 
        short_ratio as days_to_cover, 
        rsi, 
        perf_1w
    FROM {table_name} 
    WHERE (short_pct_float > 0.10 
       OR days_to_cover > 5)
       AND perf_1w > 0.10
    ORDER BY short_pct_float DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("🩳 Short Squeeze Candidate Hunter")
    print("Criteria: (Short % of Float > 10% or Days to Cover > 5) AND 1W Perf > 10%\n")
    if df.empty:
        print("No candidates found.")
    else:
        # Format percentages
        df['short_pct_float'] = (df['short_pct_float'] * 100).round(2).astype(str) + '%'
        df['perf_1w'] = (df['perf_1w'] * 100).round(2).astype(str) + '%'
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            short_squeeze_hunter(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
