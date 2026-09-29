import sqlite3
import pandas as pd
import sys

def gems_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    query = f"SELECT ticker, name, sector, industry, price, market_cap, rev_growth, gross_margin, debt_equity, f_score, ev_rev FROM {table_name}"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print(f"Table {table_name} is empty.")
        return

    # 1. Mandatory Filter: Size ($300M - $2B)
    # Note: We allow slightly more range to capture near-misses
    df = df[(df['market_cap'] >= 100_000_000) & (df['market_cap'] <= 3_000_000_000)]
    
    if df.empty:
        print(f"No stocks in {table_name} within the $100M - $3B range.")
        return

    # 2. Scoring Mechanism (Handling NAs by giving 0 points)
    df['points'] = 0
    df.loc[df['rev_growth'] > 0.15, 'points'] += 2
    df.loc[df['gross_margin'] > 0.40, 'points'] += 2
    df.loc[df['f_score'] >= 5, 'points'] += 3
    df.loc[df['debt_equity'] < 0.5, 'points'] += 1
    df.loc[df['ev_rev'] < 6, 'points'] += 2
    
    # Ranking Potential Gems
    gems = df.sort_values('points', ascending=False).head(15)

    print(f"💎 The 'Gems' Screener: {table_name}")
    print("Ranking stocks by Growth, Quality, and Valuation signals ($100M-$3B range)\n")
    
    # Formatting for display
    gems['Market Cap'] = (gems['market_cap'] / 1_000_000).round(1).astype(str) + 'M'
    gems['Rev Growth'] = (gems['rev_growth'] * 100).fillna(0).round(1).astype(str) + '%'
    gems['Gross Margin'] = (gems['gross_margin'] * 100).fillna(0).round(1).astype(str) + '%'
    gems['Score'] = gems['points']
    
    display_cols = ['ticker', 'name', 'Market Cap', 'Rev Growth', 'Gross Margin', 'Score']
    print(gems[display_cols].to_string(index=False))

if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n" + "="*50)
        try:
            gems_screener(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
