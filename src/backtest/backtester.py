import pandas as pd
from src.io.replay import ReplayEngine
from src.core.lob import OrderBook
from src.core.order import Order, Side, Trade # <-- ADDED THIS IMPORT
from src.strategy.imbalance import ImbalanceStrategy

class Backtester:
    """
    Simulates trading a strategy against historical market data.
    """
    def __init__(self, data_file: str, strategy: ImbalanceStrategy):
        self.engine = ReplayEngine(data_file)
        self.strategy = strategy
        self.book = OrderBook()
        self.trades = []
        self.pnl = 0.0
        self.inventory = 0
        self.last_trade_price = None

    def run(self):
        """
        Runs the backtest simulation.
        """
        for _, event in self.engine.events.iterrows():
            timestamp = event['timestamp']
            event_type = event['event_type']
            
            # Update the order book with the latest market data
            if event_type == 'ADD':
                order = Order(
                    order_id=event['order_id'],
                    side=Side[event['side']],
                    price=event['price'],
                    quantity=event['quantity'],
                    timestamp=timestamp
                )
                self.book.add_order(order)
            elif event_type == 'CANCEL':
                self.book.cancel_order(event['order_id'])
            elif event_type == 'TRADE':
                # A TRADE event represents a fill, so we don't add a new order to the book.
                # The LOB's state should have been updated by the aggressing order.
                # We just need to capture this fill to update our strategy's state.
                pass # We'll handle our strategy's trades below.
            elif event_type == 'MARKET_NO_TRADE':
                 pass
            
            # Check strategy for a new order to place on the book
            strategy_order = self.strategy.get_order(self.book, timestamp)
            if strategy_order:
                print(f"[{timestamp}] STRATEGY: Placing {strategy_order.side.name} order for {strategy_order.quantity} at {strategy_order.price}")
                trades = self.book.add_order(strategy_order)
                self.trades.extend(trades)

                # Update PnL and inventory based on fills from our strategy
                for trade in trades:
                    fill_price = trade.price
                    fill_qty = trade.quantity
                    if strategy_order.side == Side.BUY:
                        self.inventory += fill_qty
                        self.pnl -= fill_price * fill_qty
                    else: # A sell order
                        self.inventory -= fill_qty
                        self.pnl += fill_price * fill_qty
                    self.last_trade_price = fill_price

    def get_metrics(self):
        """
        Calculates and returns key backtesting metrics.
        """
        total_trades = len(self.trades)
        total_pnl = self.pnl
        
        # Mark to last price PnL
        if self.last_trade_price is not None:
            total_pnl += self.inventory * self.last_trade_price
        
        return {
            'total_trades': total_trades,
            'net_pnl': round(total_pnl, 2),
            'final_inventory': self.inventory
        }