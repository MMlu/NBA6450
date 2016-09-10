import numpy as np
import pandas as pd
import math
import matplotlib.pyplot as plt
import statsmodels.formula.api as sm
import statsmodels.tsa.api as stats

#Part A

df = pd.read_csv('vwret.csv')

df.ix[0, 'price'] = 1 + df.ix[0, 'vwretx']
df.ix[0, 'div'] = df.ix[0,'vwretd'] - df.ix[0,'vwretx']

for i in range(1, len(df)):
    df.ix[i, 'price'] = df.ix[i-1, 'price'] * (1 + df.ix[i, 'vwretx'])
    df.ix[i, 'div'] = df.ix[i-1, 'price'] * (df.ix[i, 'vwretd'] - df.ix[i, 'vwretx'])
    df.ix[i, 'returns'] = math.log(df.ix[i, 'price']/df.ix[i-1,'price'])

for i in range(12,len(df)):
    #df.ix[i, 'div_12mo'] = sum(df.ix[i-12:i, 'div'])
    df.ix[i, 'div_12mo'] = sum(df['div'][i-12:i])

for i in range(0,len(df)):
    df.ix[i, 'pd_ratio'] = math.log(df.ix[i, 'price']/df.ix[i, 'div_12mo'])


df.plot(y='pd_ratio')
#print(df)

#Part B
df2 = pd.read_csv('CAPE.csv')
df2['log_CAPE'] = np.log(df2['CAPE'])
#print(df2)

df['log_CAPE']= df2['log_CAPE']

corr = np.corrcoef(df[13:]['pd_ratio'],df[13:]['log_CAPE'])
print df
df2.plot(y='log_CAPE')

#print("correlation is: " + str(corr[0,1]))

#Part C
auto_regress_pd = stats.AR(df[13:]['pd_ratio'].values)
results = auto_regress_pd.fit(1)
print(results.params)

auto_regress_cape = stats.AR(df[13:]['log_CAPE'].values)
results2 = auto_regress_cape.fit(1)
print(results2.params)

half_life_pd = np.log(0.5)/np.log(results.params[1])
print("P/D half life is: ", half_life_pd )

half_life_cape = np.log(0.5)/np.log(results2.params[1])
print("CAPE half life is: ", half_life_cape)

#Part D
pd_ols = sm.ols(formula='returns ~ pd_ratio',data=df).fit()
cape_ols = sm.ols(formula='returns ~ log_CAPE',data=df).fit()

#print(pd_ols.summary())
#print(cape_ols.summary())



plt.show()



