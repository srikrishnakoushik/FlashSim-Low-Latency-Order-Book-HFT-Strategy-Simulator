import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import numpy as np
import random

from src.core.order import Order, Side, Trade
from src.core.lob import OrderBook

class MarketDataGenerator:
    """
    Generates a stream of market data events and records them to Parquet.
    """
    def __init__(self, start_time: int, event_count: int, file_path: str, volatility: float = 0.01):
        self.start_time = start_time
        self.event_count = event_count
        self.file_path = file_path
        self.book = OrderBook()
        self.volatility = volatility
        self.order_id_counter = 0

    def generate_and_record(self):
        """
        Generates events, processes them through the LOB, and saves the output.
        """
        all_events = []
        
        # We need a reproducible seed for deterministic data generation
        np.random.seed(0)
        random.seed(0)

        for i in range(self.event_count):
            event_time = self.start_time + i
            
            # Simple logic to generate a mix of events
            event_type = np.random.choice(['ADD', 'CANCEL', 'MARKET'], p=[0.7, 0.2, 0.1])
            
            if event_type == 'ADD':
                self.order_id_counter += 1
                price = int(1000 * (1 + np.random.uniform(-self.volatility, self.volatility)))
                quantity = random.randint(1, 100)
                side = random.choice([Side.BUY, Side.SELL])
                
                order = Order(
                    order_id=self.order_id_counter,
                    side=side,
                    price=price,
                    quantity=quantity,
                    timestamp=event_time
                )
                
                self.book.add_order(order)
                all_events.append({
                    'timestamp': event_time,
                    'event_type': 'ADD',
                    'order_id': order.order_id,
                    'side': order.side.name,
                    'price': order.price,
                    'quantity': order.quantity,
                    'trades_count': 0,
                    'trade_price': None,
                    'trade_quantity': None
                })
            elif event_type == 'CANCEL' and self.book.orders:
                order_id_to_cancel = random.choice(list(self.book.orders.keys()))
                self.book.cancel_order(order_id_to_cancel)
                all_events.append({
                    'timestamp': event_time,
                    'event_type': 'CANCEL',
                    'order_id': order_id_to_cancel,
                    'side': None,
                    'price': None,
                    'quantity': None,
                    'trades_count': 0,
                    'trade_price': None,
                    'trade_quantity': None
                })
            elif event_type == 'MARKET':
                self.order_id_counter += 1
                quantity = random.randint(50, 200)
                side = random.choice([Side.BUY, Side.SELL])

                # Fix for the TypeError: Check if best prices exist before creating a market order
                best_price = None
                if side == Side.BUY and self.book.best_ask is not None:
                    best_price = self.book.best_ask
                elif side == Side.SELL and self.book.best_bid is not None:
                    best_price = self.book.best_bid
                
                # If no best price exists, we use a default price to prevent errors
                if best_price is None:
                    best_price = 1000

                order = Order(
                    order_id=self.order_id_counter,
                    side=side,
                    price=best_price,
                    quantity=quantity,
                    timestamp=event_time
                )
                
                trades = self.book.add_order(order)
                if trades:
                    for trade in trades:
                        all_events.append({
                            'timestamp': trade.timestamp,
                            'event_type': 'TRADE',
                            'order_id': order.order_id,
                            'side': order.side.name,
                            'price': order.price,
                            'quantity': order.quantity,
                            'trades_count': len(trades),
                            'trade_price': trade.price,
                            'trade_quantity': trade.quantity
                        })
                else:
                    all_events.append({
                        'timestamp': event_time,
                        'event_type': 'MARKET_NO_TRADE',
                        'order_id': order.order_id,
                        'side': order.side.name,
                        'price': order.price,
                        'quantity': order.quantity,
                        'trades_count': 0,
                        'trade_price': None,
                        'trade_quantity': None
                    })

        # Save to Parquet
        df = pd.DataFrame(all_events)
        table = pa.Table.from_pandas(df)
        pq.write_table(table, self.file_path)
        print(f"Generated {len(all_events)} events and saved to {self.file_path}")