import yfinance as yf
import pandas as pd
import sqlite3
from datetime import datetime
import concurrent.futures
import os
import numpy as np

# --- Configuration ---
FUTURES = {
    "S&P 500 Futures": "ES=F",
    "Nasdaq 100 Futures": "NQ=F",
    "Dow Futures": "YM=F",
    "Russell 2000 Futures": "RTY=F"
}

WORLD_INDICES = {
    "Brazil (Bovespa)": "^BVSP",
    "Germany (DAX)": "^GDAXI",
    "UK (FTSE 100)": "^FTSE",
    "France (CAC 40)": "^FCHI",
    "China (SSE Composite)": "000001.SS",
    "Japan (Nikkei 225)": "^N225",
    "Taiwan (TSEC)": "^TWII",
    "South Korea (KOSPI)": "^KS11"
}

SECTORS = {
    "Technology": "XLK",
    "Financials": "XLF",
    "Health Care": "XLV",
    "Energy": "XLE",
    "Industrials": "XLI",
    "Consumer Disc": "XLY",
    "Consumer Staples": "XLP",
    "Materials": "XLB",
    "Real Estate": "XLRE",
    "Utilities": "XLU",
    "Comm Services": "XLC"
}

THEMATIC_ETFS = {
    "AI & Semiconductors": ["SOXX", "SMH", "BOTZ", "ROBO"],
    "Software & Cloud": ["IGV", "WCLD", "XSW", "CLOU", "SKYY"],
    "Quantum & Frontier": ["QTUM", "QTEC", "UFO", "ARKX"],
    "Biotech & Health": ["XBI", "IBB"],
    "Green Energy": ["ICLN", "TAN"],
    "Internet & MarTech": ["FDN", "PNQI"],
    "FinTech": ["FINX", "ARKF"],
    "Cybersecurity": ["CIBR", "HACK"],
    "Sentiment/Social": ["BUZZ", "MEME"]
}

BONDS_YIELDS = {
    "Volatility (VIX)": "^VIX",
    "10Y Treasury": "^TNX",
    "5Y Treasury": "^FVX",
    "3M Treasury Bill": "^IRX",
    "Long-Term Bonds": "TLT",
    "High Yield Corp": "HYG"
}

CRYPTO_COMMODITIES = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Crude Oil": "CL=F",
    "Copper": "HG=F"
}

