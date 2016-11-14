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
    def printFutures(self):
        print 'mtm:', self.monthTillMaturity, ',price:', self.price, ',size:', self.size, ',longShort:', self.longShort

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
        return 3000
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
    'numTrades' : 0,
    'countFlip' : 0,
}
profit = []
netPosition = []

def tradeFuction(data, longShort, period, amount): # longShort = 1 or -1, -1 for short future long spot, 1 reverse trade
    current['futures'].append(Futures(period, data['future' + `period`], amount, longShort==1))
    current['profit'] = current['profit'] + longShort * amount * data['spot']
    current['capacity'] = current['capacity'] + longShort * amount
    if not longShort == 1:
        current['profit'] -= CONST.SHIP_COST * amount
    current['numTrades'] += 1

def hedgeStrat(date,data):
    if checkBackwardation(date, data, 1):
        if current['capacity'] < CONST.MAX_CAPACITY: # have some holdings
            current['countFlip'] += 1
            tradeFuction(data, 1, 1, (CONST.MAX_CAPACITY - current['capacity']))
    # if current['coveredTime'] <= 0:
    #     tempMax = 0
    #     tempMaxIndex = 0
    #     for i in range(9, 0, -1):
    #         temp = (data["future" + `i`] / 1 + current['LIBOR']/i)
    #         if temp > tempMax:
    #             tempMax = temp
    #             tempMaxIndex =  i
    #     if checkContango(date, data, tempMaxIndex):
    #         current['coveredTime'] = tempMaxIndex
    #         hedgeCapacity = min(current['capacity'], i * 30 * CONST.STORAGE_COST * CONST.MAX_CAPACITY \
    #             / (data["future" + `tempMaxIndex`] / (1 + (current['LIBOR'] / tempMaxIndex)) - (data['spot']) - CONST.SHIP_COST))
    #         #hedgeCapacity = 0
    #         tradeFuction(data, -1, i, math.ceil(hedgeCapacity))
    #
    # if current['coveredTime'] >= 1 and checkBackwardation(date, data, 1): #backwardation

def gambleStrat(date,data):
    if current['capacity'] > 0 and checkContango(date,data, 1):
        tradeFuction(data, -1, 1, current['capacity'])

# True if Contango
def checkContango(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12)) > (data['spot']) + CONST.SHIP_COST)

def checkBackwardation(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12)) < (data['spot']) - CONST.SHIP_COST)

def markToMarket(date,data):
    for f in current['futures']:
        dPrice = data["future" + `f.monthTillMaturity`]
        if f.longShort:
            current['profit'] += (dPrice - f.price) * f.size
        else:
            current['profit'] += (f.price - dPrice) * f.size
        f.price = dPrice

def maturityCalculation(date,data):
    if date >= current['nextMaturity']:
        current['coveredTime'] -= 1
        updateNextMaturityDate()

        for i in range(len(current['futures']) - 1, -1, -1):
            if current['futures'][i].monthTillMaturity <= 1:
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

pltX = []
CAPACITY = []
# Main
for date, data in DATA.iterrows():
    #Process Data
    updateLibor(data)
    maturityCalculation(date, data)
    current['profit'] *= (1 + current['LIBOR'] / 365)  # math.exp((math.log(1 + current['LIBOR'], math.e))/365)
    markToMarket(date, data)

    if date >= np.datetime64('2011-01-01') and date <= np.datetime64('2016-01-01'):
        current['profit'] -= CONST.STORAGE_COST
        #Running Strategy
        hedgeStrat(date, data)
        gambleStrat(date, data)

    pltX.append(date)
    profit.append(current['profit'])
    netPosition.append(current['profit'] + (CONST.MAX_CAPACITY - current['capacity']) * data['spot'])
    CAPACITY.append(CONST.MAX_CAPACITY - current['capacity'])

curyear = pltX[0].year
yearly = []
temp = 0
for i in range(1,len(pltX)):
    d = pltX[i]
    if d.year != curyear:
        curyear = d.year
        yearly.append(temp)
        temp = 0
    temp += profit[i] - profit[i-1]

plt.plot(pltX, netPosition)
print current
for p in current['futures']: p.printFutures()
print current['profit'] / 1000000, "million"

plt.show()