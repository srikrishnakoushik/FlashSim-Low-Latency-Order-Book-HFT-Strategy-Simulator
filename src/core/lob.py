from collections import deque, defaultdict
from dataclasses import dataclass
from typing import Optional
from src.core.order import Order, Side, Trade

@dataclass()
class PriceLevel:
    """Represents a single price level in the order book."""
    price: int
    orders: deque[Order] = deque()
    size: int = 0
    num_orders: int = 0

class OrderBook:
    """
    A low-latency, price-time priority Limit Order Book.
    """
    def __init__(self):
        self.bids = defaultdict(lambda: deque())
        self.asks = defaultdict(lambda: deque())
        self.orders = {}
        self.trade_id_counter = 0

    def __repr__(self):
        return f"OrderBook(bids={len(self.bids)} levels, asks={len(self.asks)} levels)"

    @property
    def best_bid(self) -> Optional[int]:
        """Returns the best bid price or None if bids are empty."""
        if not self.bids:
            return None
        return max(self.bids.keys())

    @property
    def best_ask(self) -> Optional[int]:
        """Returns the best ask price or None if asks are empty."""
        if not self.asks:
            return None
        return min(self.asks.keys())

    def add_order(self, order: Order) -> list[Trade]:
        """
        Adds a new limit order to the book, with matching.
        Complexity: O(N) in worst case (N fills) but typically O(1).
        """
        if order.order_id in self.orders:
            raise ValueError(f"Order ID {order.order_id} already exists.")

        trades = []
        
        is_crossing = (order.side == Side.BUY and self.best_ask is not None and order.price >= self.best_ask) or \
                      (order.side == Side.SELL and self.best_bid is not None and order.price <= self.best_bid)

        if is_crossing:
            resting_book = self.asks if order.side == Side.BUY else self.bids
            resting_prices = sorted(resting_book.keys())
            if order.side == Side.BUY:
                resting_prices.reverse()
            
            new_order_remaining_qty = order.quantity
            
            for resting_price in resting_prices:
                if order.side == Side.BUY and resting_price > order.price:
                    break
                if order.side == Side.SELL and resting_price < order.price:
                    break
                
                resting_level = resting_book[resting_price]
                
                while new_order_remaining_qty > 0 and resting_level:
                    resting_order = resting_level[0]
                    fill_qty = min(new_order_remaining_qty, resting_order.quantity)
                    
                    self.trade_id_counter += 1
                    trade = Trade(
                        trade_id=self.trade_id_counter,
                        aggressing_order_id=order.order_id,
                        resting_order_id=resting_order.order_id,
                        price=resting_price,
                        quantity=fill_qty,
                        timestamp=order.timestamp
                    )
                    trades.append(trade)

                    new_order_remaining_qty -= fill_qty
                    resting_order.quantity -= fill_qty
                    
                    if resting_order.quantity == 0:
                        resting_level.popleft()
                        del self.orders[resting_order.order_id]
                
                if not resting_level:
                    del resting_book[resting_price]

                if new_order_remaining_qty == 0:
                    break
            
            if new_order_remaining_qty > 0:
                order.quantity = new_order_remaining_qty
                if order.side == Side.BUY:
                    self.bids[order.price].append(order)
                else:
                    self.asks[order.price].append(order)
                self.orders[order.order_id] = order
            else:
                if order.order_id in self.orders:
                    del self.orders[order.order_id]
        else:
            if order.side == Side.BUY:
                self.bids[order.price].append(order)
            else:
                self.asks[order.price].append(order)
            self.orders[order.order_id] = order
            
        return trades

    def cancel_order(self, order_id: int):
        order = self.orders.pop(order_id, None)
        if not order:
            return

        price_levels = self.bids if order.side == Side.BUY else self.asks
        if order.price in price_levels:
            level_orders = price_levels[order.price]
            try:
                level_orders.remove(order)
                if not level_orders:
                    del price_levels[order.price]
            except ValueError:
                pass

    def modify_order(self, order_id: int, new_quantity: int, new_price: int = None):
        order = self.orders.get(order_id)
        if order:
            self.cancel_order(order_id)
            if new_quantity > 0:
                new_order = Order(
                    order_id=order.order_id,
                    side=order.side,
                    price=new_price if new_price is not None else order.price,
                    quantity=new_quantity,
                    timestamp=order.timestamp
                )
                self.add_order(new_order)