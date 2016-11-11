import pandas as pd
import numpy as np
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date

vrp = pd.read_csv("../Data/VRPtable.csv",index_col =0,parse_dates=True)

