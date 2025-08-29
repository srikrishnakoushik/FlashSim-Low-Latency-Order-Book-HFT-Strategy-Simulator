import pandas as pd
import pyarrow.parquet as pq
import time
from src.core.lob import OrderBook

class ReplayEngine:
    """
    Replays market data from a Parquet file.
    """
    def __init__(self, file_path: str, speed: float = 1.0):
        self.file_path = file_path
        self.speed = speed
        self.events = self._load_events()

    def _load_events(self) -> pd.DataFrame:
        """
        Loads market data events from a Parquet file into a DataFrame.
        """
        table = pq.read_table(self.file_path)
        return table.to_pandas()

    def start_replay(self):
        """
        Replays the events from the loaded data at the specified speed.
        """
        print(f"Starting replay of {len(self.events)} events at {self.speed}x speed...")
        
        last_event_time = self.events.iloc[0]['timestamp']
        
        for index, event in self.events.iterrows():
            current_event_time = event['timestamp']
            time_delta = current_event_time - last_event_time
            
            # Wall-clock simulation
            sleep_time = time_delta / (1_000_000 * self.speed) # events.timestamp are in microseconds
            if sleep_time > 0:
                time.sleep(sleep_time)

            # Process the event here
            # For now, we'll just print it. In the next step, we'll connect it to a backtester.
            print(f"[{current_event_time}] Replaying event: {event['event_type']} for order {event['order_id']}")

            last_event_time = current_event_time
            
        print("Replay finished.")