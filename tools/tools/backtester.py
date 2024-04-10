import sys
sys.path.append("..")
import datamodel
from typing import *
from tools.log_parser import Log
import copy
from dataclasses import dataclass
from abc import ABC, abstractmethod
import pandas as pd

trader_type = Callable[[datamodel.TradingState], Tuple[Dict[str, List[datamodel.Order]], Any, str]]

KNOWN_LIMITS = {
    "AMETHYSTS": 20,
    "STARFRUIT": 20,
}

def _resolve_orders(my_orders: list[datamodel.Order], order_depth_dict: Dict[int, int], resolving_bids: bool, trades: list[datamodel.Trade], timestamp: int) -> Tuple[int, int]:
    """ Returns (delta_position, delta_balance) """
    delta_position = 0
    delta_balance = 0
    my_orders.sort(key=lambda o: o.price, reverse=(not resolving_bids))
    for order in my_orders:
        order.quantity = abs(order.quantity)
        order.price = int(order.price)
    order_ptr = 0

    for price, qty in order_depth_dict.items():
        price = int(price)
        qty = abs(int(qty))
        while order_ptr < len(my_orders) and my_orders[order_ptr].quantity <= 0:
            order_ptr += 1
        while qty > 0 and order_ptr < len(my_orders):
            if (
                (resolving_bids and my_orders[order_ptr].price >= price) or
                (not resolving_bids and my_orders[order_ptr].price <= price)
            ):
                order_qty = min(qty, my_orders[order_ptr].quantity)
                qty -= order_qty
                delta_position += order_qty if resolving_bids else -order_qty
                total_price = order_qty * price
                delta_balance += -total_price if resolving_bids else total_price
                my_orders[order_ptr].quantity -= order_qty
                trades.append(datamodel.Trade(
                    symbol=my_orders[order_ptr].symbol,
                    price=price,
                    quantity=order_qty,
                    buyer="SUBMISSION" if resolving_bids else "",
                    seller="" if resolving_bids else "SUBMISSION",
                    timestamp=timestamp,
                ))
                if my_orders[order_ptr].quantity == 0:
                    order_ptr += 1
            else:
                order_ptr += 1
        if order_ptr >= len(my_orders):
            break
    return delta_position, delta_balance

@dataclass
class BacktestResults:
    balance: int
    position: Dict[str, int]
    profit: int
    balance_by_symbol: Dict[str, int]
    profit_by_symbol: Dict[str, int]

class _ActivityStream(ABC):
    @abstractmethod
    def __iter__(self) -> Iterator[datamodel.TradingState]:
        """
        Returns a iterator of TradingState objects with the following filled in:
        - timestamp
        - listings
        - order_depths
        - market_trades
        - observations

        Missing values can be filled with None.
        """
        pass

    @abstractmethod
    def get_mid_price_at(self, timestamp: int) -> int:
        pass


class _ActivityStreamDF(_ActivityStream):
    def __init__(self, log: Log):
        self.log = log

    def __iter__(self) -> Iterator[datamodel.TradingState]:
        for l in self.log.sandbox_logs:
            yield l.trader_log

    def get_mid_price_at(self, timestamp: int, symbol: str) -> int:
        return self.log.activity_df.query("product == @symbol and timestamp == @timestamp").iloc[0]["mid_price"]


class _ActivityStreamPriceLog(_ActivityStream):
    def __init__(self, price_logs: pd.DataFrame):
        self.price_logs = price_logs
        self.price_logs_by_timestamp = self.price_logs.groupby("timestamp")

    def __iter__(self) -> Iterator[datamodel.TradingState]:
        for name, group in self.price_logs_by_timestamp:
            listings = {}
            order_depths = {}
            for idx, row in group.iterrows():
                listings[row["product"]] = datamodel.Listing(row["product"], row["product"], 1)
                order_depths[row["product"]] = datamodel.OrderDepth()
                for i in (1, 2, 3):
                    if not pd.isna(row[f"bid_price_{i}"]):
                        order_depths[row["product"]].buy_orders[int(row[f"bid_price_{i}"])] = int(row[f"bid_volume_{i}"])
                    if not pd.isna(row[f"ask_price_{i}"]):
                        order_depths[row["product"]].sell_orders[int(row[f"ask_price_{i}"])] = -int(row[f"ask_volume_{i}"])
            yield datamodel.TradingState(
                traderData=None,
                timestamp=name,
                listings=listings,
                order_depths=order_depths,
                market_trades={}, # If this is ever important, please add functionality to parse market trades from logs!
                observations={}, # This is not important for now...
                own_trades=None,
                position=None,
            )

    def get_mid_price_at(self, timestamp: int, symbol: str) -> int:
        return self.price_logs.query("product == @symbol and timestamp == @timestamp").iloc[0]["mid_price"]

