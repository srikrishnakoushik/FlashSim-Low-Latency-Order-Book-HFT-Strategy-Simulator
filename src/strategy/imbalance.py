from src.core.lob import OrderBook, Side
from src.core.order import Order
from typing import Optional
import numpy as np

class ImbalanceStrategy:
    """
    A simple market microstructure strategy based on order book imbalance.
    """
    def __init__(self, imbalance_threshold: float, min_qty: int):
        self.imbalance_threshold = imbalance_threshold
        self.min_qty = min_qty
        self.order_id_counter = 1000  # Start with a high ID to avoid conflicts
        self.active_orders = {}  # Track our own active orders

    def get_order(self, book: OrderBook, timestamp: int) -> Optional[Order]:
        """
        Calculates imbalance and returns a new order if a signal is found.
        Returns a new order or None if no signal is found.
        """
        if len(book.bids) < 1 or len(book.asks) < 1:
            return None

        best_bid_price = book.best_bid
        best_ask_price = book.best_ask
        
        # Check if best prices exist before proceeding
        if best_bid_price is None or best_ask_price is None:
            return None
        
        bid_size = sum(o.quantity for o in book.bids[best_bid_price])
        ask_size = sum(o.quantity for o in book.asks[best_ask_price])
        
        if (bid_size + ask_size) == 0:
            return None
        
        imbalance = (bid_size - ask_size) / (bid_size + ask_size)
        
        self.order_id_counter += 1
        
        if imbalance > self.imbalance_threshold:
            # High buy pressure, send a passive sell order
            return Order(
                order_id=self.order_id_counter,
                side=Side.SELL,
                price=best_ask_price + 1,
                quantity=self.min_qty,
                timestamp=timestamp
            )
        elif imbalance < -self.imbalance_threshold:
            # High sell pressure, send a passive buy order
            return Order(
                order_id=self.order_id_counter,
                side=Side.BUY,
                price=best_bid_price - 1,
                quantity=self.min_qty,
                timestamp=timestamp
            )
        
        return None