from dataclasses import dataclass
from enum import Enum, auto

class Side(Enum):
    BUY = auto()
    SELL = auto()

@dataclass()
class Order:
    """
    Represents a single limit order.
    """
    order_id: int
    side: Side
    price: int
    quantity: int
    timestamp: int # Microseconds since epoch

@dataclass(frozen=True)
class Trade:
    """
    Represents a trade (fill) resulting from an order match.
    """
    trade_id: int
    aggressing_order_id: int
    resting_order_id: int
    price: int
    quantity: int
    timestamp: int