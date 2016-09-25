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


ff = pd.read_csv("../Data/FF.csv",index_col =0,parse_dates=True)
lsc = pd.read_csv('../Data/small_value_ret.csv',index_col =0,parse_dates=True)
ff = ff.drop(ff.index[:6])
lsc = lsc[:-1]

ff = ff.reset_index()
lsc = lsc.reset_index()

df = pd.concat([ff, lsc], 'i')
df = df.rename(columns={'Mkt-RF': 'Mkt'})

f = ' ret ~ Mkt + SMB + HML'
lm = sm.ols(formula=f, data=df).fit(cov_type='HAC', cov_kwds={'maxlags': 0})
print lm.params

