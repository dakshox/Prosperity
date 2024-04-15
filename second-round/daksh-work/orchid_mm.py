from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Market Making best bid + 1 and best ask - 1 """

        product = 'ORCHIDS'
        order_depth: OrderDepth = state.order_depths.get(product, OrderDepth())
        position = state.position[product] if product in state.position else 0

        

        # island_asks = state.order_depths['ORCHIDS'].askPrice
        island_bid = int(max(order_depth.buy_orders.keys()))
        # island_bid_vol = order_depth.buy_orders[island_bid]
        island_ask = int(min(order_depth.sell_orders.keys()))
        # island_ask_vol = order_depth.sell_orders[island_ask]

        result = {}
        orders = []
        maxBuy = 100 - position
        maxSell = 100 + position

        if maxSell > 0:
            print('Market Making Sell:', island_ask - 1, - min(20, maxSell))
            orders.append(Order(product, island_ask - 1, - min(20, maxSell)))
        if maxBuy > 0 and island_ask - 1 > island_bid:
            print('Market Making Buy:', island_bid + 1, min(20, maxBuy))
            orders.append(Order(product, island_bid + 1, min(20, maxBuy)))

        print('Position:', position)
        result[product] = orders
        conversions = 0
        traderData = ""


        return result, conversions, traderData
