from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

class Trader:
    
    def run(self, state: TradingState):
        print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))

				# Orders to be placed on exchange matching engine
        result = {}
        product = 'AMETHYSTS'
        order_depth: OrderDepth = state.order_depths[product]
        orders: List[Order] = []
        position = state.position[product] if product in state.position else 0

        # acceptable_price = 10000
        # print("Acceptable price : " + str(acceptable_price))
        print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(len(order_depth.sell_orders)))
        print("Position: " + str(position))
        if position > -15 and position < 15:
            print("Position: " + str(position))
            orders.append(Order(product, 10002, -20 - position ))
            orders.append(Order(product, 9998, 20 - position))
        elif position >=15:
            print("Position: " + str(position))
            orders.append(Order(product, 10000, -5))
            orders.append(Order(product, 10002, -15-position))
            orders.append(Order(product, 9998, 20 - position))
        elif position <= -15:
            print("Position: " + str(position))
            orders.append(Order(product, 10000, 5))
            orders.append(Order(product, 9998, 15-position))
            orders.append(Order(product, 10002, -20 - position))
        print("Orders: " + str(orders))
            

    
        # product = 'STARFRUIT'
        # order_depth: OrderDepth = state.order_depths[product]
        # position = state.position[product] if product in state.position else 0
        # traderData = state.traderData
        # newBid = max(order_depth.buy_orders.keys())
        # newAsk = min(order_depth.sell_orders.keys())

        # if traderData == "":
        #     result[product] = orders
        #     traderData = str(newBid)+","+ str(newAsk)
        # else:
        #     #Check bid or ask has moved by a lot
        #     oldBidAsk = traderData.split(",")
        #     oldBid, oldAsk = int(oldBidAsk[0]), int(oldBidAsk[1])
        #     if newBid > oldBid + 4 & position > -17:
        #         orders.append(Order(product, newBid, -2))
        #     if newAsk < oldAsk - 4 & position < 17:
        #         orders.append(Order(product, newAsk, 2))
        #     traderData = str(newBid)+","+ str(newAsk)


        result[product] = orders
		    # String value holding Trader state data required. 
				# It will be delivered as TradingState.traderData on next execution.
        traderData = "Sample"
				# Sample conversion request. Check more details below. 
        conversions = 1
        return result, conversions, traderData