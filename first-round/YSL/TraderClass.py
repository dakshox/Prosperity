from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List, Dict, Tuple
import string

class Trader:
    
    def calculate_acceptable_price(self, sell_orders: Dict[str, int], buy_orders: Dict[str, int]) -> Tuple[float, float]:
        best_ask = min(map(int, sell_orders.keys())) if sell_orders else float('inf')
        best_bid = max(map(int, buy_orders.keys())) if buy_orders else 0
        mid_price = (best_ask + best_bid) / 2 if best_ask != float('inf') and best_bid != 0 else None
        return mid_price - 0.01, mid_price + 0.01  # Adjust by a cent for buy and sell prices

    def run(self, state: TradingState):
        result: Dict[str, List[Order]] = {}
        for product, order_depth in state.order_depths.items():
            acceptable_buy_price, acceptable_sell_price = self.calculate_acceptable_price(order_depth.sell_orders, order_depth.buy_orders)

            orders: List[Order] = []
            for price, amount in order_depth.sell_orders.items():
                if int(price) < acceptable_sell_price:
                    orders.append(Order(product, price, -amount))  # Buy order

            for price, amount in order_depth.buy_orders.items():
                if int(price) > acceptable_buy_price:
                    orders.append(Order(product, price, -amount))  # Sell order

            result[product] = orders

        traderData = "SAMPLE"  
        
        conversions = 1
        return result, conversions, traderData
