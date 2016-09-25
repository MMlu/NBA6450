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

def get_params(df, names, lag, return_period):
    d = {}
    df1 = pd.DataFrame(d)
    df1['name'] = names
    df1['coef'] = [0.0, 0.0, 0.0]
    df1['tstat'] = [0.0, 0.0, 0.0]
    df1['rsquared'] = [0.0, 0.0, 0.0]
    j = 0
    for i in names:
        f = '' + return_period + ' ~ ' + i
        lm = sm.ols(formula=f, data=df).fit(cov_type='HAC',cov_kwds={'maxlags':lag})

        df1['coef'][j] = lm.params[1]
        df1['rsquared'][j] = lm.rsquared_adj
        df1['tstat'][j] = lm.tvalues[1]
        j += 1
    return df1


ff = pd.read_csv("../Data/FF.csv",index_col =0,parse_dates=True)
lsc = pd.read_csv('../Data/small_value_ret.csv',index_col =0,parse_dates=True)
ff = ff.drop(ff.index[:6])
lsc = lsc[:-1]

ff = ff.reset_index()
lsc = lsc.reset_index()

df = pd.concat([ff, lsc], 'i')
df = df.rename(columns={'Mkt-RF': 'Mkt'})



print get_params(df, ['Mkt', 'SMB', 'HML'], 0, 'ret')

