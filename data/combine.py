import pandas as pd
import tools.log_parser as log_parser

RAW_PATH = "raw/"
OUTPUT_PATH = "data_v1/"
ROUND_1_DAYS = [-2, -1, 0]
ROUND_2_DAYS = [-1, 0, 1]
GIVEN_ROUND_1_PRICES = [RAW_PATH + f"prices_round_1_day_{i}.csv" for i in ROUND_1_DAYS]
GIVEN_ROUND_1_TRADES = [RAW_PATH + f"trades_round_1_day_{i}_nn.csv" for i in ROUND_1_DAYS]
GIVEN_ROUND_2 = [RAW_PATH + f"prices_round_2_day_{i}.csv" for i in ROUND_2_DAYS]
ROUND_1_LOG = RAW_PATH + "round_1_final.log"
TIME_PER_DAY = 10 ** 6

def make_total_timestamp(df, timestamp_col, day_col):
    df["total_timestamp"] = df[timestamp_col] + (df[day_col] + 2) * TIME_PER_DAY
    # make total_timestamp first
    cols = list(df.columns)
    if "total_timestamp" in cols:
        cols.remove("total_timestamp")
    df = df[["total_timestamp"] + cols]
    return df

def combine():
    # deal with round 1 log
    r1_log_data = log_parser.parse_log(ROUND_1_LOG, parse_trader_log_as_object=False)
    
    # get round 1 prices and trades
    r1_price_dfs = [pd.read_csv(f, sep=";") for f in GIVEN_ROUND_1_PRICES]
    r1_trade_dfs = [pd.read_csv(f, sep=";").assign(day=i) for i, f in zip(ROUND_1_DAYS, GIVEN_ROUND_1_TRADES)]
    r1_price_dfs.append(r1_log_data.activity_df)
    r1_trade_dfs.append(r1_log_data.trades_df.assign(day=2))

    r1_prices = pd.concat(r1_price_dfs)
    r1_trades = pd.concat(r1_trade_dfs)
    r1_prices = make_total_timestamp(r1_prices, "timestamp", "day")
    r1_trades = make_total_timestamp(r1_trades, "timestamp", "day")

    # deal with round 2
    r2_price_dfs = [pd.read_csv(f, sep=";") for f in GIVEN_ROUND_2]
    r2_prices = pd.concat(r2_price_dfs)
    r2_prices = make_total_timestamp(r2_prices, "timestamp", "DAY")

    # output
    r1_prices.to_csv(OUTPUT_PATH + "prices_1.csv", sep=";", index=False)
    r1_trades.to_csv(OUTPUT_PATH + "trades_1.csv", sep=";", index=False)
    r2_prices.to_csv(OUTPUT_PATH + "prices_2.csv", sep=";", index=False)


if __name__ == "__main__":
    combine()
