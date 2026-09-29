import sqlite3
import pandas as pd
import sys


def high_margin_tech_recovery(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Focus on high gross margin (moat) + recovering technicals (above 50D, below 200D, positive 1W/1M)
    query = f"""
    SELECT 
        ticker, 
        name, 
        gross_margin, 
        price, 
        avg_50d, 
        avg_200d,
        perf_1w,
        perf_1m,
        rsi
    FROM {table_name} 
    WHERE gross_margin > 0.60
      AND price > avg_50d
      AND price < avg_200d
      AND perf_1w > 0
      AND perf_1m > 0
    ORDER BY gross_margin DESC
    """
    df_stox = pd.read_sql_query(query, conn)
    
    # Also check watchlist
    query_watchlist = query.replace("FROM {table_name}", "FROM {table_name}")
    df_watch = pd.read_sql_query(query_watchlist, conn)
    
    conn.close()
    
    print("📈 High-Margin Technical Recovery Screener")
    print("Criteria: Gross Margin > 60%, Above 50D MA (Early Recovery), Below 200D MA (Still Discounted), Positive 1W & 1M\n")
    
    def format_and_print(df, title):
        print(f"--- {title} ---")
        if df.empty:
            print("No matches found.")
        else:
            df['gross_margin'] = (df['gross_margin'] * 100).round(2).astype(str) + '%'
            df['perf_1w'] = (df['perf_1w'] * 100).round(2).astype(str) + '%'
            df['perf_1m'] = (df['perf_1m'] * 100).round(2).astype(str) + '%'
            print(df.to_string(index=False))
        print()

    format_and_print(df_stox, "Portfolio Holdings (stox)")
    format_and_print(df_watch, "Watchlist Tickers")


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            high_margin_tech_recovery(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
