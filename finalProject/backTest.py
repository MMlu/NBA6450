# Bryan Lu
# For NBA6450 Final Project

import Queue
import pandas as pd
import numpy as np
from math import *
from scipy.stats import norm
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date

########## Helpers
class Futures:
    def __init__(self, monthTillMaturity, price, size, longShort):
        self.monthTillMaturity = monthTillMaturity
        self.price = price
        self.size = size
        self.longShort = longShort
    def printFutures(self):
        print 'mtm:', self.monthTillMaturity, ',price:', self.price, ',size:', self.size, ',longShort:', self.longShort

class Straddle: # we only short
    def __init__(self, strike, monthTillMaturity, size):
        self.monthTillMaturity = monthTillMaturity
        self.strike = strike
        self.size = size

def BlackScholes(CallPutFlag, S, K, T, r, d, v):
    d1 = (log(float(S) / K) + ((r - d) + v * v / 2.) * T) / (v * sqrt(T))

    d2 = d1 - v * sqrt(T)
    if CallPutFlag == 'c':
        return S * exp(-d * T) * norm.cdf(d1) - K * exp(-r * T) * norm.cdf(d2)
    else:
        return K * exp(-r * T) * norm.cdf(-d2) - S * exp(-d * T) * norm.cdf(-d1)

# CONSTANT Parameters
def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f(self)
    return property(fget, fset)

class _Const(object):
    @constant
    def STRADDLE(self):
        return True
    @constant
    def STORAGE_COST(self):
        return 3000
    @constant
    def MAX_CAPACITY(self):
        return 3300000
    @constant
    def SHIP_COST(self):
        return 0.14
    @constant
    def SHIP_LOST(self):
        return 1.0017

############### Variables
CONST = _Const()
profit = []
netPosition = []
pltX = []
CAPACITY = []
DAYRETURN = []
StraddleCashFlow = []
StraddleCashFlowX = []
DATA = pd.read_csv("data/PriceData.csv", index_col =0, parse_dates=True)
if CONST.STRADDLE:
    DATA = pd.read_csv("data/gasOptionPrice.csv", index_col=0, parse_dates=True)
    callPrice = []
    putPrice = []

    avgSpot30d = []
    curSpotTotal = 0
    q = Queue.Queue(10)
    curLibor = float(DATA['LIBOR1'][0])/100
    dayTillMaturity = 51.
    for date, data in DATA.iterrows():
        try:
            curLibor = float(data['1MLIBOR']) / 100
        except Exception:
            pass

        if date.day >= 26:
            dayTillMaturity = 61.

        callPrice.append(BlackScholes('c',data['future2'], data['future2'], dayTillMaturity/365, curLibor, 0, data['callVol']))
        putPrice.append(BlackScholes('p',data['future2'], data['future2'], dayTillMaturity/365, curLibor, 0, data['putVol']))

        if q.full():
            curSpotTotal -= q.get()
        curSpotTotal += data['spot']
        q.put(data['spot'])

        avgSpot30d.append(curSpotTotal/10.0)
        dayTillMaturity -= 1

    DATA['call'] = callPrice
    DATA['put'] = putPrice
    DATA['avgSpot30d'] = avgSpot30d

current = {
    'coveredTime' : 0,
    'capacity' : CONST.MAX_CAPACITY,
    'futures' : [],
    'nextMaturity' : np.datetime64('1995-01-27'),
    #'nextMaturityStraddle' : np.datetime64('1995-01-26'),
    #'nextMaturity' : np.datetime64('2007-10-29'),
    'curMaturityStraddle' : np.datetime64('2007-09-25'),
    'nextMaturityStraddle' : np.datetime64('2007-10-26'),
    'profit' : 0,
    'LIBOR' : float(DATA['LIBOR1'][0])/100,
    'numTrades' : 0,
    'countFlip' : 0,
    'straddles' : None,
    'numStraddles' : 0,
}

################ Trading Strategy Functions
def tradeFuction(data, longShort, period, amount): # longShort = 1 or -1, -1 for short future long spot, 1 reverse trade
    current['futures'].append(Futures(period, data['future' + `period`], amount / CONST.SHIP_LOST, longShort==1))
    current['capacity'] = current['capacity'] + longShort * amount
    current['numTrades'] += 1
    if longShort: # short spot
        current['profit'] += longShort * amount * data['spot'] / CONST.SHIP_LOST
        current['profit'] -= CONST.SHIP_COST * amount
    else: # long spot
        current['profit'] += longShort * amount * data['spot'] * CONST.SHIP_LOST
        current['profit'] -= CONST.SHIP_COST * amount * CONST.SHIP_LOST

def flipStrat(date,data):
    if checkBackwardation(date, data, 1):
        if current['capacity'] < CONST.MAX_CAPACITY: # have some holdings
            current['countFlip'] += 1
            tradeFuction(data, 1, 1, (CONST.MAX_CAPACITY - current['capacity']))

def gambleStrat(date,data):
    if current['capacity'] > 0 and checkContango(date,data, 1):
        tradeFuction(data, -1, 1, current['capacity'])

