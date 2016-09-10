import pandas as pd
import numpy as np
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date

warnings.simplefilter(action = "ignore", category = RuntimeWarning)

df = pd.read_csv('Data/vwret.csv')

df.ix[0, 'price'] = 1 + df.ix[0, 'vwretx']
df.ix[0, 'div'] = df.ix[0,'vwretd'] - df.ix[0,'vwretx']

for i in range(1, len(df)):
    df.ix[i, 'price'] = df.ix[i-1, 'price'] * (1 + df.ix[i, 'vwretx'])
    df.ix[i, 'div'] = df.ix[i-1, 'price'] * (df.ix[i, 'vwretd'] - df.ix[i, 'vwretx'])
    df.ix[i, 'returns'] = np.log(df.ix[i, 'price']/df.ix[i-1,'price'])

for i in range(12,len(df)):
    #df.ix[i, 'div_12mo'] = sum(df.ix[i-12:i, 'div'])
    df.ix[i, 'div_12mo'] = sum(df['div'][i-12:i])

for i in range(0,len(df)):
    df.ix[i, 'pd_ratio'] = np.log(df.ix[i, 'price']/df.ix[i, 'div_12mo'])


#df.plot(y='pd_ratio')
#print(df)

#Part B
df2 = pd.read_csv('Data/ie_data.csv')
df2['log_CAPE'] = np.log(df2['CAPE'])
print(len(df2))

df['log_CAPE']= df2['log_CAPE']

corr = np.corrcoef(df[12:]['pd_ratio'],df[12:]['log_CAPE'])
#print(df)
#df2.plot(y='log_CAPE')

print("correlation is: " + str(corr[0,1]))

#Part C
auto_regress_pd = stats.AR(df[12:]['pd_ratio'].values)
results = auto_regress_pd.fit(1)
print(results.params)

auto_regress_cape = stats.AR(df[12:]['log_CAPE'].values)
results2 = auto_regress_cape.fit(1)
print(results2.params)

half_life_pd = np.log(0.5)/np.log(results.params[1])
print("P/D half life is: ", half_life_pd )

half_life_cape = np.log(0.5)/np.log(results2.params[1])
print("CAPE half life is: ", half_life_cape)

#Part D
pd_dickey = stats.adfuller(df[12:]['pd_ratio'].values,1)[1]
print(pd_dickey)

cape_dickey = stats.adfuller(df[12:]['log_CAPE'].values,1)[1]
print(cape_dickey)


def rollingsum_windowed(arr,ws):
    x = [sum(arr[i-(ws-1):i+1]) if i>(ws-1) else sum(arr[:i+1])  for i in range(len(arr))]
    return x

def get_data(ticker, fromdate, todate):
    timeSeries = DataReader(ticker,  "fred", fromdate, todate)
    return timeSeries

location = "Data/FF.csv"
ff = pd.read_csv(location,index_col =0,parse_dates=True)


exret = list(ff['Mkt-RF'].values + ff['RF'].values)

lr = [np.log(1+float(i)/100) for i in exret]

mr6 = rollingsum_windowed(lr,6)
mr12 = rollingsum_windowed(lr,12)
mr36 = rollingsum_windowed(lr,36)
mr60 = rollingsum_windowed(lr,60)

Aaay = get_data("AAA",datetime(1977,1,1),datetime(2013,12,31))
Baay = get_data("BAA",datetime(1977,1,1),datetime(2013,12,31))


Default_spread = Baay['BAA'] - Aaay['AAA']

#==============================================================================
print("Average default spread: ", np.average(Default_spread))
print("Stddev of default spread: ", np.std(Default_spread))
model = stats.AR(Default_spread)
results = model.fit(1)
print ("default spread half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================

GS10 = get_data("GS10",datetime(1977,1,1),datetime(2013,12,31))
TB3MS = get_data("TB3MS",datetime(1977,1,1),datetime(2013,12,31))
term_spread = GS10['GS10']-TB3MS['TB3MS']

#==============================================================================
print("Average term spread: ", np.average(term_spread))
print("Stddev of term spread: ", np.std(term_spread))
model = stats.AR(term_spread)
results = model.fit(1)
print ("term spread half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================

location = "Data/icc.csv"
icc = pd.read_csv(location,index_col =0)

icc_append=348*['NaN']
for i in icc['icc'].values:
    icc_append.append(i)
df['icc']=icc_append

#==============================================================================
print("Average icc: ", np.average(icc['icc']))
print("Stddev of icc: ", np.std(icc['icc']))
model = stats.AR(list(icc['icc'].values))
results = model.fit(1)
print ("icc half life = ",np.log(0.5)/np.log(results.params[1]))
#==============================================================================



