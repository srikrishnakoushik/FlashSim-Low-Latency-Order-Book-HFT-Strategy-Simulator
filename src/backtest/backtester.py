import pandas as pd
from src.io.replay import ReplayEngine
from src.core.lob import OrderBook
from src.core.order import Order, Side, Trade 
from src.strategy.imbalance import ImbalanceStrategy

class Backtester:
    """
    Simulates trading a strategy against historical market data.
    """
    def __init__(self, data_file: str, strategy: ImbalanceStrategy):
        self.engine = ReplayEngine(data_file)
        self.strategy = strategy
        self.book = OrderBook()
        self.fills = []
        self.pnl = 0.0
        self.inventory = 0
        self.last_trade_price = None
        self.strategy_orders = {} # NEW: A dict to track our placed orders

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
                # A TRADE event represents a fill. We just log it for our records.
                pass 
            elif event_type == 'MARKET_NO_TRADE':
                 pass
            
            # Check strategy for a new order to place on the book
            strategy_order = self.strategy.get_order(self.book, timestamp)
            if strategy_order:
                print(f"[{timestamp}] STRATEGY: Placing {strategy_order.side.name} order for {strategy_order.quantity} at {strategy_order.price}")
                self.strategy_orders[strategy_order.order_id] = strategy_order.side # NEW: Record our placed order
                trades = self.book.add_order(strategy_order)
                self.fills.extend(trades)

                # Update PnL and inventory based on fills from our strategy
                for fill in trades:
                    fill_price = fill.price
                    fill_qty = fill.quantity
                    if strategy_order.side == Side.BUY:
                        self.inventory += fill_qty
                        self.pnl -= fill_price * fill_qty
                    else:
                        self.inventory -= fill_qty
                        self.pnl += fill_price * fill_qty
                    self.last_trade_price = fill_price

    def get_metrics(self):
        """
        Calculates and returns key backtesting metrics.
        """
        total_pnl = self.pnl
        
        # Mark to last price PnL
        if self.last_trade_price is not None:
            total_pnl += self.inventory * self.last_trade_price
        
        # Calculate win rate and total trades
        win_trades = 0
        fill_count = len(self.fills)
        if fill_count > 0:
            for i in range(fill_count):
                current_fill = self.fills[i]
                
                # Get the side of the aggressing order
                aggressing_side = self.strategy_orders.get(current_fill.aggressing_order_id)
                if aggressing_side is None:
                    continue # Not our order, or a resting fill we don't care about here

                # Simple win/loss check
                if aggressing_side == Side.BUY:
                    # Our buy order filled. Check if the price is good.
                    # This is a very rough check for now.
                    if current_fill.price <= self.last_trade_price:
                        win_trades += 1
                elif aggressing_side == Side.SELL:
                    # Our sell order filled. Check if the price is good.
                    if current_fill.price >= self.last_trade_price:
                        win_trades += 1

        win_rate = win_trades / fill_count if fill_count > 0 else 0

        return {
            'total_fills': fill_count,
            'net_pnl': round(total_pnl, 2),
            'final_inventory': self.inventory,
            'win_rate': round(win_rate, 2),
        }