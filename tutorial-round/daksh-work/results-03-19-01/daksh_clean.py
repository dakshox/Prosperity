from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

STARFRUIT = "STARFRUIT"
AMETHYSTS = "AMETHYSTS"
LIMITS = {
    "AMETHYSTS": 20,
    "STARFRUIT": 20,
}



class Trader:

    @staticmethod
    def get_position(state, product):
        return state.position[product] if product in state.position else 0
    
    @staticmethod
    def sanitise_orders(orders):
        return [{"price": price, "qty": qty} for price, qty in orders.items()]
    


    @staticmethod
    def AmethystTrades(state):
        product = AMETHYSTS
        orders: List[Order] = []
        position = Trader.get_position(state, product)

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
        return orders


    @staticmethod
    def StarfruitTrades(state):
        product = STARFRUIT
        order_depth: OrderDepth = state.order_depths[product]
        position = Trader.get_position(state, product)
        traderData = state.traderData
        orders: List[Order] = []

        newBid = max(order_depth.buy_orders.keys())
        newAsk = min(order_depth.sell_orders.keys())
        bidSize = order_depth.buy_orders[newBid]
        askSize = order_depth.sell_orders[newAsk]
            
        if traderData != "":
            #Check bid or ask has moved by a lot
            oldBidAsk = traderData.split(",")
            oldBid, oldAsk = int(oldBidAsk[0]), int(oldBidAsk[1])
            if newBid > oldBid + 4:
                orders.append(Order(product, newBid, max(-bidSize, -20-position)))
            if newAsk < oldAsk - 4:
                orders.append(Order(product, newAsk, min(askSize, 20 - position)))

        traderData = str(newBid)+","+ str(newAsk)
        return orders, traderData


    def run(self, state: TradingState):
        
        
        print("traderData: " + state.traderData)

        result = {}

        amethyst_orders = Trader.AmethystTrades(state)        
        result[AMETHYSTS] = amethyst_orders
        

        starfruit_orders, traderData = Trader.StarfruitTrades(state)
        result[STARFRUIT] = starfruit_orders

    
		    # String value holding Trader state data required. 
            # It will be delivered as TradingState.traderData on next execution.
            # Sample conversion request. Check more details below. 
        
        conversions = 1

        return result, conversions, traderData
    