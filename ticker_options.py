import yfinance as yf
import sys
import pandas as pd
from datetime import datetime, timedelta

def get_option_chain(ticker_symbol):
    try:
        ticker = yf.Ticker(ticker_symbol)
        expirations = ticker.options
        
        if not expirations:
            return {"error": f"No options available for {ticker_symbol}"}
        
        # Filter expirations within 2W to 3M
        now = datetime.now()
        min_date = now + timedelta(weeks=2)
        max_date = now + timedelta(weeks=12)
        
        valid_exps = []
        for exp in expirations:
            exp_date = datetime.strptime(exp, "%Y-%m-%d")
            if min_date <= exp_date <= max_date:
                valid_exps.append(exp)
        
        if not valid_exps:
            # Fallback to nearest if none in range
            valid_exps = expirations[:3]

        results = {}
        for exp in valid_exps[:3]: # Limit to first 3 valid exp dates for brevity
            chain = ticker.option_chain(exp)
            results[exp] = {
                "calls": chain.calls[['strike', 'lastPrice', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']].head(10).to_dict(orient='records'),
                "puts": chain.puts[['strike', 'lastPrice', 'change', 'percentChange', 'volume', 'openInterest', 'impliedVolatility']].head(10).to_dict(orient='records')
            }
            
        return {"ticker": ticker_symbol, "expirations": valid_exps, "chains": results}
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ticker_options.py <TICKER>")
        sys.exit(1)
    
    ticker = sys.argv[1].upper()
    data = get_option_chain(ticker)
    import json
    print(json.dumps(data, indent=2))
