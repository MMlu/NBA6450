import warnings
warnings.simplefilter(action = "ignore", category = RuntimeWarning)

import pandas as parray
import numpy as math
from pandas.stats.api import ols
from pandas.io.data import DataReader
from datetime import datetime
from datetime import date


def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  'yahoo', fromdate, todate)
    return timeSeries

series_spx = get_data('^GSPC',datetime(2016,1,1),date.today())
series_vix = get_data('^VIX',datetime(2016,1,1),date.today())
returns_spx = math.log(series_spx['Adj Close'].shift(1)/series_spx['Adj Close'])
returns_vix = math.log(series_vix['Adj Close'].shift(1)/series_vix['Adj Close'])
returns = parray.concat([returns_spx, returns_vix], axis=1)
returns.columns = ['lr_spx','lr_vix']

#returns.plot(kind = 'scatter',x = 'lr_vix',y='lr_spx')

#print("correlation: \n",returns.corr())

#print("spx returns stdev = ", returns['lr_spx'].std()*100)
#print("spx returns stdev = ", returns['lr_spx'].std()*100)

#regress = ols(y = returns['lr_spx'], x = returns['lr_vix'])
#print (regress)

#print("spx returns skew = ", returns['lr_spx'].skew())
#print("spx returns skew = ", returns['lr_spx'].skew())