class MarketSnapshotEngine:
    def __init__(self):
        self.history_data = {}
        self.news_results = []

    def fetch_bulk_data(self, ticker_list):
        """Fetches 1y history for all tickers."""
        print(f"📡 Vectorized Fetching {len(ticker_list)} symbols...")
        data = yf.download(ticker_list, period="1y", interval="1d", group_by='ticker', progress=False)
        
        for ticker in ticker_list:
            try:
                if ticker in data.columns.get_level_values(0):
                    self.history_data[ticker] = data[ticker].copy()
                else:
                    self.history_data[ticker] = yf.Ticker(ticker).history(period="1y")
            except:
                self.history_data[ticker] = pd.DataFrame()

    def fetch_news_single(self, sym):
        try:
            t = yf.Ticker(sym)
            news = t.news[:2]
            headlines = []
            for item in news:
                title = item.get('title') or item.get('content', {}).get('title', 'N/A')
                publisher = item.get('publisher') or item.get('content', {}).get('provider', {}).get('displayName', 'N/A')
                headlines.append(f"**[{sym}] {title}**  \n*{publisher}*")
            return headlines
        except:
            return []

    def prefetch_news(self, symbols=["SPY", "QQQ", "BTC-USD", "GC=F"]):
        print(f"📰 Fetching headlines for {len(symbols)} symbols...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            results = list(executor.map(self.fetch_news_single, symbols))
        self.news_results = [item for sublist in results for item in sublist]

    def get_portfolio_data(self):
        """Calculates portfolio stats and movers."""
        try:
            conn = sqlite3.connect("portfolio.db")
            # Pulse
            df_pulse = pd.read_sql_query("SELECT AVG(day_change) as avg_chg FROM stox", conn)
            portfolio_avg = df_pulse['avg_chg'].iloc[0] or 0
            
            # Movers
            df_movers = pd.read_sql_query("SELECT ticker, day_change FROM stox ORDER BY day_change DESC", conn)
            top_3 = df_movers.head(3).to_dict('records')
            bottom_3 = df_movers.tail(3).iloc[::-1].to_dict('records')
            
            conn.close()
            
            # Benchmarks
            spy = yf.Ticker("SPY").fast_info
            spy_chg = (spy['lastPrice'] / spy['previousClose'] - 1)
            
            return {
                "portfolio": portfolio_avg,
                "spy": spy_chg,
                "alpha_spy": portfolio_avg - spy_chg,
                "vix": yf.Ticker("^VIX").fast_info['lastPrice'],
                "gainers": top_3,
                "losers": bottom_3
            }
        except Exception as e:
            print(f"⚠️ Could not fetch portfolio data: {e}")
            return None

    def calculate_rsi(self, prices, periods=14):
        deltas = np.diff(prices)
        seed = deltas[:periods+1]
        up = seed[seed >= 0].sum()/periods
        down = -seed[seed < 0].sum()/periods
        rs = up/down if down != 0 else 0
        rsi = np.zeros_like(prices)
        rsi[:periods] = 100. - 100./(1. + rs)

        for i in range(periods, len(prices)):
            delta = deltas[i-1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(periods-1) + upval)/periods
            down = (down*(periods-1) + downval)/periods
            rs = up/down if down != 0 else 0
            rsi[i] = 100. - 100./(1. + rs)
        return rsi[-1]

    def format_val(self, val, is_pct=False, is_price=False, is_vol=False, is_rsi=False):
        if val is None or (isinstance(val, float) and pd.isna(val)): return "N/A"
        try:
            num = float(val)
            if is_pct: return f"{num*100:+.2f}%"
            if is_price: 
                if num > 1000: return f"{num:,.0f}"
                return f"{num:,.2f}"
            if is_rsi:
                color = "🔴" if num > 70 else "🟢" if num < 30 else ""
                return f"{color} {num:.1f}"
            return f"{num:.2f}"
        except:
            return str(val)

    def calculate_metrics(self, sym):
        hist = self.history_data.get(sym)
        if hist is None or hist.empty:
            return {"price": None, "day_chg": None, "perf_1m": None, "perf_1y": None, "vol": None, "rsi": None, "dist_200": None}
        
        try:
            closes = hist['Close'].values
            current = closes[-1]
            prev = closes[-2] if len(closes) > 1 else current
            day_chg = (current / prev - 1)
            
            # 1M Perf
            one_m_idx = -22 if len(closes) >= 22 else 0
            perf_1m = (current / closes[one_m_idx] - 1)
            
            # 1Y Perf
            perf_1y = (current / closes[0] - 1)
            
            # Volatility
            returns = hist['Close'].pct_change().iloc[-21:]
            vol = returns.std() * np.sqrt(252) if len(returns) > 5 else None
            
            # RSI
            rsi = self.calculate_rsi(closes) if len(closes) > 20 else None
            
            # Dist from 200DMA
            ma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
            dist_200 = (current / ma200 - 1) if not pd.isna(ma200) else None
            
            return {
                "price": current, "day_chg": day_chg, "perf_1m": perf_1m, "perf_1y": perf_1y,
                "vol": vol, "rsi": rsi, "dist_200": dist_200
            }
        except:
            return {"price": None, "day_chg": None, "perf_1m": None, "perf_1y": None, "vol": None, "rsi": None, "dist_200": None}

    def create_table(self, title, items, columns=["Price", "Day %", "1M %", "Vol"], is_sub=False):
        header_lvl = "###" if is_sub else "##"
        md = f"{header_lvl} {title}\n"
        headers = ["Asset"] + columns
        md += "| " + " | ".join(headers) + " |\n"
        md += "| " + " | ".join([":---"] * len(headers)) + " |\n"
        
        for name, sym in items.items():
            m = self.calculate_metrics(sym)
            row = [f"**{name}**"]
            if "Price" in columns: row.append(self.format_val(m["price"], is_price=True))
            if "Day %" in columns: 
                val = self.format_val(m["day_chg"], is_pct=True)
                if m["day_chg"] and m["day_chg"] > 0.04: val = f"🔥 {val}"
                elif m["day_chg"] and m["day_chg"] < -0.04: val = f"🧊 {val}"
                row.append(val)
            if "1M %" in columns: row.append(self.format_val(m["perf_1m"], is_pct=True))
            if "1Y %" in columns: row.append(self.format_val(m["perf_1y"], is_pct=True))
            if "Vol" in columns: row.append(self.format_val(m["vol"]))
            if "RSI" in columns: row.append(self.format_val(m["rsi"], is_rsi=True))
            if "Dist 200" in columns: row.append(self.format_val(m["dist_200"], is_pct=True))
            md += "| " + " | ".join(row) + " |\n"
        return md + "\n"

    def run(self):
        # 1. Collect all tickers
        all_tickers = list(FUTURES.values()) + list(WORLD_INDICES.values()) + list(SECTORS.values()) + \
                      list(BONDS_YIELDS.values()) + list(CRYPTO_COMMODITIES.values())
        for tks in THEMATIC_ETFS.values(): all_tickers.extend(tks)
        all_tickers = list(set(all_tickers))
        
        # 2. Bulk Fetch & News
        self.fetch_bulk_data(all_tickers)
        self.prefetch_news()

        # 3. Build Report
        data = self.get_portfolio_data()
        
        report = f"# 🌎 Market Intelligence Snapshot\n"
        report += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        
        if data:
            status = "🟢 BULLISH" if data['portfolio'] > 0 else "🔴 BEARISH"
            report += f"## 💓 Portfolio Pulse: {status}\n"
            report += f"| Metric | Portfolio | S&P 500 (SPY) | Alpha | VIX |\n"
            report += f"| :--- | :--- | :--- | :--- | :--- |\n"
            report += f"| **Daily Change** | **{self.format_val(data['portfolio'], is_pct=True)}** | {self.format_val(data['spy'], is_pct=True)} | **{self.format_val(data['alpha_spy'], is_pct=True)}** | {self.format_val(data['vix'])} |\n\n"

            report += "### 🏆 Holding Highlights\n"
            report += "| Top Gainers | Day % | | Top Losers | Day % |\n"
            report += "| :--- | :--- | :--- | :--- | :--- |\n"
            for i in range(3):
                g = data['gainers'][i] if i < len(data['gainers']) else {"ticker": "-", "day_change": 0}
                l = data['losers'][i] if i < len(data['losers']) else {"ticker": "-", "day_change": 0}
                report += f"| **{g['ticker']}** | {self.format_val(g['day_change'], is_pct=True)} | | **{l['ticker']}** | {self.format_val(l['day_change'], is_pct=True)} |\n"
            report += "\n"

        # Breadth
        sec_movers = [self.calculate_metrics(s)['day_chg'] for s in SECTORS.values()]
        green_sectors = len([s for s in sec_movers if s and s > 0])
        report += f"> **Market Breadth**: {green_sectors} of 11 S&P sectors are GREEN today.\n\n"

        # Yield Curve
        tnx = self.calculate_metrics("^TNX")['price']
        irx = self.calculate_metrics("^IRX")['price']
        if tnx and irx:
            spread = tnx - irx
            status = "⚠️ INVERTED" if spread < 0 else "✅ NORMAL"
            report += f"> **Yield Curve (10Y-3M)**: {status} at {spread/10:.2f}% spread.\n\n"

        report += self.create_table("📈 US Index Futures", FUTURES, columns=["Price", "Day %", "1M %", "RSI", "Dist 200"])
        report += self.create_table("🏗️ S&P 500 Sectors", SECTORS, columns=["Price", "Day %", "1M %", "Vol"])
        report += self.create_table("🔗 Bonds & Yields", BONDS_YIELDS, columns=["Price", "Day %", "1M %"])
        report += self.create_table("🪙 Crypto & Commodities", CRYPTO_COMMODITIES)
        
        report += "## 🚀 Thematic Tech Focus\n"
        for cat, tks in THEMATIC_ETFS.items():
            report += self.create_table(cat, {t: t for t in tks}, is_sub=True)

        report += self.create_table("🌏 Global World Indices", WORLD_INDICES, columns=["Price", "Day %", "1M %"])
        
        if self.news_results:
            report += "## 📰 Market Headlines\n"
            for news in self.news_results:
                report += f"{news}\n\n"

        os.makedirs("reports", exist_ok=True)
        with open("reports/MARKET_SNAPSHOT.md", "w") as f:
            f.write(report)
        print(f"✅ Market Snapshot V3 generated: reports/MARKET_SNAPSHOT.md")

if __name__ == "__main__":
    engine = MarketSnapshotEngine()
    engine.run()
