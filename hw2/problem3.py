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

def monthlyAToAnnualA(monthlyA):
    return ((1+monthlyA)**12) - 1

ff = pd.read_csv("../Data/FF.csv",index_col =0,parse_dates=True)
lsc = pd.read_csv('../Data/small_value_ret.csv',index_col =0,parse_dates=True)
ff = ff.drop(ff.index[:6])
lsc = lsc[:-1]

ff = ff.reset_index()
lsc = lsc.reset_index()

df = pd.concat([ff, lsc], 'i')
df = df.rename(columns={'Mkt-RF': 'MktRF'})

df['ret'] = df['ret'] * 100
df['ret_rf'] = df['ret'] - df['RF']
yearAvg = df.groupby(['year']).sum()

# A
f = ' ret_rf ~ MktRF'
lm = sm.ols(formula=f, data=df).fit()
print lm.summary()

expectedReturn = lm.params[1] * yearAvg['MktRF'].mean()
print expectedReturn
print

# B
f = ' ret_rf ~ MktRF + SMB + HML'
lm = sm.ols(formula=f, data=df).fit()
print lm.summary()

expectedReturn = lm.params[1] * df['MktRF'].mean() \
                    + lm.params[2] * df['SMB'].mean() \
                    + lm.params[3] * df['HML'].mean()
print expectedReturn
print

# C
df['MktRFMA'] = movingAverage(df['MktRF'], 12)
df['SMBMA'] = movingAverage(df['SMB'], 12)
df['HMLMA'] = movingAverage(df['HML'], 12)
yearAvg = df.groupby(['year']).sum()



ddf = df
df = df.ix[11:]

f = ' ret_rf ~ MktRFMA + SMBMA + HMLMA'
lm = sm.ols(formula=f, data=df).fit()
print lm.summary()

expectedReturn = lm.params[1] * df['MktRFMA'].mean() \
                    + lm.params[2] * df['SMBMA'].mean() \
                    + lm.params[3] * df['HMLMA'].mean()
print expectedReturn
print np.average(df['RF'])