import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm

df = pd.read_csv('FF3F.csv')

df_filter = df.query('197612<Date<201401')
print df
df.drop(df.index[:605])
print df

#for i in range(0,len(df),3):
#    df_filter.ix[i,'3mo_returns'] = math.log(1 + df_filter.ix[i, 'Mkt-RF'])

#print df_filter