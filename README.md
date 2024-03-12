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
