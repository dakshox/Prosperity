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
        """Get the current position for a product."""
        return state.position.get(product, 0)

    @staticmethod
    def AmethystTrades(state):
        """Generate trades for AMETHYSTS based on the current position."""
        product = AMETHYSTS
        orders: List[Order] = []
        position = Trader.get_position(state, product)
        print('Position:', position)
        print(state.own_trades)
        stopHittingLimit = 15

        if -stopHittingLimit < position < stopHittingLimit:
            orders.append(Order(product, 10002, -20 - position))
            orders.append(Order(product, 9998, 20 - position))
        elif position >= stopHittingLimit:
            orders.append(Order(product, 10000, -5))
            orders.append(Order(product, 10002, -15 - position))
            if position != 20:
                orders.append(Order(product, 9998, 20 - position))
        elif position <= -stopHittingLimit:
            orders.append(Order(product, 10000, 5))
            orders.append(Order(product, 9998, 15 - position))
            if position != -20:
                orders.append(Order(product, 10002, -20 - position))
        return orders

    @staticmethod
    def StarfruitTrades(state):
        """Generate trades for STARFRUIT using an EWMA strategy."""
        product = STARFRUIT
        order_depth: OrderDepth = state.order_depths.get(product, OrderDepth())
        position = Trader.get_position(state, product)
        traderData = state.traderData
        orders: List[Order] = []

        if order_depth.buy_orders and order_depth.sell_orders:
            newBid = int(max(order_depth.buy_orders.keys()))
            newAsk = int(min(order_depth.sell_orders.keys()))
            newMid = (newBid + newAsk) // 2
            maxBuy = LIMITS[product] - position
            maxSell = LIMITS[product] + position

            ewma3 = (0.3 * newMid + 0.7 * float(traderData)) if traderData else newMid
            traderData = str(ewma3)
            # print('Position:', position)

            #First trade on orders that exist
            for price, volume in order_depth.sell_orders.items():
                if price < ewma3 - 1 and maxBuy > 0:
                    # print("BUY",price, ewma3, position, min(-volume, maxBuy))
                    orders.append(Order(product, price, min(-volume, maxBuy)))
                    maxBuy -= min(-volume, maxBuy)
            for price, volume in order_depth.buy_orders.items():
                if price > ewma3 + 1 and maxSell > 0:
                    # print("SELL",price, ewma3, position, -min(volume, maxSell))
                    orders.append(Order(product, price, -min(volume, maxSell)))
                    maxSell -= min(volume, maxSell)
                
            

            #Second, market make around ewma
            if maxSell > 0:
                # print('Market Making MaxSell:', maxSell)
                orders.append(Order(product, round(ewma3) + 2, -maxSell))
            if maxBuy > 0:
                # print('Market Making MaxBuy:', maxBuy)
                orders.append(Order(product, round(ewma3) - 2, maxBuy))

        return orders, traderData

    def run(self, state: TradingState):
        """Main trading logic execution point."""
        result = {}

        # Generate orders for AMETHYSTS and STARFRUIT
        amethyst_orders = Trader.AmethystTrades(state)        
        result[AMETHYSTS] = amethyst_orders

        starfruit_orders, traderData = Trader.StarfruitTrades(state)
        result[STARFRUIT] = starfruit_orders

        # traderData = ''
        # Placeholder for conversions and trader data management
        conversions = 1

        return result, conversions, traderData