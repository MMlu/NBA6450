import pandas as pd
import numpy as np
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date
import statsmodels.formula.api as sm


def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  "fred", fromdate, todate)
    return timeSeries

def movingAverage(interval, window_size):
    window = np.ones(int(window_size))/float(window_size)
    return np.convolve(interval, window, 'same')


ff = pd.read_csv("../Data/FF.csv",index_col =0,parse_dates=True)
lsc = pd.read_csv('../Data/small_value_ret.csv',index_col =0,parse_dates=True)
ff = ff.drop(ff.index[:6])
lsc = lsc[:-1]

ff = ff.reset_index()
lsc = lsc.reset_index()

df = pd.concat([ff, lsc], 'i')
df = df.rename(columns={'Mkt-RF': 'MktRF'})
yearAvg = df.groupby(['year']).sum()

df['retRF'] = df['ret'] - df['RF']

print df

# A
f = ' ret ~ MktRF'
lm = sm.ols(formula=f, data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 0})
print lm.params

expectedReturn = lm.params[1] * yearAvg['MktRF'].mean()
print expectedReturn, '\n'

# B
f = ' ret ~ MktRF + SMB + HML'
lm = sm.ols(formula=f, data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 0})
print lm.params

expectedReturn = lm.params[1] * yearAvg['MktRF'].mean() \
                    + lm.params[2] * yearAvg['SMB'].mean() \
                    + lm.params[3] * yearAvg['HML'].mean()

print expectedReturn

# C
print movingAverage(df['MktRF'], 12)
