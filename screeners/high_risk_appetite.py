import sqlite3
import pandas as pd
import sys


def high_risk_appetite(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Focus on high beta, high volatility, high growth, and market cap < 5B
    query = f"""
    SELECT 
        ticker, 
        name, 
        beta, 
        volatility, 
        rev_growth, 
        market_cap
    FROM {table_name} 
    WHERE beta > 1.5 
      AND volatility > 0.40
      AND rev_growth > 0.30
    ORDER BY beta DESC, rev_growth DESC
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    print("🧨 High-Risk Appetite Screener")
    print("Criteria: Beta > 1.5, Volatility > 40%, Revenue Growth > 30%\n")
    
    if df.empty:
        print("No high-risk/high-reward candidates identified.")
    else:
        # Format for display
        df['volatility'] = (df['volatility'] * 100).round(2).astype(str) + '%'
        df['rev_growth'] = (df['rev_growth'] * 100).round(2).astype(str) + '%'
        # Convert market cap to Billions
        df['market_cap'] = df['market_cap'].apply(lambda x: f"${x/1e9:.2f}B" if x else "N/A")
        
        print(df.to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            high_risk_appetite(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
