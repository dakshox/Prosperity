from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Does nothing and probes the state at each iteration. """

        print(jsonpickle.encode(state))

        result = {}
        for product in state.order_depths:
            orders: List[Order] = []
            result[product] = orders
    
        traderData = ""
        
        conversions = 0
        return result, conversions, traderData
