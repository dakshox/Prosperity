from dataclasses import dataclass
from typing import *
import pandas as pd
import re
import jsonpickle
import json
import io
import datamodel

@dataclass
class SandboxLogEntry:
    timestamp: int
    sandbox_log: str
    trader_log: Any

@dataclass
class Log:
    sandbox_logs: list[SandboxLogEntry]
    activity_df: pd.DataFrame
    trades_df: pd.DataFrame

def parse_log(path: str, parse_trader_log_as_object: bool = False) -> Log:
    """
    Parses a log file.

    Args:
        path: The path to the log file.
        parse_trader_log_as_object: Whether to parse the trader log as an object (good for anything that
            prints json serialised data) or leave it as a string.
    """
    with open(path, 'r') as f:
        s = f.read()
    sections = re.split("\n\n+", s)
    assert len(sections) == 3

    decoder = jsonpickle.decode if parse_trader_log_as_object else lambda x: x

    def parse_sandbox(sect: str):
        t = sect.split('\n', 1)
        assert t[0].lower().strip() == "sandbox logs:"
        lines = t[1].splitlines()
        entries = []
        for i in range(0, len(lines), 5):
            entry = "\n".join(lines[i:i+5])
            obj = json.loads(entry)
            try:
                log_object = decoder(obj["lambdaLog"], classes=datamodel.TradingState)
            except json.decoder.JSONDecodeError:
                print(f"[WARN] lambdaLog is missing for timestamp {obj['timestamp']}.")
                log_object = None
            entries.append(SandboxLogEntry(obj["timestamp"], obj["sandboxLog"], log_object))
        return entries
    
    def parse_activity(sect: str):
        t = sect.split('\n', 1)
        assert t[0].lower().strip() == "activities log:"
        return pd.read_csv(io.StringIO(t[1]), sep=';')

    def parse_trades(sect: str):
        t = sect.split('\n', 1)
        assert t[0].lower().strip() == "trade history:"
        obj = json.loads(t[1])
        return pd.DataFrame(obj)
    
    return Log(parse_sandbox(sections[0]), parse_activity(sections[1]), parse_trades(sections[2]))
    

if __name__ == "__main__":
    # Example usage
    log = parse_log("../data/prober_log.log", parse_trader_log_as_object=True)
    print(log.sandbox_logs[3].trader_log.order_depths["AMETHYSTS"].buy_orders)
    print(log.sandbox_logs[3].trader_log.listings)
    print(log.activity_df)
    print(log.trades_df)
