"""

Changelog:

01: copy from round 1

"""


from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string
import jsonpickle

STARFRUIT = "STARFRUIT"
AMETHYSTS = "AMETHYSTS"
LIMITS = {
    AMETHYSTS: 20,
    STARFRUIT: 20,
}

class Trader:
    @staticmethod
    def get_position(state, product):
        """Get the current position for a product."""
        return state.position.get(product, 0)

    @staticmethod
    def generate_amethyst_trades(state):
        """Generate trades for AMETHYSTS based on the current position."""
        product = AMETHYSTS
        orders: List[Order] = []
        position = Trader.get_position(state, product)
        order_depth: OrderDepth = state.order_depths.get(product, OrderDepth())
        maxBuy = LIMITS[product] - position
        maxSell = LIMITS[product] + position
        print('Position:', position)
        print(state.own_trades)

        for price, volume in order_depth.sell_orders.items():
            if price < 10000 and maxBuy > 0:
                print('BUY', price, volume, maxBuy)
                orders.append(Order(product, price, min(-volume, maxBuy)))
                maxBuy -= min(-volume, maxBuy)

        for price, volume in order_depth.buy_orders.items():
            if price > 10000 and maxSell > 0:
                print('SELL', price, volume, maxSell)
                orders.append(Order(product, price, -min(volume, maxSell)))
                maxSell -= min(volume, maxSell)
        
        if maxSell > 0:
            print('Market Making MaxSell:', maxSell)
            orders.append(Order(product, 10002, -maxSell))
        if maxBuy > 0:
            print('Market Making MaxBuy:', maxBuy)
            orders.append(Order(product, 9998, maxBuy))
        return orders

    @staticmethod
    def generate_starfruit_trades(state, traderData):
        """Generate trades for STARFRUIT using an EWMA strategy."""
        product = STARFRUIT
        order_depth: OrderDepth = state.order_depths.get(product, OrderDepth())
        position = Trader.get_position(state, product)
        orders: List[Order] = []

        if order_depth.buy_orders and order_depth.sell_orders:
            newBid = int(max(order_depth.buy_orders.keys()))
            newAsk = int(min(order_depth.sell_orders.keys()))
            newMid = (newBid + newAsk) // 2
            maxBuy = LIMITS[product] - position
            maxSell = LIMITS[product] + position

            ewma3 = (0.3 * newMid + 0.7 * float(traderData)) if traderData else newMid
            traderData = str(ewma3)

            #First trade on orders that exist
            for price, volume in order_depth.sell_orders.items():
                if price < ewma3 - .5 and maxBuy > 0:
                    orders.append(Order(product, price, min(-volume, maxBuy)))
                    maxBuy -= min(-volume, maxBuy)
            for price, volume in order_depth.buy_orders.items():
                if price > ewma3 + .5 and maxSell > 0:
                    orders.append(Order(product, price, -min(volume, maxSell)))
                    maxSell -= min(volume, maxSell)

            #Second, market make around ewma
            if maxSell > 0:
                orders.append(Order(product, round(ewma3 + 1.5), -maxSell))
            if maxBuy > 0:
                orders.append(Order(product, round(ewma3 - 1.5), maxBuy))

        return orders, traderData

    @staticmethod
    def clean_state(state: TradingState):
        """Remove orders of size 0."""
        def clean_orders(d: dict):
            return {k: v for k, v in d.items() if v != 0}
        for depth in state.order_depths.values():
            depth.buy_orders = clean_orders(depth.buy_orders)
            depth.sell_orders = clean_orders(depth.sell_orders)

    def run(self, state: TradingState, verbose=True):
        """Main trading logic execution point."""
        if not verbose: # Disable print statements
            global print
            print = lambda *args, **kwargs: None

        Trader.clean_state(state)
        traderData = jsonpickle.decode(state.traderData) if state.traderData else {"starfruit": None}

        result = {}

        # Generate orders for AMETHYSTS and STARFRUIT
        amethyst_orders = Trader.generate_amethyst_trades(state)        
        result[AMETHYSTS] = amethyst_orders

        starfruit_orders, starfruit_traderData = Trader.generate_starfruit_trades(state, traderData["starfruit"])
        result[STARFRUIT] = starfruit_orders

        # traderData = ''
        # Placeholder for conversions and trader data management
        conversions = 1

        traderData = {"starfruit": starfruit_traderData}

        return result, conversions, jsonpickle.encode(traderData)


if __name__ == "__main__":
    from tools.backtester import backtest_from_log
    import pandas as pd
    import functools
    prices_df = pd.read_csv("../../data/data_v1/prices_1.csv", sep=";")
    # trades_df = pd.read_csv("../../data/data_v1/trades_1.csv", sep=";") # idk whats going on with trades rn
    orchids_df = pd.read_csv("../../data/data_v1/prices_2.csv", sep=";")
    print(backtest_from_log(functools.partial(Trader().run, verbose=False), prices_df, None, orchids_df, day=1))
