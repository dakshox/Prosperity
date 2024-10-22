from datamodel import *
import jsonpickle
from dataclasses import dataclass

starfruit_c = -0.45
starfruit_intercept = 0
STARFRUIT = "STARFRUIT"
AMETHYSTS = "AMETHYSTS"
LIMITS = {
    AMETHYSTS: 20,
    STARFRUIT: 20,
}

@dataclass
class StarfruitData:
    ema0_1: float
    ema0_01: float
    last_mid_price: float

@dataclass
class Data:
    starfruit_data: StarfruitData | None

def sign(x):
    return 1 if x > 0 else -1 if x < 0 else 0

class Trader:
    @staticmethod
    def sanitise_and_sort_orders(orders):
        return sorted([{"price": int(k), "qty": int(v)} for k, v in orders.items()], key=lambda x: x["price"] * -sign(x["qty"]))

    @staticmethod
    def starfruit_strategy(state, data):
        symbol = STARFRUIT
        order_depths = state.order_depths[symbol]
        buy_orders = Trader.sanitise_and_sort_orders(order_depths.buy_orders)
        sell_orders = Trader.sanitise_and_sort_orders(order_depths.sell_orders)

        position = 0 if symbol not in state.position else state.position[symbol]
        max_buy = LIMITS[symbol] - position
        max_sell = position + LIMITS[symbol]

        # print(buy_orders, sell_orders)
        if len(buy_orders) > 0 and len(sell_orders) > 0:
            mid_price = (buy_orders[0]["price"] + sell_orders[0]["price"]) / 2
        else:
            if data is None:
                # No info!
                return {}, ""
            mid_price = data.last_mid_price
        
        if data is None:
            data = StarfruitData(
                ema0_1=mid_price,
                ema0_01=mid_price,
                last_mid_price=mid_price
            )

        data.ema0_1 = 0.1 * mid_price + 0.9 * data.ema0_1
        data.ema0_01 = 0.01 * mid_price + 0.99 * data.ema0_01

        ema_diff = data.ema0_1 - data.ema0_01
        pred_future_diff = ema_diff * starfruit_c + starfruit_intercept
        
        target_price = data.ema0_1 - pred_future_diff

        buy_target = min(data.ema0_1, target_price)
        sell_target = max(data.ema0_1, target_price)
        # print(ema_diff, pred_future_diff, target_price)

        orders = []

        for order in sell_orders:
            if max_buy <= 0:
                break
            if order["price"] < buy_target:
                qty = min(max_buy, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], qty)) # buy
                max_buy -= qty

        for order in buy_orders:
            if max_sell <= 0:
                break
            if order["price"] > sell_target:
                qty = min(max_sell, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], -qty))
                max_sell -= qty
        
        # some market making
        if max_buy > 0:
            orders.append(Order(symbol, round(buy_target - 1.5), max_buy))
        if max_sell > 0:
            orders.append(Order(symbol, round(sell_target + 1.5), -max_sell))

        data.last_mid_price = mid_price

        return orders, data

    @staticmethod
    def amethyst_threshold(pos):
        return 2
        

    @staticmethod
    def amethyst_strategy(state, data):
        symbol = AMETHYSTS
        order_depths = state.order_depths[symbol]
        buy_orders = Trader.sanitise_and_sort_orders(order_depths.buy_orders)
        sell_orders = Trader.sanitise_and_sort_orders(order_depths.sell_orders)

        position = 0 if symbol not in state.position else state.position[symbol]
        max_buy = LIMITS[symbol] - position
        max_sell = position + LIMITS[symbol]

        target_price = 10000
        orders = []

        new_pos = position

        for order in sell_orders:
            if max_buy <= 0:
                break
            if order["price"] < target_price:
                qty = min(max_buy, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], qty))
                max_buy -= qty
                new_pos += qty
        
        for order in buy_orders:
            if max_sell <= 0:
                break
            if order["price"] > target_price:
                qty = min(max_sell, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], -qty))
                max_sell -= qty
                new_pos -= qty

        # # attempt to get position back to 0
        # if new_pos > 0:
        #     # try to sell at target price
        #     amt = min(new_pos, max_sell)
        #     orders.append(Order(symbol, target_price, -amt))
        #     max_sell -= amt
        # if new_pos < 0:
        #     # try to buy at target price
        #     amt = min(-new_pos, max_buy)
        #     orders.append(Order(symbol, target_price, amt))
        #     max_buy -= amt

        # Market make
        if max_buy > 0:
            orders.append(Order(symbol, target_price - Trader.amethyst_threshold(new_pos), max_buy))
        if max_sell > 0:
            orders.append(Order(symbol, target_price + Trader.amethyst_threshold(-new_pos), -max_sell))
        
        return orders, None

    def clean_state(self, state: TradingState):
        # Remove orders of size 0
        def clean_orders(d: dict):
            return {k: v for k, v in d.items() if v != 0}
        for depth in state.order_depths.values():
            depth.buy_orders = clean_orders(depth.buy_orders)
            depth.sell_orders = clean_orders(depth.sell_orders)

    def run(self, state: TradingState, verbose=True):
        if verbose:
            print(jsonpickle.encode(state))

        self.clean_state(state)

        data_str = state.traderData
        if data_str == "":
            data = None
        else:
            data = jsonpickle.decode(data_str, classes=Data)

        orders = {}
        starfruit_orders, starfruit_data = Trader.starfruit_strategy(state, data.starfruit_data if data is not None else None)
        orders[STARFRUIT] = starfruit_orders
        amethyst_orders, amethyst_data = Trader.amethyst_strategy(state, None)
        orders[AMETHYSTS] = amethyst_orders

        return orders, None, jsonpickle.encode(Data(starfruit_data))


if __name__ == "__main__":
    import tools.backtester as backtester
    import tools.log_parser as log_parser
    import numpy as np
    import pandas as pd
    # log = log_parser.parse_log("prober.log", parse_trader_log_as_object=True)
    log = pd.read_csv("../data/prices_round_1_day_0.csv", sep=";")

    for starfruit_c in np.arange(-0.8, -0.3, 0.05):
        print(starfruit_c, backtester.backtest_from_log(lambda *args, **kwargs: Trader().run(*args, **kwargs, verbose=False), log))
