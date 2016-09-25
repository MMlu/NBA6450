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


Aaay = get_data("AAA",datetime(1977,1,1),datetime(2013,12,31))