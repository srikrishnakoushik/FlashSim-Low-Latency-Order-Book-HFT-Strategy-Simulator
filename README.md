# FlashSim: Low-Latency Limit Order Book & HFT Simulator

## Project Overview

FlashSim is a production-grade, low-latency Limit Order Book (LOB) simulator designed for developing and backtesting high-frequency trading (HFT) strategies. This project provides a complete end-to-end framework, including a high-performance matching engine, a market data I/O pipeline, a backtester with advanced analytics, and a real-time visualization dashboard.

The core of the simulator is a price-time priority matching engine built in pure Python. Its modular design allows for easy integration of new strategies and potential acceleration of critical paths using C++ in future versions.

## Key Features

- **Low-Latency Matching Engine**: A correct and deterministic order book that handles adds, cancels, and partial fills with price-time priority.
- **Dynamic Data Pipeline**: Generates and records synthetic market data with configurable volatility, allowing for robust backtesting across different market environments.
- **Microstructure Strategy**: A simple imbalance-based strategy is included to demonstrate the backtesting functionality.
- **Comprehensive Backtester**: Simulates trades and reports key metrics such as PnL, inventory, and win rate.
- **Real-time Dashboard**: A Streamlit application to visualize the order book and live trades as the simulation runs.
- **Professional CLI**: A user-friendly command-line interface for running different parts of the application.

## Repository Structure
lob-sim/
├── data/                  # Generated market data files (.parquet)
├── src/
│   ├── core/              # Core Order Book logic and data structures
│   │   ├── lob.py
│   │   └── order.py
│   ├── io/                # Market data generator and replay engine
│   │   ├── generator.py
│   │   └── replay.py
│   ├── backtest/          # Backtesting harness and analytics
│   │   └── backtester.py
│   ├── strategy/          # Trading strategies
│   │   └── imbalance.py
│   └── dash/              # Streamlit dashboard application
│       └── app.py
├── run.py                 # Main script to run simulations
├── run_all.sh             # Script to run the dashboard and backtest together
└── pyproject.toml         # Python project configuration and dependencies

## How to Run

### 1. Setup the Environment

```bash
# Create and activate a virtual environment
python3.9 -m venv .venv
source .venv/bin/activate

# Install dependencies from pyproject.toml
pip install pytest black ruff pyarrow numpy pandas streamlit

# Run a low volatility backtest
python3 run.py --events 5000 --volatility 0.002

# Run a high volatility backtest
python3 run.py --events 5000 --volatility 0.05

#run the dashboard
python3 run.py --mode dashboard

#. Sample Backtest Results
Here is a sample output demonstrating how the strategy performs in a high volatility environment.

--- Backtest Results ---
Total Fills: 119
Final PnL: -556.0
Final Inventory: 465.0
Win Rate: 0.61
