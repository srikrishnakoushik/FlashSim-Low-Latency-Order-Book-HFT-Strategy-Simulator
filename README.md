 
### Low-Latency Limit Order Book & HFT Strategy Simulator

FlashSim is a **production-grade, low-latency Limit Order Book (LOB) simulator** designed for **developing, testing, and backtesting high-frequency trading (HFT) strategies**.

The project provides an **end-to-end simulation framework**, including a deterministic matching engine, a configurable market data pipeline, a backtesting engine with analytics, and a real-time visualization dashboard.

The core of FlashSim is a **price–time priority matching engine implemented in pure Python**, with a modular architecture that allows future acceleration of performance-critical paths using C++ or other low-level optimizations.

---

## 📌 Project Overview

High-frequency trading strategies depend heavily on:

- Market microstructure behavior  
- Order queue positioning  
- Latency and execution priority  
- Deterministic matching logic  

Most academic models abstract these details away.

**FlashSim focuses on execution realism rather than prediction**, allowing strategies to be evaluated under realistic order book dynamics and latency-sensitive conditions.

---

## 🎯 Key Features

- **Low-Latency Matching Engine**  
  - Deterministic limit order book  
  - Price–time priority matching  
  - Supports adds, cancels, partial fills  

- **Dynamic Market Data Pipeline**  
  - Synthetic market data generation  
  - Configurable volatility regimes  
  - Market replay for reproducible experiments  

- **Microstructure Trading Strategy**  
  - Imbalance-based strategy included  
  - Demonstrates interaction with the order book  

- **Comprehensive Backtester**  
  - Simulates trades and execution  
  - Reports PnL, inventory, win rate, and fills  

- **Real-Time Visualization Dashboard**  
  - Streamlit-based UI  
  - Live order book and trade visualization  

- **Professional CLI Interface**  
  - Flexible command-line execution  
  - Supports backtesting and dashboard modes  

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    CLI[CLI / Runner]
    GEN[Market Data Generator]
    LOB[Limit Order Book Engine]
    STRAT[Trading Strategy]
    BT[Backtester & Metrics]
    DASH[Streamlit Dashboard]

    CLI --> GEN
    GEN --> LOB
    STRAT --> LOB
    LOB --> BT
    LOB --> DASH
````

---

## 🔄 Execution Flow

1. Market events are generated or replayed
2. Orders are submitted to the limit order book
3. Matching engine processes events using price–time priority
4. Strategy reacts to order book state and submits orders
5. Trades are recorded by the backtester
6. Metrics and analytics are computed
7. Live state is optionally visualized in the dashboard

---

## 🧩 Repository Structure

```
lob-sim/
├── data/                 # Generated market data (.parquet)
├── src/
│   ├── core/             # Core order book logic
│   │   ├── lob.py
│   │   └── order.py
│   ├── io/               # Market data generation & replay
│   │   ├── generator.py
│   │   └── replay.py
│   ├── backtest/         # Backtesting engine & analytics
│   │   └── backtester.py
│   ├── strategy/         # Trading strategies
│   │   └── imbalance.py
│   └── dash/             # Streamlit dashboard
│       └── app.py
├── run.py                # Main execution script
├── run_all.sh             # Combined dashboard + backtest runner
└── pyproject.toml        # Project configuration & dependencies
```

---

## ⚙️ Technology Stack

| Component     | Technology             |
| ------------- | ---------------------- |
| Language      | Python 3.9+            |
| Data          | NumPy, Pandas, PyArrow |
| Visualization | Streamlit              |
| Storage       | Parquet                |
| Tooling       | CLI, Shell Scripts     |

---

## 🛠️ Setup & Installation

### 1️⃣ Create Virtual Environment

```bash
python3.9 -m venv .venv
source .venv/bin/activate
```

---

### 2️⃣ Install Dependencies

```bash
pip install pytest black ruff pyarrow numpy pandas streamlit
```

(Dependencies are defined in `pyproject.toml`.)

---

## ▶️ How to Run

### Run a Low-Volatility Backtest

```bash
python3 run.py --events 5000 --volatility 0.002
```

---

### Run a High-Volatility Backtest

```bash
python3 run.py --events 5000 --volatility 0.05
```

---

### Run the Real-Time Dashboard

```bash
python3 run.py --mode dashboard
```

---

### Run Backtest + Dashboard Together

```bash
./run_all.sh
```

---

## 📊 Sample Backtest Results

Example output from a high-volatility simulation:

```
--- Backtest Results ---
Total Fills: 119
Final PnL: -556.0
Final Inventory: 465.0
Win Rate: 0.61
```

These results illustrate how execution quality, volatility, and inventory risk directly affect performance.

---

## ⚠️ Limitations

* Matching engine implemented in Python (single-threaded)
* Synthetic data only (no live exchange feeds)
* Strategy set intentionally minimal for clarity
* No transaction cost or exchange fee modeling

---

## 🗺️ Future Enhancements

* C++ acceleration of matching engine
* Multi-asset order book support
* Latency injection and network delay simulation
* Additional market microstructure strategies
* Integration with real historical market data

---

## 🎯 What This Project Demonstrates

* Deep understanding of **market microstructure**
* Deterministic order book implementation
* Execution-driven strategy evaluation
* Latency-aware system thinking
* Clean, modular system design

---

## ⚠️ Disclaimer

This project is intended for **educational and research purposes only** and does not represent a production trading system or financial advice.

---

## 📄 License

MIT License

```



