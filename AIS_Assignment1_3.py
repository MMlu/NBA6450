import pandas as pd
import numpy as math
import matplotlib.pyplot as ploty
import statsmodels.tsa.api as stats
import warnings

warnings.simplefilter(action = "ignore", category = RuntimeWarning)

def rollingsum_windowed(arr,ws):
    x = [sum(arr[i-(ws-1):i+1]) if i>(ws-1) else sum(arr[:i+1])  for i in range(len(arr))]
    return x

location = "/Users/jones/Documents/Data/FF.csv"
ff = pd.read_csv(location,index_col =0,parse_dates=True)
exret = list(ff['Mkt-RF'].values)
exret.remove('Mkt-RF')
lr = [math.log(1+float(i)/100) for i in exret]

mr6 = rollingsum_windowed(lr,6)
mr12 = rollingsum_windowed(lr,12)
mr36 = rollingsum_windowed(lr,36)
mr60 = rollingsum_windowed(lr,60)

