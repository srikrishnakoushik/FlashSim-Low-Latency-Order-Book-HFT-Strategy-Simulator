import sys
import os

from collections import deque
# Explicitly add the project root to the Python path
# so that we can import modules from the `src/` directory.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.order import Order, Side, Trade
from src.core.lob import OrderBook, PriceLevel

def test_environment_setup():
    """
    Sanity check to ensure pytest is working.
    """
    assert True

def test_order_creation():
    """
    Test that an Order object can be created correctly.
    """
    order = Order(order_id=1, side=Side.BUY, price=100, quantity=10, timestamp=1678886400000000)
    assert order.order_id == 1
    assert order.side == Side.BUY
    assert order.price == 100
    assert order.quantity == 10
    assert isinstance(order.timestamp, int)

def test_trade_creation():
    """
    Test that a Trade object can be created correctly.
    """
    trade = Trade(trade_id=1, aggressing_order_id=1, resting_order_id=2, price=100, quantity=5, timestamp=1678886400000000)
    assert trade.trade_id == 1
    assert trade.price == 100
    assert trade.quantity == 5
    assert isinstance(trade.timestamp, int)

def test_price_level_creation():
    """Test that a PriceLevel object can be created."""
    level = PriceLevel(price=100)
    assert level.price == 100
    assert isinstance(level.orders, deque)

def test_add_order():
    """Test that a single order can be added to the book."""
    book = OrderBook()
    order = Order(order_id=1, side=Side.BUY, price=100, quantity=10, timestamp=1678886400000000)
    book.add_order(order)

    assert len(book.orders) == 1
    assert book.orders[1].quantity == 10 # Check quantity after add
    assert book.bids[100][0] == order
    assert len(book.bids[100]) == 1
    assert not book.asks

def test_cancel_order():
    """Test that a single order can be canceled."""
    book = OrderBook()
    order_id = 1
    order = Order(order_id=order_id, side=Side.BUY, price=100, quantity=10, timestamp=1)
    book.add_order(order)
    
    # Sanity check before cancel
    assert book.orders.get(order_id) is not None

    book.cancel_order(order_id)
    
    assert len(book.orders) == 0
    assert order_id not in book.orders
    assert 100 not in book.bids

def test_modify_order():
    """Test that an order can be modified (cancel+add)."""
    book = OrderBook()
    order = Order(order_id=1, side=Side.BUY, price=100, quantity=10, timestamp=1)
    book.add_order(order)
    
    book.modify_order(order_id=1, new_quantity=5)
    
    assert len(book.orders) == 1
    modified_order = book.orders.get(1)
    assert modified_order.quantity == 5
    assert len(book.bids[100]) == 1
    assert book.bids[100][0].quantity == 5
    assert book.bids[100][0].timestamp == 1

def test_full_fill():
    """Test that an aggressing order fully fills a resting order."""
    book = OrderBook()
    resting_order = Order(order_id=1, side=Side.SELL, price=100, quantity=10, timestamp=1)
    book.add_order(resting_order)

    aggressing_order = Order(order_id=2, side=Side.BUY, price=100, quantity=10, timestamp=2)
    trades = book.add_order(aggressing_order)

    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert len(book.orders) == 0 # Both orders should be removed
    assert 100 not in book.asks
    assert 100 not in book.bids

def test_partial_fill_aggressing_order():
    """Test that a new order is partially filled and rests in the book."""
    book = OrderBook()
    resting_order = Order(order_id=1, side=Side.SELL, price=100, quantity=10, timestamp=1)
    book.add_order(resting_order)
    
    aggressing_order = Order(order_id=2, side=Side.BUY, price=100, quantity=20, timestamp=2)
    trades = book.add_order(aggressing_order)

    assert len(trades) == 1
    assert trades[0].quantity == 10
    assert len(book.orders) == 1 # Only the aggressing order should remain
    assert book.orders[2].quantity == 10
    assert book.orders[2].price == 100
    assert not book.asks
    assert len(book.bids[100]) == 1
    assert book.bids[100][0].order_id == 2

def test_multiple_fills():
    """Test a new order filling against multiple resting orders."""
    book = OrderBook()
    book.add_order(Order(order_id=1, side=Side.SELL, price=100, quantity=5, timestamp=1))
    book.add_order(Order(order_id=2, side=Side.SELL, price=100, quantity=5, timestamp=2))
    aggressing_order = Order(order_id=3, side=Side.BUY, price=100, quantity=10, timestamp=3)
    trades = book.add_order(aggressing_order)

    assert len(trades) == 2
    assert sum(t.quantity for t in trades) == 10
    assert len(book.orders) == 0
    assert not book.asks