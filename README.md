# IMC Prosperity 2024

Team Name: `K2BLE`

## Setup Instructions

Python projects should use a virtual environment to control which versions of packages are used. After cloning this repository, perform the following commands while inside the directory.

1. Create a virtual environment with `python -m venv ".venv"`.
1. Activate it with `./.venv/Scripts/activate` on Windows, or `source ./.venv/bin/activate` on Mac (not tested yet).
1. Install the required packages with `pip install -r requirements.txt`.

Whenever you install a new package and use it in the project, add it to the requirements list with `pip freeze > requirements.txt`. This overwrites the old file, so make sure the new package is really necessary!

## Protocol

From experiments, this is approximately what happens at each timestep:

1. you get a list of bids/offers
2. you get to submit any number of bids/offers
3. your trades get matched to the bots' bids/offers, resolving to the *bot price*
4. your remaining trades may be executed by the bots, resolving to *your price*

## Using the Backtester

The backtester will simulate your trades on the order book in each iteration, so all trades of step 3 above will be processed. No trades from step 4 will be processed as we don't know what the bots will do (thus the backtester will execute less trades overall).

Example code in `tutorial-round/backtest.py`.

- Run `prober.py` (or some other solution that prints `jsonpickle.encode(state)` and nothing else) on the actual evaluation platform.
- Download the log.
- Parse the log file: `log = log_parser.parse_log("/path/to/log/file", parse_trader_log_as_object=True)`
- Run `backtester.backtest(trader.run, log)`, where `trader.run` is the run *function* of the trader you want to backtest.

Note that you don't need to make a trader to run the backtester: just make the function if you're testing things out.

## Changelog

### Initial Commit (`Daksh 2024-03-11`)

This is what I did so far...

Data1 includes all the stuff from the log, thinking maybe we keep each thing in a seperate folder? idk how to best organise data

I wrote the script that changes log into 2 logs and a csv (readLog.py)

In each data folder there is the trader bot that gave that data:

Trader1 is just standard, doesnt ac work because 'appropriate price' was set to like 10 or smt

Trader2 I set 'appropriate price' to 10000, this now only trades Amethyst because thats the one with a stable price
Trader2 only 'market takes' when price moves

Trader3 and Trader4 are constantly market making around 10000,
trader3 is 9999 bid 10001 ask
trader4 is 9998 bid 10002 ask

both have same PnL, shown in activityAnalysis.ipynb