from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        product = 'AMETHYSTS'
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []
        position = state.position[product] if len(state.position) > 0 else 0
        acceptable_price = 10000  # Participant should calculate this value
        print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        if position > -15:
            orders.append(Order(product, 10001, -2))
        if position < 15:
            orders.append(Order(product, 9999, 2))

        result[product] = orders
  



		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "SAMPLE" 
        
				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData