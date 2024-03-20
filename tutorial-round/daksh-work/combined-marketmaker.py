from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import string

x = 0

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
    def AmethystTrades(state):
        product = AMETHYSTS
        orders: List[Order] = []
        position = Trader.get_position(state, product)

        if position > -15 and position < 15:
            # print("Position: " + str(position))
            orders.append(Order(product, 10002, -20 - position ))
            orders.append(Order(product, 9998, 20 - position))
        elif position >=15:
            # print("Position: " + str(position))
            orders.append(Order(product, 10000, -5))
            orders.append(Order(product, 10002, -15-position))
            if position != 20:
                orders.append(Order(product, 9998, 20 - position))
        elif position <= -15:
            # print("Position: " + str(position))
            orders.append(Order(product, 10000, 5))
            orders.append(Order(product, 9998, 15-position))
            if position != -20:
                orders.append(Order(product, 10002, -20 - position))
        return orders


    @staticmethod
    def StarfruitTrades(state):
        product = STARFRUIT
        order_depth: OrderDepth = state.order_depths[product]
        position = Trader.get_position(state, product)
        traderData = state.traderData
        orders: List[Order] = []

        newBid = int(max(order_depth.buy_orders.keys()))
        newAsk = int(min(order_depth.sell_orders.keys()))
        newMid = (newBid + newAsk) // 2

        if traderData == "":
            ewma = newMid
            traderData = str(ewma)

        else:
            ewma = float(traderData)
            ewma = 0.1 * newMid + 0.9 * ewma
            traderData = str(ewma)
            if position > -20:
                orders.append(Order(product, round(ewma) + 2, -20-position))
            if position < 20:
                orders.append(Order(product, round(ewma) - 2, 20 - position))


        return orders, traderData

    def run(self, state: TradingState):
        


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
    
if __name__ == "__main__":
    import tools.backtester as backtester
    import tools.log_parser as log_parser
    log = log_parser.parse_log("tutorial-round\daksh-work\prober.log", parse_trader_log_as_object=True)
    for x in range(1, 11):
        print(x)
        print(backtester.backtest(Trader().run, log))
    