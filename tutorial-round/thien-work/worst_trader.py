from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        # print("traderData: " + state.traderData)
        # print("Observations: " + str(state.observations))

        print(jsonpickle.encode(state))

        result = {}
        for product in state.listings.keys():
            result[product] = []
            pos = state.position[product] if product in state.position else 0
            limit = 20
            if pos < limit:
                result[product].append(Order(product, 1000000, limit - pos))
            if -pos < limit:
                result[product].append(Order(product, 0, -(limit + pos)))
            # orders: List[Order] = [Order(product, 0, 1)]
            # result[product] = orders
    
        traderData = ""
        
        conversions = 0
        return result, conversions, traderData

if __name__ == "__main__":
    import tools.backtester as backtester
    import tools.log_parser as log_parser
    log = log_parser.parse_log("trader4_log.log", parse_trader_log_as_object=True)
    print(backtester.backtest(Trader().run, log))
