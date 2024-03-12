import sys
sys.path.append("..")
import datamodel
from typing import *
from tools.log_parser import Log
import copy
from dataclasses import dataclass

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

    print(f"my_orders: {my_orders}, order_depth_dict: {order_depth_dict}, resolving_bids: {resolving_bids}, timestamp: {timestamp}")

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
                print("trade: ", trades[-1])
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

def backtest(trader_func: trader_type, data: Log, iters=None, suppress_warnings=False, limits=KNOWN_LIMITS) -> BacktestResults:
    """
    Backtests against log data from a prober strategy. The prober must call "print(jsonpickle.encode(state))" every round, and print nothing else.
    Please call log_parser.parse_log with parse_trader_log_as_object=True to parse the prober log as an object.

    Important args:
        trader_func: The trader function to backtest
        data: The log to backtest against
        iters: The number of iterations to test (good for testing). If not specified, runs all iterations.
    """

    warn = lambda s: sys.stderr.write(f"[WARN] {s}\n") if not suppress_warnings else None

    trading_states = [l.trader_log for l in data.sandbox_logs]

    activity_df = data.activity_df

    balance = 0
    trader_data = ""
    position = {s: 0 for s in limits.keys()}
    last_round_trades = []

    final_timestamp = 0
    for i, log_state in enumerate(trading_states):
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
            assert all(o.quantity != 0 for o in symbol_orders), f"Order with 0 quantity found: {symbol}, {symbol_orders}"

            current_position = position[symbol]
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
            position[symbol] += bid_delta_position + ask_delta_position
            balance += bid_delta_balance + ask_delta_balance
            if bid_delta_position != 0 and ask_delta_position != 0:
                warn(f"Bid and ask filled at the same time for {symbol} at timestamp {log_state.timestamp}")
        final_timestamp = log_state.timestamp

    profit = balance

    # Liquidate all positions
    for symbol, pos in position.items():
        mid_price = activity_df.query("product == @symbol and timestamp == @final_timestamp").iloc[0]["mid_price"]
        profit += mid_price * pos

    return BacktestResults(
        balance,
        position,
        profit
    )
