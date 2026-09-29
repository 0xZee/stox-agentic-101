import subprocess
import os

def run_strategy(script_path):
    print(f"\n{'#'*60}")
    print(f"🚀 RUNNING: {os.path.basename(script_path)}")
    print(f"{'#'*60}")
    try:
        result = subprocess.run(["python3", script_path], capture_output=False, text=True)
    except Exception as e:
        print(f"❌ Failed to run {script_path}: {e}")

if __name__ == "__main__":
    strategy_dir = "strategies"
    scripts = [
        "value_screeners.py",
        "quant_risk_strategies.py",
        "tech_momentum_strategies.py",
        "sentiment_analyst_edge.py",
        "dividend_strategies.py"
    ]
    
    print("📈 STARTING GLOBAL PORTFOLIO STRATEGY ANALYSIS...")
    
    for script in scripts:
        path = os.path.join(strategy_dir, script)
        if os.path.exists(path):
            run_strategy(path)
        else:
            print(f"⚠️ Script not found: {path}")

    print("\n✅ All strategies processed.")
