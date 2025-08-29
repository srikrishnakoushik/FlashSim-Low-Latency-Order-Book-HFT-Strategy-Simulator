#!/bin/bash

# A simple script to run the dashboard and backtest simultaneously.

# Ensure the virtual environment is active
source .venv/bin/activate

echo "Starting Streamlit dashboard in the background..."
# Run the dashboard in the background
streamlit run src/dash/app.py &

# Wait for the dashboard to start (optional, but good practice)
sleep 5

echo "Starting backtest simulation..."
# Run the backtest in the foreground
python3 run.py --mode backtest

echo "Backtest finished. The dashboard may be manually closed."