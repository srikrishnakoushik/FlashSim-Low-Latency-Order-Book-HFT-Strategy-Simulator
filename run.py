import os
import sys
import argparse 

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.io.generator import MarketDataGenerator
from src.strategy.imbalance import ImbalanceStrategy
from src.backtest.backtester import Backtester

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LOB simulator components.")
    parser.add_argument("--mode", type=str, choices=["backtest", "dashboard"], default="backtest", help="Choose run mode: 'backtest' or 'dashboard'.")
    parser.add_argument("--events", type=int, default=1000, help="Number of events to generate/replay.")
    parser.add_argument("--imbalance-threshold", type=float, default=0.3, help="Imbalance threshold for the strategy.")
    parser.add_argument("--min-qty", type=int, default=5, help="Minimum quantity for strategy orders.")
    parser.add_argument("--volatility", type=float, default=0.01, help="Volatility factor for data generation.")
    args = parser.parse_args()

    DATA_FILE = f"data/sample_vol_{args.volatility}.parquet"
    EVENT_COUNT = args.events

    # Step 1: Generate market data if it doesn't exist
    if not os.path.exists(DATA_FILE):
        print(f"Generating synthetic market data with {EVENT_COUNT} events and volatility {args.volatility}...")
        generator = MarketDataGenerator(start_time=1, event_count=EVENT_COUNT, file_path=DATA_FILE, volatility=args.volatility)
        generator.generate_and_record()
    
    if args.mode == "backtest":
        # Step 2: Initialize strategy and backtester
        print("\nStarting backtest...")
        imbalance_strategy = ImbalanceStrategy(
            imbalance_threshold=args.imbalance_threshold,
            min_qty=args.min_qty
        )
        backtester = Backtester(data_file=DATA_FILE, strategy=imbalance_strategy)

        # Step 3: Run the backtest
        backtester.run()

        # Step 4: Report results
        metrics = backtester.get_metrics()
        print("\n--- Backtest Results ---")
        print(f"Total Fills: {metrics['total_fills']}")
        print(f"Final PnL: {metrics['net_pnl']}")
        print(f"Final Inventory: {metrics['final_inventory']}")
        print(f"Win Rate: {metrics['win_rate']}")

    elif args.mode == "dashboard":
        # The run_all.sh script will handle this.
        print("\nStarting Streamlit dashboard...")
        os.system(f"streamlit run src/dash/app.py")