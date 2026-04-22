import re
import time
import os
import json
from dotenv import load_dotenv

from binance.client import Client
from binance.enums import *

# =========================
# INIT
# =========================
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

FILE_PATH = "alerts_log.txt"
TRADE_LOG = "trade_log.txt"
POSITIONS_FILE = "positions.json"
PORTFOLIO_FILE = "portfolio.json"

print("🚀 PRO TRADING BOT STARTED")

# =========================
# INIT FILES
# =========================
def init_files():
    if not os.path.exists(POSITIONS_FILE):
        with open(POSITIONS_FILE, "w") as f:
            json.dump({}, f)

init_files()


def init_portfolio():
    if not os.path.exists(PORTFOLIO_FILE):
        balance = client.get_asset_balance(asset="USDT")
        starting = float(balance["free"])

        data = {
            "starting_balance": starting,
            "realized_pnl": 0.0,
            "wins": 0,
            "losses": 0
        }

        with open(PORTFOLIO_FILE, "w") as f:
            json.dump(data, f, indent=4)

init_portfolio()


# =========================
# HELPERS
# =========================
def get_wallet_balance():
    return float(client.get_asset_balance(asset="USDT")["free"])


def get_price(symbol):
    return float(client.get_symbol_ticker(symbol=symbol)["price"])


# =========================
# RISK MANAGEMENT
# =========================
def get_trade_amount():
    total = get_wallet_balance()
    trade = round(total * 0.10, 2)

    print(f"💰 Balance: {total}")
    print(f"📊 Trade Size: {trade}")

    return trade


# =========================
# POSITION STORAGE
# =========================
def save_position(symbol, qty, entry, tp, sl):

    with open(POSITIONS_FILE, "r") as f:
        data = json.load(f)

    data[symbol] = {
        "qty": qty,
        "entry": entry,
        "tp": tp,
        "sl": sl,
        "status": "OPEN"
    }

    with open(POSITIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)


# =========================
# LOGGING
# =========================
def log_trade(symbol, qty, tp, sl, status):

    with open(TRADE_LOG, "a") as f:
        f.write(f"""
TIME: {time.ctime()}
SYMBOL: {symbol}
QTY: {qty}
TP: {tp}
SL: {sl}
STATUS: {status}
-----------------------------
""")


# =========================
# PARSER
# =========================
def parse_alert(block):

    clean = block.replace("*", "").replace("`", "")

    asset = re.search(r"Asset:\s*([A-Z]+/[A-Z]+)", clean)
    tp = re.search(r"TP\s*=\s*([0-9.]+)", clean)
    sl = re.search(r"SL\s*=\s*([0-9.]+)", clean)

    if not asset or not tp or not sl:
        return None, None, None

    symbol = asset.group(1).replace("/", "").upper()

    return symbol, float(tp.group(1)), float(sl.group(1))


# =========================
# TRADE EXECUTION
# =========================
def execute_trade(symbol, tp, sl):

    try:

        amount = get_trade_amount()

        print(f"\n🚀 BUY {symbol}")

        order = client.create_order(
            symbol=symbol,
            side=SIDE_BUY,
            type=ORDER_TYPE_MARKET,
            quoteOrderQty=amount
        )

        fills = order["fills"]

        qty = sum(float(f["qty"]) for f in fills)
        entry = sum(float(f["price"]) * float(f["qty"]) for f in fills) / qty

        save_position(symbol, qty, entry, tp, sl)
        log_trade(symbol, qty, tp, sl, "OPEN")

        print("✅ Trade Executed")

        return True

    except Exception as e:
        print("ERROR:", e)
        return False


# =========================
# WATCHER LOOP
# =========================
last_size = 0

print(f"📡 Watching {FILE_PATH}")

while True:

    try:

        if os.path.exists(FILE_PATH):

            size = os.path.getsize(FILE_PATH)

            if size > last_size:

                with open(FILE_PATH, "r") as f:
                    f.seek(last_size)
                    new = f.read()

                last_size = size

                alerts = new.split("------------------------------------------------------------")

                for alert in alerts:

                    if "HONEYPOT" not in alert.upper():
                        continue

                    symbol, tp, sl = parse_alert(alert)

                    if symbol:
                        execute_trade(symbol, tp, sl)

        time.sleep(3)

    except Exception as e:

        print("Loop error:", e)
        time.sleep(5)