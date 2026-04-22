import json
import os
import time
from flask import Flask, render_template_string, Response
from binance.client import Client
from dotenv import load_dotenv

# =========================
# INIT
# =========================
load_dotenv()

API_KEY = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

client = Client(API_KEY, API_SECRET)
client.API_URL = "https://testnet.binance.vision/api"

POSITIONS_FILE = "positions.json"
PORTFOLIO_FILE = "portfolio.json"

app = Flask(__name__)

# =========================
# CACHE
# =========================
price_cache = {}
last_cache = 0
CACHE_TTL = 2


def load_json(file):
    if not os.path.exists(file):
        return {}
    with open(file) as f:
        return json.load(f)


def get_wallet_balance():
    return float(client.get_asset_balance(asset="USDT")["free"])


def get_price(symbol):

    global last_cache

    if time.time() - last_cache > CACHE_TTL:
        price_cache.clear()

    if symbol not in price_cache:
        price_cache[symbol] = float(
            client.get_symbol_ticker(symbol=symbol)["price"]
        )

    return price_cache[symbol]


# =========================
# API
# =========================
@app.route("/api/data")
def data():

    portfolio = load_json(PORTFOLIO_FILE)
    positions = load_json(POSITIONS_FILE)

    wallet = get_wallet_balance()

    starting = portfolio.get("starting_balance", wallet)
    realized = portfolio.get("realized_pnl", 0)
    wins = portfolio.get("wins", 0)
    losses = portfolio.get("losses", 0)

    open_positions = []
    unrealized = 0

    for sym, v in positions.items():

        if v["status"] != "OPEN":
            continue

        price = get_price(sym)

        entry = v["entry"]
        qty = v["qty"]

        pnl = (price - entry) * qty
        pct = ((price - entry) / entry) * 100

        trade_value = entry * qty
        market_value = price * qty

        unrealized += pnl

        open_positions.append({
            "symbol": sym,
            "side": "LONG",
            "qty": qty,
            "pnl": pnl,
            "pct": pct,
            "trade": trade_value,
            "market": market_value
        })

    total_equity = wallet + unrealized
    total_pnl = total_equity - starting

    return Response(json.dumps({

        "starting": starting,
        "wallet": wallet,
        "unrealized": unrealized,
        "realized": realized,
        "total_pnl": total_pnl,
        "equity": total_equity,
        "wins": wins,
        "losses": losses,
        "positions": open_positions

    }), mimetype="application/json")


# =========================
# HTML
# =========================
HTML = """
<!DOCTYPE html>
<html>
<head>
<title>Trading Dashboard</title>

<style>

body{
background:#0f172a;
color:white;
font-family:Arial;
padding:20px;
}

.grid{
display:grid;
grid-template-columns:repeat(4,1fr);
gap:10px;
margin-bottom:20px;
}

.card{
background:#1e293b;
padding:15px;
border-radius:10px;
}

table{
width:100%;
border-collapse:collapse;
}

th,td{
padding:12px;
border-bottom:1px solid #334155;
}

tr:hover{
background:#1e293b;
}

.green{color:#22c55e}
.red{color:#ef4444}

</style>

</head>

<body>

<h1>🚀 Trading Dashboard</h1>

<div class="grid">

<div class="card">💰 Starting: <span id="starting"></span></div>
<div class="card">🏦 Wallet: <span id="wallet"></span></div>
<div class="card">📈 Unrealized: <span id="unrealized"></span></div>
<div class="card">💵 Realized: <span id="realized"></span></div>

<div class="card">📊 Total PnL: <span id="total"></span></div>
<div class="card">📦 Equity: <span id="equity"></span></div>
<div class="card">🟢 Wins: <span id="wins"></span></div>
<div class="card">🔴 Losses: <span id="losses"></span></div>

</div>

<h2>Open Positions</h2>

<table>

<thead>
<tr>
<th>Symbol</th>
<th>Side</th>
<th>Qty</th>
<th>Unrealized</th>
<th>%</th>
<th>Trade Value</th>
<th>Market Value</th>
</tr>
</thead>

<tbody id="table"></tbody>

</table>

<script>

async function load(){

let res = await fetch("/api/data")
let data = await res.json()

document.getElementById("starting").innerText = data.starting.toFixed(2)
document.getElementById("wallet").innerText = data.wallet.toFixed(2)
document.getElementById("unrealized").innerText = data.unrealized.toFixed(2)
document.getElementById("realized").innerText = data.realized.toFixed(2)
document.getElementById("total").innerText = data.total_pnl.toFixed(2)
document.getElementById("equity").innerText = data.equity.toFixed(2)
document.getElementById("wins").innerText = data.wins
document.getElementById("losses").innerText = data.losses

let html=""

data.positions.forEach(p=>{

let color = p.pnl>=0 ? "green":"red"

html+=`
<tr>
<td>${p.symbol}</td>
<td>${p.side}</td>
<td>${p.qty.toFixed(4)}</td>
<td class="${color}">${p.pnl.toFixed(2)}</td>
<td class="${color}">${p.pct.toFixed(2)}%</td>
<td>${p.trade.toFixed(2)}</td>
<td>${p.market.toFixed(2)}</td>
</tr>
`
})

document.getElementById("table").innerHTML=html

}

setInterval(load,1500)
load()

</script>

</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML)


if __name__ == "__main__":
    print("🌐 http://127.0.0.1:5000")
    app.run(debug=True, threaded=True)