from datamodel import *
from tools.log_parser import *

def annotate_log(log: Log):
    """
    Annotates the dataframes with useful information from probe output of solutions.
    log should be parsed with parse_log(..., parse_trader_log_as_object=True).
    """

    trader_logs: dict[int, TradingState] = {l.timestamp: l.trader_log for l in log.sandbox_logs}
    def get_position(timestamp, product):
        if timestamp not in trader_logs:
            return None
        position_obj = trader_logs[timestamp].position
        return position_obj[product] if product in position_obj else 0

    # Add position information to activity_df
    log.activity_df["position"] = log.activity_df.apply(lambda row: get_position(row["timestamp"], row["product"]), axis=1)

    # Annotate trades_df
    # match trades against order book
    log.trades_df.sort_values("timestamp", inplace=True)
    log.trades_df.assign(submission_involved=False, market_order_filled=None)
    for timestamp in trader_logs:
        for symbol in log.trades_df["symbol"].unique():
            all_trades = log.trades_df[(log.trades_df.timestamp == timestamp) & (log.trades_df.symbol == symbol)]
            buys = [] # (price, quantity, index)
            sells = []

            @dataclass
            class Trade:
                price: int
                qty: int
                idx: int

            for row in all_trades.itertuples():
                if row.buyer == "SUBMISSION":
                    buys.append(Trade(row.price, row.quantity, row.Index))
                    log.trades_df.at[row.Index, "submission_involved"] = True
                    log.trades_df.at[row.Index, "market_order_filled"] = 0
                elif row.seller == "SUBMISSION":
                    sells.append(Trade(row.price, row.quantity, row.Index))
                    log.trades_df.at[row.Index, "submission_involved"] = True
                    log.trades_df.at[row.Index, "market_order_filled"] = 0
            buys.sort(key=lambda x: x.price)
            sells.sort(key=lambda x: x.price, reverse=True)

            book = trader_logs[timestamp].order_depths[symbol]
            # match our buys against sell orders
            buy_idx = 0
            for price, qty in book.sell_orders.items():
                price = int(price)
                qty = int(qty)
                while buy_idx < len(buys) and qty > 0:
                    if buys[buy_idx].price < price:
                        buy_idx += 1
                        continue
                    trade_qty = min(qty, buys[buy_idx].qty)
                    qty -= trade_qty
                    buys[buy_idx].qty -= trade_qty
                    log.trades_df.at[buys[buy_idx].idx, "market_order_filled"] += trade_qty
                    if buys[buy_idx].qty == 0:
                        buy_idx += 1

            # match our sells against buy orders
            sell_idx = 0
            for price, qty in book.buy_orders.items():
                price = int(price)
                qty = int(qty)
                while sell_idx < len(sells) and qty > 0:
                    if sells[sell_idx].price > price:
                        sell_idx += 1
                        continue
                    trade_qty = min(qty, sells[sell_idx].qty)
                    qty -= trade_qty
                    sells[sell_idx].qty -= trade_qty
                    log.trades_df.at[sells[sell_idx].idx, "market_order_filled"] += trade_qty
                    if sells[sell_idx].qty == 0:
                        sell_idx += 1



if __name__ == "__main__":
    log = parse_log("03_19_combined_trader.log", True)
    annotate_log(log)
    # print(log.sandbox_logs[5].trader_log.own_trades)
    # print(log.activity_df.tail())

    print(log.trades_df.head(10))
    print(log.activity_df.head(10))

    # print()
    # activity = log.activity_df.rename({"product": "symbol"}, inplace=False, axis=1).set_index(["timestamp", "symbol"], inplace=False)
    # print(activity)
    # print(log.trades_df.set_index(["timestamp", "symbol"]))
    # final = (activity.merge(log.trades_df.set_index(["timestamp", "symbol"]), how="right", left_index=True, right_index=True).reset_index())
    # print(final[final.symbol == "STARFRUIT"].head(20))

    # # resolve trades
    # old_position = 0
    # for row in log.activity_df[log.activity_df["product"] == "STARFRUIT"].itertuples():
    #     trades = log.trades_df[(log.trades_df.symbol == "STARFRUIT") & (log.trades_df.timestamp == row.timestamp - 100)]
    #     delta = trades[trades.buyer == "SUBMISSION"].quantity.sum() - trades[trades.seller == "SUBMISSION"].quantity.sum()
    #     expected_position = old_position + delta
    #     actual_position = row.position
    #     if expected_position != actual_position:
    #         print(f"Time: {row.timestamp}, Expected: {expected_position}, Actual: {actual_position}")
    #     old_position = actual_position
