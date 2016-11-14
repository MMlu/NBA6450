# Bryan Lu
# For NBA6450 Final Project

import pandas as pd
import numpy as np
import math
from pandas.io.data import DataReader
import matplotlib.pyplot as plt
import statsmodels.tsa.api as stats
import warnings
from datetime import datetime
from datetime import date

class Futures:
    def __init__(self, monthTillMaturity, price, size, longShort):
        self.monthTillMaturity = monthTillMaturity
        self.price = price
        self.size = size
        self.longShort = longShort

# CONSTANT Parameters
def constant(f):
    def fset(self, value):
        raise TypeError
    def fget(self):
        return f(self)
    return property(fget, fset)

class _Const(object):
    @constant
    def STORAGE_COST(self):
        return 0.0017
    @constant
    def MAX_CAPACITY(self):
        return 3300000
    @constant
    def SHIP_COST(self):
        return 0.02

CONST = _Const()

DATA = pd.read_csv("data/PriceData.csv", index_col =0, parse_dates=True)


current = {
    'coveredTime' : 0,
    'capacity' : CONST.MAX_CAPACITY,
    'futures' : [],
    'nextMaturity' : np.datetime64('1995-01-27'),
    'profit' : 0,
    'LIBOR' : float(DATA['LIBOR1'][0])/100,
}
profit = []
netPosition = []

def tradeFuction(longShort, period, amount): # longShort = 1 or -1, -1 for short future long spot, 1 reverse trade
    current['futures'].append(Futures(period, data['future' + `period`], amount, longShort==1))
    current['profit'] = current['profit'] + longShort * amount * data['spot']
    current['capacity'] = current['capacity'] + longShort * amount

def hedgeStrat(date,data):
    if current['coveredTime'] <= 0:
        for i in range(9, 0, -1):
            if checkContangoBackwardation(date, data, i):
                hedgeCapacity = min(current['capacity'], i * 30 * CONST.STORAGE_COST \
                    / (data["future" + `i`] / (1 + (current['LIBOR'] / i)) - (data['spot']) - CONST.SHIP_COST))
                tradeFuction(-1, i, hedgeCapacity)
                break
    if not checkContangoBackwardation(date, data, 1): #backwardation
        if current['capacity'] < CONST.MAX_CAPACITY: # have some holdings
            tradeFuction(1, 1, (CONST.MAX_CAPACITY - current['capacity']))

def gambleStrat(date,data):
    if current['capacity'] > 0 and checkContangoBackwardation(date,data, 1):
        tradeFuction(-1, 1, current['capacity'])

# True if Contango, False if Backwardation
def checkContangoBackwardation(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR']/period)) > (data['spot']) + CONST.SHIP_COST)

def markToMarket(date,data):
    for f in current['futures']:
        dPrice = data["future" + `f.monthTillMaturity`]
        if f.longShort:
            current['profit'] += (dPrice - f.price)
        else:
            current['profit'] += (f.price - dPrice)
        f.price = dPrice

def maturityCalculation(date,data):
    if date >= current['nextMaturity']:
        current['coveredTime'] -= 1
        updateNextMaturityDate()

        for i in range(len(current['futures']) - 1, -1, -1):
            if current['futures'][i].monthTillMaturity == 1:
                f = current['futures'].pop(i)
                if f.longShort:
                    current['profit'] -= (f.size * f.price)
                    current['capacity'] -= f.size
                else:
                    current['profit'] += (f.size * (f.price - CONST.SHIP_COST ))
                    current['capacity'] += f.size
            else:
                current['futures'][i].monthTillMaturity -= 1

def updateNextMaturityDate():
    one_day = np.timedelta64(1, 'D')
    curMonth = current['nextMaturity'].astype(object).month
    curYear = current['nextMaturity'].astype(object).year
    current['nextMaturity'] += one_day
    while (current['nextMaturity'].astype(object).month % 12) != ((curMonth + 2) % 12) \
            or not np.is_busday(current['nextMaturity']):
        current['nextMaturity'] += one_day

    offSetDays = 3
    while offSetDays > 0:
        current['nextMaturity'] -= one_day
        if np.is_busday(current['nextMaturity']):
            offSetDays -= 1

def updateLibor(data):
    try:
        current['LIBOR'] = float(data['LIBOR'])/100
    except Exception:
        pass

# Main
for date, data in DATA.iterrows():
    #Process Data
    updateLibor(data)
    maturityCalculation(date, data)
    markToMarket(date, data)

    #if date >= np.datetime64('2011-01-01') and date <= np.datetime64('2016-01-01'):
    current['profit'] *= (1 + (current['LIBOR'] / 365))
    current['profit'] -= CONST.STORAGE_COST * (CONST.MAX_CAPACITY - current['capacity'])

    #Running Strategy
    hedgeStrat(date, data)
    gambleStrat(date, data)

    profit.append(current['profit'])
    netPosition.append(current['profit'] + (CONST.MAX_CAPACITY - current['capacity']) * data['spot'])


plt.plot(DATA.index.values, profit)
print current
for p in current['futures']: print p.price
print profit[-1]

plt.show()