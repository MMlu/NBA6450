import pandas as pd
import numpy as math
import matplotlib.pyplot as ploty
import statsmodels.tsa.api as stats
import warnings

warnings.simplefilter(action = "ignore", category = RuntimeWarning)

location = "/Users/jones/Documents/Data/FF.csv"
ff = pd.read_csv(location,index_col =0,parse_dates=True)
exret = list(ff['Mkt-RF'].values)
exret.remove('Mkt-RF')
lr = [math.log(1+float(i)/100) for i in exret]

ff.