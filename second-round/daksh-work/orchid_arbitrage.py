from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import jsonpickle

class Trader:
    
    def run(self, state: TradingState):
        """ Check if arbitrage opportunity available, if so sell now and import next tick """

        product = 'ORCHIDS'
        order_depth: OrderDepth = state.order_depths.get(product, OrderDepth())
        position = state.position[product] if product in state.position else 0
        if state.traderData == "":
            traderData = "0"
        else:
            traderData = state.traderData
        
        # print()
        # south_bid = state.observations.orderDepths['ORCHIDS'].bidPrice

        south_ask = state.observations.conversionObservations[product].askPrice
        import_tarrif = state.observations.conversionObservations[product].importTariff
        transport_fees = state.observations.conversionObservations[product].transportFees

        # island_asks = state.order_depths['ORCHIDS'].askPrice
        island_bid = int(max(order_depth.buy_orders.keys()))
        island_vol = order_depth.buy_orders[island_bid]


        # print(state.observations.conversionObservations['ORCHIDS'].bidPrice)
        result = {}
        
        # if (state.timestamp // 100) % 2 == 0:
            # result['ORCHIDS'] = [Order('ORCHIDS', 0, -20)]
            # conversions = 0
        # else:
            # conversions = -position

        if island_bid > south_ask + import_tarrif + transport_fees + 1 and position == 0:
            result['ORCHIDS'] = [Order('ORCHIDS', island_bid, -island_vol)]	
            conversions = 0    

            total_trades = int(traderData)
            total_trades += island_vol
            traderData = str(total_trades)
        
        elif position != 0:
            conversions = -position
        
        else:
            conversions = 0
        print(traderData)

        return result, conversions, traderData
