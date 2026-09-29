import sqlite3
import pandas as pd
import sys


def moat_quality_score(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Fetch quality metrics
    df = pd.read_sql_query(f"SELECT ticker, name, gross_margin, roe, f_score FROM {table_name}", conn)
    conn.close()
    
    if df.empty:
        print("Database is empty.")
        return

    # Normalize metrics 0-1 (simple min-max or ranking)
    # Using ranking for more robust relative scoring
    df['gm_rank'] = df['gross_margin'].rank(pct=True)
    df['roe_rank'] = df['roe'].rank(pct=True)
    df['f_rank'] = df['f_score'].rank(pct=True)

    # Composite Score: 40% Margin, 30% ROE, 30% F-Score
    df['quality_score'] = (df['gm_rank'] * 0.4 + df['roe_rank'] * 0.3 + df['f_rank'] * 0.3) * 100
    df['quality_score'] = df['quality_score'].round(2)

    top_quality = df.sort_values('quality_score', ascending=False).head(20)

    print("🏰 Moat Quality Score (Top 20)")
    print("Composite ranking based on Gross Margins, ROE, and Financial Strength (F-Score)\n")
    
    # Format for display
    top_quality['gross_margin'] = (top_quality['gross_margin'] * 100).round(2).astype(str) + '%'
    top_quality['roe'] = (top_quality['roe'] * 100).round(2).astype(str) + '%'
    
    print(top_quality[['ticker', 'name', 'quality_score', 'gross_margin', 'roe', 'f_score']].to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            moat_quality_score(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
