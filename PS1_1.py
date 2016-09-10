import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)

import pandas as parray
import numpy as math
from pandas.stats.api import ols
from pandas.io.data import DataReader
import statsmodels.formula.api as sm
import matplotlib.pyplot as plt



from datetime import datetime
from datetime import date


def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  'yahoo', fromdate, todate)
    return timeSeries

series_spx = get_data('^GSPC',datetime(1990,01,02),datetime(2015,12,31))
series_vix = get_data('^VIX',datetime(1990,01,02),datetime(2015,12,31))
returns_spx = math.log(series_spx['Adj Close'].shift(1)/series_spx['Adj Close'])
returns_vix = math.log(series_vix['Adj Close'].shift(1)/series_vix['Adj Close'])
returns = parray.concat([returns_spx, returns_vix], axis=1)
returns.columns = ['lr_spx','lr_vix']
print returns

returns.plot(kind = 'scatter',x = 'lr_vix',y='lr_spx')

print("correlation: \n",returns.corr())

print("vix returns stdev = ", returns['lr_vix'].std()*100)
print("spx returns stdev = ", returns['lr_spx'].std()*100)

regress = sm.ols(formula="lr_spx ~ lr_vix", data=returns).fit()

print (regress.summary())

print("spx returns skew = ", returns['lr_spx'].skew())
print("vix returns skew = ", returns['lr_vix'].skew())
plt.show()

