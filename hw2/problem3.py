import pandas as pd
import numpy as np
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date



def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  "fred", fromdate, todate)
    return timeSeries


ff = pd.read_csv("Data/FF.csv",index_col =0,parse_dates=True)
exret = list(ff['Mkt-RF'].values)
smb = list(ff['SMB'].values)
hml = list(ff['HML'].values)
rf = list(ff['RF'].values)