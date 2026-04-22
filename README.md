🚀 Trading Algo – Automated Crypto Trading System (Binance Testnet)

Trading Algo is a Python-based algorithmic trading system integrated with the Binance Spot Testnet. It is designed to detect market patterns, generate trade signals, execute simulated trades, and provide real-time performance monitoring through a local web dashboard.

📌 Key Features
🔌 Binance Testnet Integration
Secure API connection via .env file
Executes trades in a risk-free demo environment
📊 Algorithmic Pattern Detection
Analyzes market data to identify trading opportunities
Generates signals including entry, TP (Take Profit), and SL (Stop Loss) levels
💾 Signal Logging System
Stores detected trade signals in .txt files
Acts as a communication bridge between strategy engine and execution layer
⚙️ Automated Trade Execution
Reads signals from file
Executes market orders on Binance Spot Testnet
Uses configurable position sizing (e.g., percentage of balance allocation per trade)
📈 Web Trading Dashboard (Flask - localhost)
Live monitoring at: http://127.0.0.1:5000/
Displays:
Starting balance
Wallet balance
Unrealized / Realized PnL
Total equity
Win/Loss tracking
Open positions with live metrics
📦 Portfolio & Risk Tracking
Tracks performance metrics:
Wins / Losses
Total PnL
Position exposure
Trade value allocation logic
<img width="1366" height="643" alt="image" src="https://github.com/user-attachments/assets/783503ac-3053-49a6-872d-9fbb4a730993" />


# TREDING_ALGO
🧠 System Workflow Market data is analyzed by the trading algorithm Pattern detection triggers buy/sell signals Signals are saved into a .txt file Execution module reads signals and places test trades on Binance Dashboard continuously fetches trade updates User monitors performance in real time via web UI
