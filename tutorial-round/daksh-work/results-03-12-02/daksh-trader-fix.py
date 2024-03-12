from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        product = 'STARFRUIT'
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []
        position = state.position[product] if len(state.position) > 0 else 0
        # acceptable_price = 10000
        # print("Acceptable price : " + str(acceptable_price))
        # print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))

        # if position > -15:
        #     orders.append(Order(product, 10001, -2))
        # if position < 15:
        #     orders.append(Order(product, 9999, 2))
        traderData = state.traderData
        newBid = max(order_depth.buy_orders.keys())
        newAsk = min(order_depth.sell_orders.keys())
        newBid_size = order_depth.buy_orders[newBid]
        newAsk_size = order_depth.sell_orders[newAsk]

        if traderData != "":
            #Check bid or ask has moved by a lot
            oldBidAsk = traderData.split(",")
            oldBid, oldAsk = int(oldBidAsk[0]), int(oldBidAsk[1])
            if newBid > oldBid + 4 & position > -17:
                orders.append(Order(product, newBid, -2))
                print("newBid:", newBid, "oldBid:", oldBid, "position:", position, "orders:", orders)
            if newAsk < oldAsk - 4 & position < 17:
                orders.append(Order(product, newAsk, 2))
                print("newAsk:", newAsk, "oldAsk:", oldAsk, "position:", position, "orders:", orders)
            traderData = str(newBid)+","+ str(newAsk)
        result[product] = orders
        traderData = str(newBid)+","+ str(newAsk)



		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        
				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData