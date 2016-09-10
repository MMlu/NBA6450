import pandas as pd
import numpy as np
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date

warnings.simplefilter(action = "ignore", category = RuntimeWarning)

def rollingsum_windowed(arr,ws):
    x = [sum(arr[i-(ws-1):i+1]) if i>(ws-1) else sum(arr[:i+1])  for i in range(len(arr))]
    return x

def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  "fred", fromdate, todate)
    return timeSeries

location = "/Users/jones/Documents/Data/FF.csv"
ff = pd.read_csv(location,index_col =0,parse_dates=True)
exret = list(ff['Mkt-RF'].values)
lr = [np.log(1+float(i)/100) for i in exret]

mr6 = rollingsum_windowed(lr,6)
mr12 = rollingsum_windowed(lr,12)
mr36 = rollingsum_windowed(lr,36)
mr60 = rollingsum_windowed(lr,60)

Aaay = get_data("AAA",datetime(1977,1,1),datetime(2013,12,31))
Baay = get_data("BAA",datetime(1977,1,1),datetime(2013,12,31))
Default_spread = Baay['BAA'] - Aaay['AAA']

#==============================================================================
# print("Average default spread: ", np.average(Default_spread))
# print("Stddev of default spread: ", np.std(Default_spread))
# model = stats.AR(Default_spread)
# results = model.fit(1)
# print ("default spread half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================

GS10 = get_data("GS10",datetime(1977,1,1),datetime(2013,12,31))
TB3MS = get_data("TB3MS",datetime(1977,1,1),datetime(2013,12,31))
term_spread = GS10['GS10']-TB3MS['TB3MS']

#==============================================================================
# print("Average term spread: ", np.average(term_spread))
# print("Stddev of term spread: ", np.std(term_spread))
# model = stats.AR(term_spread)
# results = model.fit(1)
# print ("term spread half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================

location = "/Users/jones/Documents/Data/icc.csv"
icc = pd.read_csv(location,index_col =0)

#==============================================================================
# print("Average icc: ", np.average(icc))
# print("Stddev of icc: ", np.std(icc))
# model = stats.AR(icc)
# results = model.fit(1)
# print ("icc half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================