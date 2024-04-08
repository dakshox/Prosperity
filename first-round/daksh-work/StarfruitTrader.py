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

        if -15 < position < 15:
            orders.append(Order(product, 10002, -20 - position))
            orders.append(Order(product, 9998, 20 - position))
        elif position >= 15:
            orders.append(Order(product, 10000, -5))
            orders.append(Order(product, 10002, -15 - position))
            if position != 20:
                orders.append(Order(product, 9998, 20 - position))
        elif position <= -15:
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

            ewma3 = (0.3 * newMid + 0.7 * float(traderData)) if traderData else newMid
            traderData = str(ewma3)
            print('Position:', position)
            #First trade on orders that exist

            THIS DOESNT WORK YET

            
            for price, volume in order_depth.sell_orders.items():
                if price < ewma3 - 1 and position + volume > -LIMITS[product]:
                    print("BUY",price, ewma3, position, -volume)
                    orders.append(Order(product, price, -volume))
                    position += -volume
            for price, volume in order_depth.buy_orders.items():
                if price > ewma3 + 1 and position + volume < LIMITS[product]:
                    print("SELL",price, ewma3, position, -volume)
                    orders.append(Order(product, price, -volume))
                    position += -volume
                
            

            #Second, market make around ewma
            if position > -LIMITS[product]:
                print(-20 - position)
                orders.append(Order(product, round(ewma3) + 2, - 20 - position))
            if position < LIMITS[product]:
                print(20 - position)
                orders.append(Order(product, round(ewma3) - 2, 20 - position))

        return orders, traderData

    def run(self, state: TradingState):
        """Main trading logic execution point."""
        result = {}

        # Generate orders for AMETHYSTS and STARFRUIT
        # amethyst_orders = Trader.AmethystTrades(state)        
        # result[AMETHYSTS] = amethyst_orders

        starfruit_orders, traderData = Trader.StarfruitTrades(state)
        result[STARFRUIT] = starfruit_orders

        # Placeholder for conversions and trader data management
        conversions = 1

        return result, conversions, traderData