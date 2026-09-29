import sqlite3
import os
import sys
from datetime import datetime

def get_db_data(ticker):
    conn = sqlite3.connect("portfolio.db")
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    row = cursor.execute("SELECT * FROM stox WHERE ticker=?", (ticker.upper(),)).fetchone()
    conn.close()
    return row

def create_progress_bar(val, min_val, max_val, length=20):
    if None in [val, min_val, max_val] or max_val == min_val:
        return "[Data Unavailable]"
    percent = (val - min_val) / (max_val - min_val)
    pos = int(percent * length)
    pos = max(0, min(pos, length - 1))
    bar = ["-"] * length
    bar[pos] = "O"
    return f"[{''.join(bar)}] ({percent*100:.1f}%)"

def format_pct(val):
    if val is None: return "N/A"
    return f"{val*100:.2f}%"

def format_num(val, suffix=""):
    if val is None: return "N/A"
    if abs(val) >= 1e12: return f"{val/1e12:.2f}T{suffix}"
    if abs(val) >= 1e9: return f"{val/1e9:.2f}B{suffix}"
    if abs(val) >= 1e6: return f"{val/1e6:.2f}M{suffix}"
    return f"{val:,.2f}{suffix}"

def get_rating_stars(score):
    if score is None: return "N/A"
    stars = int(round(score / 2))
    return "⭐" * stars + "☆" * (5 - stars)

