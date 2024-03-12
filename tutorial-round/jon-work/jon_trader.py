from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle


class Trader:
    """
    Jonathan's Trading Bot
    Date: 2024-03-12
    Version: 0

    Amethyst: Simply makes a two-wide market around 10,000.

    Starfruit (not implemented yet): Reads the order book and fills pending orders
    that are favourable, i.e. unusually high bids, or low asks.
    Does this by keeping track of a running mean and standard
    deviation of bids and asks in the last 10 time steps.
    """

    def run(self, state: TradingState):
        print(jsonpickle.encode(state))

        # Return trade requests as a map: product -> list of orders
        result = {}

        # Make trades on Amethysts
        product = "AMETHYSTS"
        position = state.position[product] if (product in state.position) else 0
        POSITION_LIMIT = 20
        orders = []

        # Make as many orders as possible without allowing
        # possibility of going over position limit.
        # Fill from the outside first.
        short_left = POSITION_LIMIT - abs(min(position, 0))
        for price, amount in zip([10004, 10002], [10, 10]):
            order_size = min(amount, short_left)
            orders.append(Order(product, price, -order_size))
            short_left -= order_size

        long_left = POSITION_LIMIT - max(position, 0)
        for price, amount in zip([9996, 9998], [10, 10]):
            order_size = min(amount, long_left)
            orders.append(Order(product, price, order_size))
            long_left -= order_size

        result[product] = orders

        # Make trades on Starfruit (not implemented)

        # String value holding Trader state data required
        # Delivered as state.traderData on next execution
        traderData = ""
        conversions = 0

        return result, conversions, traderData
