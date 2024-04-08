from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict

class BetterTrader:
    def __init__(self):
        self.trading_limits = {"AMETHYSTS": 20, "STARFRUIT": 20}
        self.price_history = {"AMETHYSTS": [], "STARFRUIT": []}
        self.average_price = {"AMETHYSTS": 0, "STARFRUIT": 0}
    
    def update_price_history_and_average(self, product, new_price):
        # Keep the last 10 prices to calculate a simple moving average
        self.price_history[product] = (self.price_history[product][-9:] + [new_price])
        self.average_price[product] = sum(self.price_history[product]) / len(self.price_history[product])
    
    def decide_order(self, product, bid_price, ask_price):
        orders = []
        # Determine the strategy based on the product's market behavior
        if product == "STARFRUIT":
            # Volatile market strategy
            if ask_price < self.average_price[product] * 0.95:  # Buying opportunity
                orders.append(Order(product, ask_price, self.trading_limits[product]))
            elif bid_price > self.average_price[product] * 1.05:  # Selling opportunity
                orders.append(Order(product, bid_price, -self.trading_limits[product]))
        else:
            # Stable market strategy
            if ask_price <= self.average_price[product]:  # Buying opportunity
                orders.append(Order(product, ask_price, self.trading_limits[product]))
            elif bid_price >= self.average_price[product]:  # Selling opportunity
                orders.append(Order(product, bid_price, -self.trading_limits[product]))
        return orders
    
    def run(self, state: TradingState):
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                best_ask = min(order_depth.sell_orders.keys())
                best_bid = max(order_depth.buy_orders.keys())
                self.update_price_history_and_average(product, (best_ask + best_bid) / 2)
                result[product] = self.decide_order(product, best_bid, best_ask)
        return result
