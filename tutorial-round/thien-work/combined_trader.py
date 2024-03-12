from datamodel import *
import jsonpickle
from dataclasses import dataclass

starfruit_c = -0.45
starfruit_intercept = 0
STARFRUIT = "STARFRUIT"
AMETHYSTS = "AMETHYSTS"
LIMITS = {
    "AMETHYSTS": 20,
    "STARFRUIT": 20,
}

@dataclass
class StarfruitData:
    ema0_1: float
    ema0_01: float
    last_mid_price: float

@dataclass
class Data:
    starfruit_data: StarfruitData | None

class Trader:
    @staticmethod
    def sanitise_orders(orders):
        return [{"price": int(k), "qty": int(v)} for k, v in orders.items()]

    @staticmethod
    def starfruit_strategy(state, data):
        symbol = STARFRUIT
        order_depths = state.order_depths[symbol]
        buy_orders = Trader.sanitise_orders(order_depths.buy_orders)
        sell_orders = Trader.sanitise_orders(order_depths.sell_orders)

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
        # print(ema_diff, pred_future_diff, target_price)

        orders = []

        for order in sell_orders:
            if max_buy <= 0:
                break
            if order["price"] < target_price:
                qty = min(max_buy, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], qty)) # buy
                max_buy -= qty

        for order in buy_orders:
            if max_sell <= 0:
                break
            if order["price"] > target_price:
                qty = min(max_sell, abs(order["qty"]))
                orders.append(Order(symbol, order["price"], -qty))
                max_sell -= qty
        
        # some market making
        if max_buy > 0:
            orders.append(Order(symbol, round(target_price - 1), max_buy))
        if max_sell > 0:
            orders.append(Order(symbol, round(target_price + 1), -max_sell))

        data.last_mid_price = mid_price

        return orders, data

    @staticmethod
    def amethyst_threshold(pos):
        return 2
        

    @staticmethod
    def amethyst_strategy(state, data):
        symbol = AMETHYSTS
        order_depths = state.order_depths[symbol]
        buy_orders = Trader.sanitise_orders(order_depths.buy_orders)
        sell_orders = Trader.sanitise_orders(order_depths.sell_orders)

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
        
        

    def run(self, state: TradingState):

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
    log = log_parser.parse_log("trader4_log.log", parse_trader_log_as_object=True)

    for starfruit_c in np.arange(-0.5, -0.4, 0.005):
        print(starfruit_c, backtester.backtest(Trader().run, log))
