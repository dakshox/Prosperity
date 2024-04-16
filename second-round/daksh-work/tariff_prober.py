from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Does nothing and probes the state at each iteration. """

        position = state.position['ORCHIDS'] if 'ORCHIDS' in state.position else 0
        print(position)

        result = {}
        
        if (state.timestamp // 100) % 2 == 0:
            result['ORCHIDS'] = [Order('ORCHIDS', 0, -20)]
            conversions = 0
        else:
            conversions = -position

        traderData = ""
        
        # conversions = 0
        return result, conversions, traderData