def generate_report(ticker):
    row = get_db_data(ticker)
    if not row:
        print(f"❌ Ticker {ticker} not found in database.")
        return

    # Weighted Scoring
    val_score = 0
    if row['pe_forward'] and row['pe_forward'] < 20: val_score += 4
    if row['peg'] and row['peg'] < 1.0: val_score += 4
    if row['p_sales'] and row['p_sales'] < 3: val_score += 2
    
    grow_score = 0
    if row['rev_growth'] and row['rev_growth'] > 0.15: grow_score += 5
    if row['earn_growth'] and row['earn_growth'] > 0.15: grow_score += 5
    
    safe_score = 0
    if row['altman_status'] == "Safe": safe_score += 4
    if row['debt_equity'] and row['debt_equity'] < 50: safe_score += 3
    if row['current_ratio'] and row['current_ratio'] > 1.5: safe_score += 3

    # Short Squeeze Logic
    is_squeeze_candidate = False
    if row['short_pct_float'] and row['short_pct_float'] > 0.15 and row['short_ratio'] and row['short_ratio'] > 5:
        is_squeeze_candidate = True

    report = f"""# 📑 Comprehensive Intelligence Dossier: {row['name']} ({row['ticker']})
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M")}

---

## 🏗️ Executive Dashboard
| Pillar | Rating | Score | Status |
| :--- | :--- | :--- | :--- |
| **Value** | {get_rating_stars(val_score)} | {val_score}/10 | {"🟢 Undervalued" if val_score > 7 else "🟡 Fair" if val_score > 4 else "🔴 Premium"} |
| **Growth** | {get_rating_stars(grow_score)} | {grow_score}/10 | {"🟢 Aggressive" if grow_score > 7 else "🟡 Moderate" if grow_score > 3 else "🔴 Stagnant"} |
| **Safety** | {get_rating_stars(safe_score)} | {safe_score}/10 | {"🟢 Fortress" if safe_score > 7 else "🟡 Robust" if safe_score > 4 else "🔴 Risk Alert"} |

### 🎯 Price & Analyst Targeting
**Current Price**: ${row['price']} | **Prev Close**: ${row['prev_close']}
**52W Range**: ${row['fifty_two_w_low']} — ${row['fifty_two_w_high']}
**Position**: {create_progress_bar(row['price'], row['fifty_two_w_low'], row['fifty_two_w_high'])}
**Analyst Target**: ${row['target_mean']} ({format_pct(row['upside'])} Upside)

---

## 💹 Valuation Waterfall
| Metric | Value | Breakdown |
| :--- | :--- | :--- |
| **P/E (Trailing)** | {row['pe_trailing']} | Current Earnings Yield |
| **P/E (Forward)** | {row['pe_forward']} | Growth Adjusted Expectations |
| **PEG Ratio** | {row['peg']} | Efficiency of Growth (< 1.0 is Ideal) |
| **Price / Sales** | {row['p_sales']} | Revenue Multiple |
| **Price / Book** | {row['p_book']} | Net Asset Valuation |
| **EV / Revenue** | {row['ev_rev']} | Total Enterprise Scale |
| **EV / EBITDA** | {row['ev_ebitda']} | Operational Cash Multiple |

---

## 🔊 Volume & Liquidity
| Metric | Current | Benchmark |
| :--- | :--- | :--- |
| **Volume** | {format_num(row['volume'])} | Today's Activity |
| **Avg Vol (10d)** | {format_num(row['avg_vol_10d'])} | Short-term Liquidity |
| **Avg Vol (3m)** | {format_num(row['avg_vol_3m'])} | Institutional Baseline |
| **Avg Daily Vol (10d)** | {format_num(row['avg_daily_vol_10d'])} | Daily Turnover |
| **Bid/Ask Spread** | ${row['bid']} / ${row['ask']} | Trade Friction |

---

## 🩳 Short Squeeze Risk Analysis
**Squeeze Status**: {"🔥 HIGH ALERT" if is_squeeze_candidate else "✅ Low Risk"}

- **Short % of Float**: {format_pct(row['short_pct_float'])}
- **Short Ratio (Days to Cover)**: {row['short_ratio']}
- **Shares Short**: {format_num(row['shares_short'])}
- **Short % Change**: {format_pct(row['short_pct_chg'])}
- **Prior Month Short**: {format_num(row['short_prior'])}

---

## 📈 Profitability Heatmap
| Metric | Value | Industry Performance |
| :--- | :--- | :--- |
| **Gross Margin** | {format_pct(row['gross_margin'])} | Core Product Profitability |
| **Operating Margin** | {format_pct(row['oper_margin'])} | Overhead Efficiency |
| **Profit Margin** | {format_pct(row['profit_margin'])} | Net Bottom Line |
| **ROE** | {format_pct(row['roe'])} | Return on Equity |
| **ROA** | {format_pct(row['roa'])} | Asset Efficiency |

---

## 🛡️ Financial Fortitude (Safety)
**Altman Z-Score**: {row['z_score']} ({row['altman_status']})

- **Liquidity**: Current Ratio: {row['current_ratio']} | Quick Ratio: {row['quick_ratio']}
- **Solvency**: Debt to Equity: {row['debt_equity']}
- **War Chest**: Total Cash: ${format_num(row['total_cash'])} | FCF: ${format_num(row['fcf'])}

---

## 🧭 Technical & Sentiment
- **Momentum (RSI 14d)**: {row['rsi']} ({"Overbought" if row['rsi'] and row['rsi'] > 70 else "Oversold" if row['rsi'] and row['rsi'] < 30 else "Neutral"})
- **Beta (5Y)**: {row['beta']} ({"Aggressive" if row['beta'] and row['beta'] > 1.2 else "Stable" if row['beta'] and row['beta'] < 1.0 else "Market Match"})
- **Analyst Consensus**: {row['consensus']} ({int(row['opinions'] or 0)} opinions)

---

## 🏢 Profile
- **Sector**: {row['sector']}
- **Industry**: {row['industry']}
- **Location**: {row['city']}, {row['state']}, {row['country']}
- **Employees**: {format_num(row['employees'])}
- **Website**: [{row['website']}]({row['website']})
"""

    report_path = f"reports/{ticker.upper()}_REPORT.md"
    with open(report_path, "w") as f:
        report_content = report.strip()
        f.write(report_content)
    
    print(f"✅ Comprehensive Dossier generated: {report_path}")
    return report_content

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_ticker.py <TICKER>")
    else:
        generate_report(sys.argv[1])
