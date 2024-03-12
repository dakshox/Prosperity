import tools.log_parser as log_parser

if __name__ == "__main__":
    log_path = "tutorial-round/thien-work/trader4_log.log"
    log = log_parser.parse_log(log_path, parse_trader_log_as_object=True)

    for entry in log.sandbox_logs[:100]:
        trader_log = entry.trader_log
        trades = trader_log.own_trades["AMETHYSTS"] if "AMETHYSTS" in trader_log.own_trades else []
        if len(trades) > 0 and trades[0].timestamp == entry.timestamp - 100:
            print(entry.timestamp, trades)
