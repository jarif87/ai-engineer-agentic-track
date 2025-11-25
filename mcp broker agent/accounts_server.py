from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel
import json
from datetime import datetime
import yfinance as yf
import sys

INITIAL_BALANCE = 10_000.0
SPREAD = 0.002

_database = {}

def get_share_price(symbol: str) -> float:
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.history(period="1d")["Close"].iloc[-1]
        return float(price)
    except:
        return 0.0

def write_account(name: str, data: dict):
    _database[name.lower()] = data

def read_account(name: str):
    return _database.get(name.lower())

def write_log(name: str, type_: str, message: str):
    print(f"[{name}] {type_}: {message}", file=sys.stderr,flush=True)

class Transaction(BaseModel):
    symbol: str
    quantity: int
    price: float
    timestamp: str
    rationale: str

    def total(self) -> float:
        return self.quantity * self.price

class Account(BaseModel):
    name: str
    balance: float = INITIAL_BALANCE
    strategy: str = ""
    holdings: dict[str, int] = {}
    transactions: list[Transaction] = []
    portfolio_value_time_series: list[tuple[str, float]] = []

    @classmethod
    def get(cls, name: str):
        fields = read_account(name.lower())
        if not fields:
            fields = {
                "name": name.lower(),
                "balance": INITIAL_BALANCE,
                "strategy": "",
                "holdings": {},
                "transactions": [],
                "portfolio_value_time_series": []
            }
            write_account(name.lower(), fields)
        return cls(**fields)

    def save(self):
        write_account(self.name.lower(), self.model_dump())

    def buy_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        price = get_share_price(symbol)
        if price == 0:
            raise ValueError(f"Unrecognized symbol {symbol}")
        buy_price = price * (1 + SPREAD)
        total_cost = buy_price * quantity
        if total_cost > self.balance:
            raise ValueError("Insufficient funds")
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self.balance -= total_cost
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trx = Transaction(symbol=symbol, quantity=quantity, price=buy_price, timestamp=ts, rationale=rationale)
        self.transactions.append(trx)
        self.save()
        write_log(self.name, "account", f"Bought {quantity} {symbol}")
        return "Buy completed.\n" + self.report()

    def sell_shares(self, symbol: str, quantity: int, rationale: str) -> str:
        if self.holdings.get(symbol, 0) < quantity:
            raise ValueError("Not enough shares")
        price = get_share_price(symbol)
        sell_price = price * (1 - SPREAD)
        proceeds = sell_price * quantity
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol]
        self.balance += proceeds
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        trx = Transaction(symbol=symbol, quantity=-quantity, price=sell_price, timestamp=ts, rationale=rationale)
        self.transactions.append(trx)
        self.save()
        write_log(self.name, "account", f"Sold {quantity} {symbol}")
        return "Sell completed.\n" + self.report()

    def calculate_portfolio_value(self) -> float:
        total = self.balance
        for sym, qty in self.holdings.items():
            total += get_share_price(sym) * qty
        return total

    def report(self) -> str:
        pv = self.calculate_portfolio_value()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.portfolio_value_time_series.append((ts, pv))
        self.save()
        data = self.model_dump()
        data["total_portfolio_value"] = pv
        return json.dumps(data, indent=2)

mcp = FastMCP("accounts_server")

@mcp.tool()
async def get_balance(name: str) -> float:
    return Account.get(name.lower()).balance

@mcp.tool()
async def get_holdings(name: str) -> dict[str, int]:
    return Account.get(name.lower()).holdings

@mcp.tool()
async def buy_shares(name: str, symbol: str, quantity: int, rationale: str) -> str:
    return Account.get(name.lower()).buy_shares(symbol, quantity, rationale)

@mcp.tool()
async def sell_shares(name: str, symbol: str, quantity: int, rationale: str) -> str:
    return Account.get(name.lower()).sell_shares(symbol, quantity, rationale)

@mcp.tool()
async def change_strategy(name: str, strategy: str) -> str:
    acc = Account.get(name.lower())
    acc.strategy = strategy
    acc.save()
    return "Strategy updated"

@mcp.resource("accounts://{name}")
async def read_account_resource(name: str) -> str:
    return Account.get(name.lower()).report()

if __name__ == "__main__":
    mcp.run(transport='stdio')