def _backtest_from_stream(trader_func: trader_type, activity_stream: _ActivityStream, iters=None, suppress_warnings=False, limits=KNOWN_LIMITS) -> BacktestResults:
    warn = lambda s: sys.stderr.write(f"[WARN] {s}\n") if not suppress_warnings else None

    balance = 0
    trader_data = ""
    position = {}
    last_round_trades = []
    balance_by_symbol = {}
    profit_by_symbol = {}

    final_timestamp = 0
    for i, log_state in enumerate(activity_stream):
        if iters is not None and i >= iters:
            break
        if log_state is None:
            warn(f"Empty trading state at position {i}, skipping")
            continue
        trading_state = datamodel.TradingState(
            trader_data,
            timestamp=log_state.timestamp,
            listings=log_state.listings,
            order_depths=log_state.order_depths,
            own_trades=last_round_trades,
            market_trades=log_state.market_trades, # NOT ACCURATE; this is using data from the probe, so it's not affected by what trades you make
            position=copy.deepcopy(position),
            observations=log_state.observations)
        orders, _, trader_data = trader_func(trading_state)
        last_round_trades = []

        assert isinstance(trader_data, str)

        # resolve orders
        for symbol, symbol_orders in orders.items():
            if any(o.quantity == 0 for o in symbol_orders):
                warn(f"Order with 0 quantity found: {symbol}, timestamp={trading_state.timestamp}, {symbol_orders},")

            current_position = position[symbol] if symbol in position.keys() else 0
            bid_orders = [o for o in symbol_orders if o.quantity > 0]
            ask_orders = [o for o in symbol_orders if o.quantity < 0]

            # Over limit?
            bid_quantity = sum(o.quantity for o in bid_orders)
            ask_quantity = sum(-o.quantity for o in ask_orders)

            if current_position + bid_quantity > limits[symbol] or current_position - ask_quantity < -limits[symbol]:
                warn(f"Over order limit for {symbol} at timestamp {log_state.timestamp}, skipping orders")
                continue

            # Resolve our bids/asks
            bid_delta_position, bid_delta_balance = _resolve_orders(
                bid_orders,
                log_state.order_depths[symbol].sell_orders,
                resolving_bids=True,
                trades=last_round_trades,
                timestamp=log_state.timestamp
            )
            ask_delta_position, ask_delta_balance = _resolve_orders(
                ask_orders,
                log_state.order_depths[symbol].buy_orders,
                resolving_bids=False,
                trades=last_round_trades,
                timestamp=log_state.timestamp
            )
            if bid_delta_position + ask_delta_position != 0:
                if symbol not in position.keys():
                    position[symbol] = 0
                position[symbol] += bid_delta_position + ask_delta_position

            balance += bid_delta_balance + ask_delta_balance
            if symbol not in balance_by_symbol.keys():
                balance_by_symbol[symbol] = 0
            balance_by_symbol[symbol] += bid_delta_balance + ask_delta_balance

            if bid_delta_position != 0 and ask_delta_position != 0:
                warn(f"Bid and ask filled at the same time for {symbol} at timestamp {log_state.timestamp}")
        final_timestamp = log_state.timestamp

    profit = balance

    # Liquidate all positions
    for symbol, pos in position.items():
        # mid_price = activity_df.query("product == @symbol and timestamp == @final_timestamp").iloc[0]["mid_price"]
        mid_price = activity_stream.get_mid_price_at(final_timestamp, symbol)
        profit += mid_price * pos
        profit_by_symbol[symbol] = mid_price * pos + balance_by_symbol[symbol]

    return BacktestResults(
        balance,
        position,
        profit,
        balance_by_symbol,
        profit_by_symbol
    )

def backtest(trader_func: trader_type, data: Log, *args, **kwargs) -> BacktestResults:
    """
    Backtests against log data from a prober strategy. The prober must call "print(jsonpickle.encode(state))" every round, and print nothing else.
    Please call log_parser.parse_log with parse_trader_log_as_object=True to parse the prober log as an object.

    Important args:
        trader_func: The trader function to backtest
        data: The log to backtest against
        iters: The number of iterations to test (good for testing). If not specified, runs all iterations.
        suppress_warnings: If True, suppresses warnings (but you should probably fix the issues, because they are usually very bad)
        limits: The limits for each symbol. If new symbols are added, please add them to KNOWN_LIMITS (the default).
    """
    activity_stream = _ActivityStreamDF(data)
    return _backtest_from_stream(trader_func, activity_stream, *args, **kwargs)

def backtest_from_log(trader_func: trader_type, activity_df: pd.DataFrame, *args, **kwargs) -> BacktestResults:
    """
    Backtests against historical log data. (e.g. from strategies, or "data in a bottle", in data/)

    Important args:
        trader_func: The trader function to backtest
        activity_df: the data in DataFrame format (pd.read_csv(file_path, sep=";"))
        iters: The number of iterations to test (good for testing). If not specified, runs all iterations.
        suppress_warnings: If True, suppresses warnings (but you should probably fix the issues, because they are usually very bad)
        limits: The limits for each symbol. If new symbols are added, please add them to KNOWN_LIMITS (the default).
    """
    activity_stream = _ActivityStreamPriceLog(activity_df)
    return _backtest_from_stream(trader_func, activity_stream, *args, **kwargs)
