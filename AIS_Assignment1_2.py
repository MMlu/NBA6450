import pandas as pd
import numpy as math
import matplotlib.pyplot as ploty
import statsmodels.tsa.api as stats
import warnings

warnings.simplefilter(action = "ignore", category = RuntimeWarning)

def rollingsum_windowed(arr,ws):
    x = [sum(arr[i-(ws-1):i+1]) if i>(ws-1) else sum(arr[:i+1])  for i in range(len(arr))]
    return x

location = "/Users/jones/Documents/Data/vwret.csv"
vwret = pd.read_csv(location,index_col =0,parse_dates=True)

prices =[1]
dividends = [0]

i = 1
while i < len(vwret.vwretx):
    prices.append(prices[i-1] * (1+vwret.vwretx[i-1]))
    dividends.append(prices[i-1] * (vwret.vwretd[i-1]-vwret.vwretx[i-1]))
    i+=1

payout = rollingsum_windowed(dividends,12)
p2d = [math.log(x/y) for x, y in zip(prices[1:], payout[1:])]
p2d = p2d[12:]
dates =list(vwret.index.values)
ploty.plot(dates[12:-1],p2d)
ploty.show()

location2 = "/Users/jones/Documents/Data/CAPE.csv"
cape = pd.read_csv(location2,index_col =0)
cape = list(cape.CAPE.values)
cape = list(math.log(cape[-779:]))
print ("Correlation P/d - CAPE :\n",math.corrcoef(p2d,cape))

model = stats.AR(p2d)
print("Dickey fuller p-value:", stats.adfuller(p2d,1)[1])
results = model.fit(1)
print( results.params)
print ("p2d half life = ",math.log(0.5)/math.log(results.params[1]))

model = stats.AR(cape)
print("Dickey fuller p-value:", stats.adfuller(cape,1)[1])
results = model.fit(1)
print( results.params)
print ("CAPE half life = ",math.log(0.5)/math.log(results.params[1]))