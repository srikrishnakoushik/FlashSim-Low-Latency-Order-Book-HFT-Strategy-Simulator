import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))

from src.io.generator import MarketDataGenerator
from src.strategy.imbalance import ImbalanceStrategy
from src.backtest.backtester import Backtester

if __name__ == "__main__":
    DATA_FILE = "data/sample.parquet"
    EVENT_COUNT = 1000

    # Step 1: Generate market data if it doesn't exist
    if not os.path.exists(DATA_FILE):
        print(f"Generating synthetic market data with {EVENT_COUNT} events...")
        generator = MarketDataGenerator(start_time=1, event_count=EVENT_COUNT, file_path=DATA_FILE)
        generator.generate_and_record()

    # Step 2: Initialize strategy and backtester
    print("\nStarting backtest...")
    imbalance_strategy = ImbalanceStrategy(imbalance_threshold=0.3, min_qty=5)
    backtester = Backtester(data_file=DATA_FILE, strategy=imbalance_strategy)

    # Step 3: Run the backtest
    backtester.run()

    # Step 4: Report results
    metrics = backtester.get_metrics()
    print("\n--- Backtest Results ---")
    print(f"Total Trades: {metrics['total_trades']}")
    print(f"Final PnL: {metrics['net_pnl']}")
    print(f"Final Inventory: {metrics['final_inventory']}")