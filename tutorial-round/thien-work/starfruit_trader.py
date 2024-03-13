from datamodel import *
import jsonpickle
from dataclasses import dataclass

starfruit_c = -0.07127450931319589
starfruit_intercept = -0.0014791778084142356
STARFRUIT = "STARFRUIT"
LIMITS = {
    "AMETHYSTS": 20,
    "STARFRUIT": 20,
}

class Trader:
    def run(self, state: TradingState):
        @dataclass
        class Data:
            ema0_1: float
            ema0_01: float
            last_mid_price: float
        
        def sanitise_orders(orders):
            return [{"price": int(k), "qty": int(v)} for k, v in orders.items()]

        data_str = state.traderData
        if data_str == "":
            data = None
        else:
            data = jsonpickle.decode(data_str, classes=Data)

        symbol = STARFRUIT
        order_depths = state.order_depths[symbol]
        buy_orders = sanitise_orders(order_depths.buy_orders)
        sell_orders = sanitise_orders(order_depths.sell_orders)

        position = 0 if symbol not in state.position else state.position[symbol]
        max_buy = LIMITS[symbol] - position
        max_sell = position + LIMITS[symbol]

        # print(buy_orders, sell_orders)
        if len(buy_orders) > 0 and len(sell_orders) > 0:
            mid_price = (buy_orders[0]["price"] + sell_orders[0]["price"]) / 2
        else:
            if data is None:
                # No info!
                return {}, None, ""
            mid_price = data.last_mid_price
        
        if data is None:
            data = Data(
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

        orders = {symbol: []}

        for order in sell_orders:
            if max_buy <= 0:
                break
            if order["price"] < target_price:
                qty = min(max_buy, abs(order["qty"]))
                orders[symbol].append(Order(symbol, order["price"], qty)) # buy
                max_buy -= qty

        for order in buy_orders:
            if max_sell <= 0:
                break
            if order["price"] > target_price:
                qty = min(max_sell, abs(order["qty"]))
                orders[symbol].append(Order(symbol, order["price"], -qty))
                max_sell -= qty
        
        # some market making
        if max_buy > 0:
            orders[symbol].append(Order(symbol, round(target_price - 1), max_buy))
        if max_sell > 0:
            orders[symbol].append(Order(symbol, round(target_price + 1), -max_sell))

        data.last_mid_price = mid_price

        return orders, None, jsonpickle.encode(data)


if __name__ == "__main__":
    import tools.backtester as backtester
    import tools.log_parser as log_parser
    log = log_parser.parse_log("trader4_log.log", parse_trader_log_as_object=True)
    print(backtester.backtest(Trader().run, log))
