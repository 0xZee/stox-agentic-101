import yfinance as yf
import json

def default_converter(o):
    import datetime
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

ticker = yf.Ticker("SOFI")
exp = "2026-08-14"
chain = ticker.option_chain(exp)
calls = chain.calls
target_call = calls[calls['strike'] == 20.0]

if not target_call.empty:
    # Use to_json and then loads to avoid Timestamp issue, or use a custom converter
    print(target_call.to_json(orient='records', date_format='iso'))
else:
    nearby = calls[(calls['strike'] >= 18.0) & (calls['strike'] <= 22.0)]
    print(nearby.to_json(orient='records', date_format='iso'))
