# Bryan Lu
# For NBA6450 Final Project

import pandas as pd
import numpy as np
from math import *
from scipy.stats import norm
import matplotlib.pyplot as plt

########## Helpers
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
    def STRADDLE(self):
        return False
    @constant
    def STORAGE_COST(self):
        return 0.0025
    @constant
    def STORAGE_MIN_COST(self):
        return 1800
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

# True if Contango
def checkContango(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12))
            > (data['spot'] * CONST.SHIP_LOST**2) + CONST.SHIP_COST * 2)

def checkBackwardation(date,data,period):
    return (data["future" + `period`] / (1 + (current['LIBOR'] * period / 12))
            < (data['spot'] * CONST.SHIP_LOST**2) - CONST.SHIP_COST * 2)

def maturityCalculation(date,data):
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

    if date >= np.datetime64('2011-01-01') and date <= np.datetime64('2016-01-01'):
    #if date >= np.datetime64('1990-01-01'):
        current['profit'] -= CONST.STORAGE_MIN_COST
        current['profit'] -= CONST.STORAGE_COST * (CONST.MAX_CAPACITY - current['capacity'])
        #Running Strategy
        gambleStrat(date, data)
        flipStrat(date, data)

print current['profit'] / 1000000