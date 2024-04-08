# The goal is to calculate the best bid1 and bid2 for the manual trade
# If the fish likes our bid1, we buy at bid1 and sell at 1000, 
# if the fish doesn't like our bid1 but likes bid2 we buy at bid2 and sell at 1000
# The PDF is P(X=x) = x/5000
# The CDF is P(X <= x) = x^2/10000
# The EV of one bid is then the P(X <= x) * (100 - x)
# The EV of two bids can easily be calculated
# The best bid1 and bid2 can be calculated by iterating through all possible bids
# The best bid1 and bid2 are 52 and 78 respectively, giving a EV of 20.4152


ev = 0

for i in range(0, 101):
    for j in range(i + 1, 101):
        new_ev =  ( i**2 * (100 - i ) + (j**2 - i**2)*(100-j) ) / 10000
        if new_ev > ev:
            ev = new_ev
            print(i, j, ev)

