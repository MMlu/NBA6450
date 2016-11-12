import pandas as pd
import numpy as np
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
        return 0
    @constant
    def MAX_CAPACITY(self):
        return 1

CONST = _Const()

DATA = pd.read_csv("data/PriceData.csv", index_col =0, parse_dates=True)


current = {
    'coveredTime' : 100000000,
    'capacity' : CONST.MAX_CAPACITY,
    'futures' : [],
    'nextMaturity' : np.datetime64('1995-01-24'),
    'profit' : 0,
    'LIBOR' : float(DATA['LIBOR1'][0])/100,
}
profit = []

def hedgeStrat(date,data):
    if current['coveredTime'] <= 0:
        for i in range(9, 0, -1):
            if checkContangoBackwardation(date, data, "future" + `i`):
                current['coveredTime'] = i
                print "hedgeStratA", current['coveredTime']
                break
    if not checkContangoBackwardation(date, data, 'future1'): #backwardation
        if current['capacity'] < CONST.MAX_CAPACITY: # have some holdings
            pass


def gambleStrat(date,data):
    if current['capacity'] > 0 and checkContangoBackwardation(date,data,"future1"):
        current['futures'].append(Futures(1, data['future1'], current['capacity'], False))
        current['profit'] -= current['capacity'] * data['spot']
        current['capacity'] = 0


# True if Contango, False if Backwardation
def checkContangoBackwardation(date,data,tick):
    return (data[tick] / (1 + (current['LIBOR']/12)) > data['spot'])

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
                    current['profit'] += (f.size * f.price)
                    current['capacity'] += f.size
            else:
                current['futures'][i].monthTillMaturity -= 1

def updateNextMaturityDate():
    one_day = np.timedelta64(1, 'D')
    curDay = current['nextMaturity'].astype(object).day
    curYear = current['nextMaturity'].astype(object).year
    current['nextMaturity'] += one_day
    while current['nextMaturity'].astype(object).day != curDay:
        current['nextMaturity'] += one_day

    if current['nextMaturity'].astype(object).year > curYear:
        current['nextMaturity'] += one_day
        while current['nextMaturity'].astype(object).day > 29:
            current['nextMaturity'] += one_day

def updateLibor(data):
    try:
        current['LIBOR'] = float(data['LIBOR'])/100
    except Exception:
        pass

# Main
for date, data in DATA.iterrows():
    #Process Data
    updateLibor(data)
    current['profit'] = current['profit'] * (1 + (current['LIBOR'] / 365))
    maturityCalculation(date, data)
    markToMarket(date, data)

    #Running Strategy
    hedgeStrat(date, data)
    gambleStrat(date, data)

    profit.append(current['profit'])


plt.plot(profit)
print current
for p in current['futures']: print p.price
print profit[-1]

plt.show()