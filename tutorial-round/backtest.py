
import tools.log_parser as log_parser
import tools.backtester as backtester
import sys
sys.path.append("./tutorial-round/daksh-work/results-03-11-04/")
import trader4 as solution
from functools import partial

if __name__ == "__main__":
    log = log_parser.parse_log("./tutorial-round/prober_logs/prober.log", parse_trader_log_as_object=True)
    trader = solution.Trader()
    print(backtester.backtest(trader.run, log, iters=100))
