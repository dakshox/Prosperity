import sys
sys.path.append("..")
import combined_trader as trader

import tools.backtester as backtester
import tools.log_parser as log_parser
import pandas as pd
from functools import partial

LOG_PATH = "prober.log"
ACTIVITY_LOG_PATH = "../data/prices_round_1_day_0.csv"

def bench_backtest():
    trader_func = partial(trader.Trader().run, verbose=False)
    log = log_parser.parse_log(LOG_PATH, parse_trader_log_as_object=True)
    results = backtester.backtest(trader_func, log)
    print(results)

    results2 = backtester.backtest_from_log(trader_func, log.activity_df)
    print(results2)

def bench_backtest_from_log():
    trader_func = partial(trader.Trader().run, verbose=False)
    log = pd.read_csv(ACTIVITY_LOG_PATH, sep=";")
    results = backtester.backtest_from_log(trader_func, log, iters=1000)
    print(results)

if __name__ == "__main__":
    bench_backtest()
    bench_backtest_from_log()

# BacktestResults(balance=-239197, position={'STARFRUIT': 8, 'AMETHYSTS': 20}, profit=1227.0)
