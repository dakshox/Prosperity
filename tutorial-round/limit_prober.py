from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Good for finding out order limits."""

        print(jsonpickle.encode(state))

        result = {}
        for product in state.listings.keys():
            orders: List[Order] = [Order(product, 10 ** 9, 1)]
            result[product] = orders
    
        traderData = ""
        
        conversions = 0
        return result, conversions, traderData
