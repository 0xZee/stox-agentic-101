import sqlite3
import pandas as pd
import sys


def sector_relative_value(table_name):
    conn = sqlite3.connect('portfolio.db')
    # Fetch data to calculate sector averages
    df = pd.read_sql_query(f"SELECT ticker, name, sector, pe_forward, p_sales, profit_margin FROM {table_name}", conn)
    conn.close()
    
    if df.empty:
        print("Database is empty.")
        return

    # Calculate sector medians
    sector_stats = df.groupby('sector').agg({
        'pe_forward': 'median',
        'p_sales': 'median',
        'profit_margin': 'median'
    }).rename(columns={
        'pe_forward': 'sector_pe_med',
        'p_sales': 'sector_ps_med',
        'profit_margin': 'sector_margin_med'
    })

    # Join back to original data
    df = df.join(sector_stats, on='sector')

    # Find stocks trading at a discount to sector P/E median while having better margins
    discounts = df[
        (df['pe_forward'] < df['sector_pe_med'] * 0.8) & 
        (df['profit_margin'] > df['sector_margin_med'])
    ].copy()

    print("📊 Sector Relative Value Analysis")
    print("Finding stocks at >20% discount to Sector P/E median with superior Profit Margins\n")
    
    if discounts.empty:
        print("No relative value gems identified.")
    else:
        # Clean up for display
        display_cols = ['ticker', 'name', 'sector', 'pe_forward', 'sector_pe_med', 'profit_margin', 'sector_margin_med']
        discounts['profit_margin'] = (discounts['profit_margin'] * 100).round(2).astype(str) + '%'
        discounts['sector_margin_med'] = (discounts['sector_margin_med'] * 100).round(2).astype(str) + '%'
        print(discounts[display_cols].to_string(index=False))


if __name__ == "__main__":
    tables = sys.argv[1:] if len(sys.argv) > 1 else ['stox', 'watchlist']
    for t in tables:
        print(f"\n==================== TABLE: {t} ====================")
        try:
            sector_relative_value(t)
        except Exception as e:
            print(f"Error running screener on {t}: {e}")
