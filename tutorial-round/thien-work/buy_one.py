from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Does nothing and probes the state at each iteration. """

        print(jsonpickle.encode(state))

        result = {}
        for product in state.listings.keys():
            result[product] = []
            pos = state.position[product] if product in state.position else 0
            if product == "STARFRUIT" and pos == 0:
                result[product].append(Order(product, 1000000, 1))
    
        traderData = ""
        
        conversions = 0
        return result, conversions, traderData
