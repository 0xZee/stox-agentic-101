import sqlite3
import pandas as pd
import sys


def volume_price_surge(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Focus on volume spikes relative to 3m average, positive performance, and being above 50D MA
    query = f"""
    SELECT 
        ticker, 
        name, 
        volume, 
        avg_vol_3m,
        ROUND(CAST(volume AS REAL) / avg_vol_3m, 2) as vol_rel_avg,
        price,
        avg_50d,
        perf_1w,
        perf_1m,
        held_institutions
    FROM {table_name} 
    WHERE volume > (avg_vol_3m * 1.5)
      AND price > avg_50d
      AND perf_1w > 0
    ORDER BY vol_rel_avg DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("🔥 Volume & Price Momentum Surge")
    print("Criteria: Volume > 1.5x Avg(3m), Price > 50D MA, Positive 1W Performance\n")
    
    if df.empty:
        print("No surge candidates found today.")
    else:
        # Format for display
        df['perf_1w'] = (df['perf_1w'] * 100).round(2).astype(str) + '%'
        df['perf_1m'] = (df['perf_1m'] * 100).round(2).astype(str) + '%'
        df['held_institutions'] = (df['held_institutions'] * 100).round(2).astype(str) + '%'
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            volume_price_surge(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
