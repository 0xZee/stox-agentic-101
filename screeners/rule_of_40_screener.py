import sqlite3
import pandas as pd
import sys


def rule_of_40_screener(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Fetch growth and margin
    df = pd.read_sql_query(f"SELECT ticker, name, sector, rev_growth, profit_margin FROM {table_name}", conn)
    conn.close()
    
    if df.empty:
        print("Database is empty.")
        return

    # Filter out companies with N/A data
    df = df.dropna(subset=['rev_growth', 'profit_margin'])

    # Calculate Rule of 40 Score
    df['rule_of_40_score'] = (df['rev_growth'] + df['profit_margin']) * 100
    
    # Filter for score >= 40
    r40_df = df[df['rule_of_40_score'] >= 40].copy().sort_values('rule_of_40_score', ascending=False)

    print("🚀 The Rule of 40 Screener")
    print("Criteria: Revenue Growth + Profit Margin >= 40%\n")
    
    if r40_df.empty:
        print("No companies currently meeting the Rule of 40.")
    else:
        # Format for display
        r40_df['rev_growth'] = (r40_df['rev_growth'] * 100).round(2).astype(str) + '%'
        r40_df['profit_margin'] = (r40_df['profit_margin'] * 100).round(2).astype(str) + '%'
        r40_df['rule_of_40_score'] = r40_df['rule_of_40_score'].round(2)
        
        print(r40_df[['ticker', 'name', 'rule_of_40_score', 'rev_growth', 'profit_margin', 'sector']].to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            rule_of_40_screener(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
