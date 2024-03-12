from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle


class Trader:
    """
    Jonathan's Trading Bot
    Date: 2024-03-12
    Version: 0

    Amethyst: Simply makes a two-wide market around 10,000, of maximum size
    such that the position limit is not violated.

    Starfruit (not implemented yet): Reads the order book and fills pending orders
    that are favourable, i.e. unusually high bids, or low asks.
    Does this by keeping track of a running mean and standard
    deviation of bids and asks in the last 10 time steps.
    """

    def run(self, state: TradingState):
        print(jsonpickle.encode(state))

        # Return trade requests as a map: product -> list of orders
        result = {}
        POSITION_LIMIT = 20

        # Make trades on Amethysts
        product = "AMETHYSTS"
        orders = []
        position = state.position[product] if (product in state.position) else 0

        # Find the maximum order size we can ask, and place it on 10002
        short_left = -POSITION_LIMIT - min(position, 0)
        orders.append(Order(product, 10002, short_left))

        # Find the maximum order size we can bid, and place it on 9998
        long_left = POSITION_LIMIT - max(position, 0)
        orders.append(Order(product, 9998, long_left))

        result[product] = orders

        # Debugging just for curiosity:
        # How often do we hit the position limit?
        if abs(position) == POSITION_LIMIT:
            print("We got blocked by the position limit!")

        # Make trades on Starfruit (not implemented)
        product = "STARFRUIT"
        orders = []
        position = state.position[product] if (product in state.position) else 0

        # Hack for now: since we know the price trends downwards
        # then just short as much as possible at the very beginning
        if position > -20:
            orders.append(Order(product, 4995, -20))

        # String value holding Trader state data required
        # Delivered as state.traderData on next execution
        traderData = ""
        conversions = 0

        return result, conversions, traderData
