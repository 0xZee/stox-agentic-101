import yfinance as yf
import sqlite3
import pandas as pd
from datetime import datetime, timedelta

def get_3m_perf():
    conn = sqlite3.connect('portfolio.db')
    tickers = pd.read_sql_query("SELECT ticker FROM stox", conn)['ticker'].tolist()
    conn.close()

    results = []
    end_date = datetime.now()
    start_date = end_date - timedelta(days=90)
    
    print(f"Fetching 3-month data for {len(tickers)} tickers...")
    
    # Fetch in batches to be efficient
    data = yf.download(tickers, start=start_date, end=end_date, interval='1d', group_by='ticker', threads=True, progress=False)
    
    for ticker in tickers:
        try:
            if ticker in data.columns.levels[0]:
                ticker_data = data[ticker]['Close'].dropna()
                if len(ticker_data) > 2:
                    start_price = ticker_data.iloc[0]
                    end_price = ticker_data.iloc[-1]
                    perf_3m = (end_price / start_price) - 1
                    results.append({'ticker': ticker, 'perf_3m': perf_3m})
        except Exception:
            continue
            
    df = pd.DataFrame(results).sort_values(by='perf_3m', ascending=False)
    return df.head(20)

if __name__ == "__main__":
    top_20 = get_3m_perf()
    print(top_20.to_string(index=False))
