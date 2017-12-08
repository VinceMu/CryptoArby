import bittrex
import datetime
import pandas as pd
import numpy as np
import threading

class Flipper:

    bittrexHandler = None
    market = None

    BUYMARGIN = 35
    SELLMARGIN = 65


    def __init__(self,Market):
        self.bittrexHandler = bittrex.Bittrex(None, None,api_version=bittrex.API_V2_0)
        self.market = Market

    def printAllMarkets(self):
        print(self.bittrexHandler.get_markets())

    def getSeries(self,interval):
        candles = self.bittrexHandler.get_candles(self.market, interval)['result']
        closePrices = []
        times = []
        for candleSet in candles:
            closePrices.append(candleSet['C'])
            times.append(candleSet['T'])
        return closePrices,times

    def createDataframe(self,prices,times):
        dataFrame = pd.DataFrame({'Price':prices,'Date':times})
        return dataFrame

    def getDateandTimeIso(self):
        date = datetime.date.isoformat()
        return date

    def calculateRSI(self,period=14):
        rawSeries = myFlipper.getSeries(bittrex.TICKINTERVAL_HOUR)
        dataframe = myFlipper.createDataframe(rawSeries[0],rawSeries[1])
        delta = dataframe['Price'].diff().dropna()
        u = delta * 0
        d = u.copy()
        u[delta > 0] = delta[delta > 0]
        d[delta < 0] = -delta[delta < 0]
        u[u.index[period - 1]] = np.mean(u[:period])  # first value is sum of avg gains
        u = u.drop(u.index[:(period - 1)])
        d[d.index[period - 1]] = np.mean(d[:period])  # first value is sum of avg losses
        d = d.drop(d.index[:(period - 1)])
       # rs = pd.stats.moments.ewma(u, com=period - 1, adjust=False) / \
        #     pd.stats.moments.ewma(d, com=period - 1, adjust=False)
        rs = u.ewm(com = period-1, min_periods=0,adjust=False,ignore_na=False).mean()/ \
             d.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
        print(100 - 100 / (1 + rs))
        return 100 - 100 / (1 + rs)

    def decide(self):
        RSISeries = self.calculateRSI(period=14)
        rsiVal = RSISeries.iloc[-1] #get last value
        print(type(rsiVal))
        print("Current Rsi Value is " + str(rsiVal))
        if rsiVal < self.BUYMARGIN:
            print("buy")
        elif rsiVal > self.SELLMARGIN:
            print("sell")
        else:
            print("doing nothing")

    def run(self):
        print("starting")
        threading.Timer(10.0, self.run).start()
        self.decide()

myFlipper = Flipper("BTC-ETH")
myFlipper.run()