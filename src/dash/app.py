import streamlit as st
import pandas as pd
import time
import os
import sys

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.io.replay import ReplayEngine
from src.core.lob import OrderBook, Side
from src.core.order import Order
from src.strategy.imbalance import ImbalanceStrategy

def run_backtest_with_dashboard(data_file, strategy):
    """
    Runs the backtest and updates the Streamlit dashboard in real-time.
    """
    # Initialize components
    engine = ReplayEngine(data_file)
    book = OrderBook()
    
    # Dashboard containers
    st.title("LOB Simulator & Backtester")
    st.markdown("### Real-time Market Data & Strategy Performance")

    # Metrics display
    col1, col2, col3 = st.columns(3)
    best_bid_display = col1.empty()
    best_ask_display = col2.empty()
    last_trade_display = col3.empty()
    
    # PnL and Inventory display
    pnl_display = st.empty()
    inventory_display = st.empty()
    
    # Order book and trades logs
    st.markdown("#### Order Book")
    bid_chart = st.empty()
    ask_chart = st.empty()
    
    st.markdown("#### Trades & Strategy Orders")
    trades_log = st.empty()

    trades_data = []

    for index, event in engine.events.iterrows():
        event_type = event['event_type']
        
        # Update the order book with market data
        if event_type == 'ADD':
            order = Order(
                order_id=event['order_id'],
                side=Side[event['side']],
                price=event['price'],
                quantity=event['quantity'],
                timestamp=event['timestamp']
            )
            book.add_order(order)
        elif event_type == 'CANCEL':
            book.cancel_order(event['order_id'])

        # Update best bid/ask displays
        if book.bids:
            best_bid_display.metric("Best Bid", f"${book.best_bid}")
        if book.asks:
            best_ask_display.metric("Best Ask", f"${book.best_ask}")

        # Strategy logic
        strategy_order = strategy.get_order(book, event['timestamp'])
        if strategy_order:
            fills = book.add_order(strategy_order)
            for fill in fills:
                trades_data.append({
                    "Timestamp": fill.timestamp,
                    "Price": fill.price,
                    "Quantity": fill.quantity,
                    "Side": strategy_order.side.name,
                    "Type": "Strategy Fill"
                })

        # Process market order fills
        if event_type == 'TRADE':
            trades_data.append({
                "Timestamp": event['timestamp'],
                "Price": event['trade_price'],
                "Quantity": event['trade_quantity'],
                "Side": event['side'],
                "Type": "Market Trade"
            })
            
        # Update dashboard
        if trades_data:
            df_trades = pd.DataFrame(trades_data)
            trades_log.dataframe(df_trades.tail(20))

        # Update order book visualization
        bids = pd.DataFrame([{"Price": p, "Quantity": sum(o.quantity for o in v)} for p, v in book.bids.items()])
        asks = pd.DataFrame([{"Price": p, "Quantity": sum(o.quantity for o in v)} for p, v in book.asks.items()])
        
        if not bids.empty:
            bid_chart.bar_chart(bids.set_index("Price").sort_index(ascending=False))
        
        if not asks.empty:
            ask_chart.bar_chart(asks.set_index("Price"))
        
        time.sleep(0.001) # Small sleep to avoid overloading the CPU

    st.success("Backtest finished!")

if __name__ == "__main__":
    DATA_FILE = "data/sample.parquet"
    if not os.path.exists(DATA_FILE):
        st.warning(f"Data file {DATA_FILE} not found. Please run the data generator first.")
    else:
        imbalance_strategy = ImbalanceStrategy(imbalance_threshold=0.3, min_qty=5)
        run_backtest_with_dashboard(DATA_FILE, imbalance_strategy)