def shortVolStrat(date, data):
    #print data['avgSpot30d'] * exp((data['putVol'] + data['callVol']) / 2), data['spot']
    if current['straddles'] is None and \
            data['future1'] < data['avgSpot30d'] * exp((data['putVol'] + data['callVol']) / 10) and \
            data['future1'] > data['avgSpot30d'] / exp((data['putVol'] + data['callVol']) / 10) :
            #date + np.timedelta64(10, 'D') > current['nextMaturityStraddle']:
        straddleSize = CONST.MAX_CAPACITY * exp(-(data['putVol'] + data['callVol']) / 2)
        current['profit'] += straddleSize * (data['call'] + data['put'])
        StraddleCashFlow.append(straddleSize * (data['call'] + data['put']))
        mTillM = 2
        if date.month < current['nextMaturityStraddle'].astype(object).month:
            mTillM = 1
        current['straddles'] = Straddle(data['future1'], mTillM, straddleSize)
        current['numStraddles'] += 1


# True if Contango
def checkContango(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12))
            > (data['spot'] * CONST.SHIP_LOST**2) + CONST.SHIP_COST * 2)

def checkBackwardation(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12))
            < (data['spot'] * CONST.SHIP_LOST**2) - CONST.SHIP_COST * 2)

def markToMarket(date,data):
    for f in current['futures']:
        dPrice = data["future" + `f.monthTillMaturity`]
        if f.longShort:
            current['profit'] += (dPrice - f.price) * f.size
        else:
            current['profit'] += (f.price - dPrice) * f.size
        f.price = dPrice

def maturityCalculation(date,data):
    # Straddle matruity
    if CONST.STRADDLE and date >= (current['curMaturityStraddle']):
        current['curMaturityStraddle'] = current['nextMaturityStraddle']
        current['nextMaturityStraddle'] = updateNextMaturityDate(current['nextMaturityStraddle'], 4)
        if CONST.STRADDLE and current['straddles'] is not None:
            if current['straddles'].monthTillMaturity <= 1:
                s = current['straddles']
                current['profit'] -= abs(s.strike - data['future1']) * s.size
                StraddleCashFlow[-1] -= abs(s.strike - data['future1']) * s.size
                StraddleCashFlowX.append(date)
                current['straddles'] = None
            else:
                current['straddles'].monthTillMaturity -= 1

    # Future maturity
    if date >= current['nextMaturity']:
        current['coveredTime'] -= 1
        current['nextMaturity'] = updateNextMaturityDate(current['nextMaturity'], 3)

        for i in range(len(current['futures']) - 1, -1, -1):
            if current['futures'][i].monthTillMaturity <= 1:
                f = current['futures'].pop(i)
                if f.longShort:
                    current['profit'] -= (f.price + CONST.SHIP_COST * CONST.SHIP_LOST + data['spot']
                                          * (CONST.SHIP_LOST - 1)) * f.size
                    current['capacity'] -= f.size * CONST.SHIP_LOST
                else:
                    current['profit'] += (f.price - CONST.SHIP_COST * CONST.SHIP_LOST) * f.size
                    current['capacity'] += f.size * CONST.SHIP_LOST
            else:
                current['futures'][i].monthTillMaturity -= 1

def updateNextMaturityDate(originalDay, offSetDays):
    one_day = np.timedelta64(1, 'D')
    curMonth = originalDay.astype(object).month
    originalDay += one_day
    while (originalDay.astype(object).month % 12) != ((curMonth + 2) % 12) \
            or not np.is_busday(originalDay):
        originalDay += one_day

    while offSetDays > 0:
        originalDay -= one_day
        if np.is_busday(originalDay):
            offSetDays -= 1
    return originalDay

def updateLibor(data):
    try:
        current['LIBOR'] = float(data['LIBOR1'])/100
    except Exception:
        pass

########## Main
for date, data in DATA.iterrows():
    #Process Data
    updateLibor(data)
    maturityCalculation(date, data)
    #current['profit'] *= (1 + current['LIBOR'] / 365)  # math.exp((math.log(1 + current['LIBOR'], math.e))/365)
    #markToMarket(date, data)

    if date >= np.datetime64('1995-01-01') and date <= np.datetime64('2016-01-01'):
    #if date >= np.datetime64('1990-01-01'):
        current['profit'] -= CONST.STORAGE_COST
        #Running Strategy
        gambleStrat(date, data)
        flipStrat(date, data)
        if CONST.STRADDLE:
            shortVolStrat(date, data)

    pltX.append(date)
    profit.append(current['profit'])
    netPosition.append(current['profit'] + (CONST.MAX_CAPACITY - current['capacity']) * data['spot'])
    CAPACITY.append(CONST.MAX_CAPACITY - current['capacity'])
    divisor = (netPosition[len(netPosition)-2])
    if divisor == 0:
        DAYRETURN.append(0)
    else:
        DAYRETURN.append((netPosition[len(netPosition)-1] - (netPosition[len(netPosition)-2]))/ divisor)


############# Generating Result
curyear = pltX[0].year
yearly = []
temp = 0
for i in range(1,len(pltX)):
    d = pltX[i]
    if d.year != curyear:
        curyear = d.year
        yearly.append(temp)
        temp = 0
    temp += netPosition[i] - netPosition[i-1]

#plt.bar(range(1995, 2016), yearly)
plt.plot(StraddleCashFlow)
#plt.bar(StraddleCashFlow, range(0, len(StraddleCashFlow)))
print current
for p in current['futures']: p.printFutures()
print current['profit'] / 1000000, "million"

print sum(StraddleCashFlow) / 1000000, "million"
plt.show()

#print DATA

#DATA['return'] = DAYRETURN
#DATA.to_csv("rett", sep=',', encoding='utf-8')
#print DATA