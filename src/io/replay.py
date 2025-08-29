import pandas as pd
import pyarrow.parquet as pq
from src.core.lob import OrderBook

class ReplayEngine:
    """
    Replays market data from a Parquet file.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.events = self._load_events()

    def _load_events(self) -> pd.DataFrame:
        """
        Loads market data events from a Parquet file into a DataFrame.
        """
        table = pq.read_table(self.file_path)
        return table.to_pandas()