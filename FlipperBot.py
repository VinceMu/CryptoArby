import bittrex
import datetime
import pandas as pd
import numpy as np
import threading
import logging
import os
import json
from enum import Enum


def getSeries(bittrex_candles):
    candles = bittrex_candles
    closePrices = []
    times = []
    for candleSet in candles:
        closePrices.append(candleSet['C'])
        times.append(candleSet['T'])
    return closePrices, times


def createDataframe( prices, times):
    dataFrame = pd.DataFrame({'Price': prices, 'Date': times})
    return dataFrame


def calculateRSI(bittrexCandles, period=14):
    rawSeries = getSeries(bittrexCandles)
    dataframe = createDataframe(rawSeries[0], rawSeries[1])
    delta = dataframe['Price'].diff().dropna()
    u = delta * 0
    d = u.copy()
    u[delta > 0] = delta[delta > 0]
    d[delta < 0] = -delta[delta < 0]
    u[u.index[period - 1]] = np.mean(u[:period])  # first value is sum of avg gains
    u = u.drop(u.index[:(period - 1)])
    d[d.index[period - 1]] = np.mean(d[:period])  # first value is sum of avg losses
    d = d.drop(d.index[:(period - 1)])
    rs = u.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean() / \
         d.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
    return 100 - 100 / (1 + rs)


class FlipperV2:

    JSONSTATE_NAME = None
    stateJson = None
    currentState = None
    previousState = None

    BUYMARGIN = None
    SELLMARGIN = None
    TRADINGCOMMISSION = 0.0025
    MINIMUMTRADE = 0.001
    PRICEMULTIPLIER = 1.006

    tradingAmount = None
    myLogger = None

    priceBought = None
    amountBought = None

    key = None
    secret = None

    BUYINGSTATE = "BUYING"
    SELLINGSTATE = "SELLING"
    WAITINGSTATE= "WAITING"

    def __init__(self,Market,key,TradingAmount,BuyMargin=40.00,SellMargin=60.00):
        if TradingAmount < self.MINIMUMTRADE:
            raise ValueError("smaller than minimum trade size " + str(self.MINIMUMTRADE))

        self.secret = "48fbc489dacf4e21ae9ca9cc2bbbb697"
        self.key = key
        self.bittrexHandler = bittrex.Bittrex(api_key=key, api_secret=self.secret,api_version=bittrex.API_V2_0)
        self.market = Market #must be valid bittrex market
        self.BUYMARGIN = BuyMargin
        self.SELLMARGIN = SellMargin

        currencySplit = Market.split("-")
        self.currencyFrom = currencySplit[0]
        self.currencyTo = currencySplit[1]
        self.tradingAmount = TradingAmount
        self.JSONSTATE_NAME = Market + "-state.json"

        self.loadState()
        self.myLogger = logging.getLogger(Market + " Log")

        if not self.myLogger.handlers:
            fileHandler = logging.FileHandler(Market + " Log.txt")
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            fileHandler.setFormatter(formatter)
            self.myLogger.addHandler(fileHandler)
        self.myLogger.setLevel(logging.NOTSET)


    def loadState(self):
        if os.path.isfile(self.JSONSTATE_NAME):
            with open(self.JSONSTATE_NAME) as stateJson:
                stateData = json.load(stateJson)
                self.currentState = stateData["state"]
                self.priceBought = stateData["lastBought"]
                self.previousState = stateData["previousState"]
                self.amountBought = stateData["amountBought"]
        else:
            self.currentState = self.BUYINGSTATE
            self.priceBought = None
            self.previousState = None
            self.amountBought = None
            self.writeStateJson()

    def writeStateJson(self):
        jsonData = {"state": self.currentState,
                    "previousState": self.previousState,
                    "lastBought": self.priceBought,
                    "amountBought": self.amountBought}

        with open(self.JSONSTATE_NAME,'w') as jsonFile:
            json.dump(jsonData,jsonFile)



    def getPrice(self,ordertype):
        orderBook = None
        if ordertype == "BUYING":
            orderBook = self.bittrexHandler.get_orderbook(market=self.market, depth_type=bittrex.SELL_ORDERBOOK)
        elif ordertype == "SELLING":
            orderBook = self.bittrexHandler.get_orderbook(market=self.market, depth_type=bittrex.BUY_ORDERBOOK)
        price = next(iter(orderBook["result"]["buy"]))["Rate"]
        return price

    def run(self):
        RSISeries = calculateRSI(self.bittrexHandler.get_candles(self.market, bittrex.TICKINTERVAL_FIVEMIN)['result'],period=14)
        rsiVal = RSISeries.iloc[-1]
        self.myLogger.warning("RSI Value is " + str(rsiVal))

        if self.currentState == self.BUYINGSTATE:
            if rsiVal < self.BUYMARGIN:
                self.priceBought = self.getPrice("BUYING") * self.PRICEMULTIPLIER
                self.amountBought = self.tradingAmount / self.priceBought
                self.buy(self.amountBought)
                self.currentState = self.WAITINGSTATE
                self.previousState = self.BUYINGSTATE
                self.myLogger.warning("Buying  " + str(self.amountBought) + " " + self.currencyTo)

        elif self.currentState == self.SELLINGSTATE:
            if rsiVal > self.SELLMARGIN:
                amountToSell = self.amountBought
                self.sell(amountToSell)
                self.currentState = self.WAITINGSTATE
                self.previousState = self.SELLINGSTATE
                self.myLogger.warning("selling  " + str(amountToSell) + " " + self.currencyTo)


        elif self.currentState == self.WAITINGSTATE:
            if self.isOrderComplete() is True:
                if self.previousState == self.BUYINGSTATE:
                    self.currentState = self.SELLINGSTATE
                    self.previousState = self.WAITINGSTATE
                elif self.previousState == self.SELLINGSTATE:
                    self.currentState = self.BUYINGSTATE
                    self.previousState = self.WAITINGSTATE
            self.myLogger.warning("waiting")

        self.writeStateJson()

    def buy(self,amount):
        buyHandler = bittrex.Bittrex(api_key=self.key, api_secret=self.secret,api_version=bittrex.API_V1_1)
        response = buyHandler.buy_limit(self.market, amount,self.getPrice(ordertype="BUYING"))
        return response

    def sell(self,amount):
        sellHandler = bittrex.Bittrex(api_key=self.key, api_secret=self.secret, api_version=bittrex.API_V1_1)
        response = sellHandler.sell_limit(self.market, amount, self.getPrice(ordertype="SELLING"))
        return response

    def isOrderComplete(self):
        openOrders = self.bittrexHandler.get_open_orders(self.market)
        if not openOrders['result']:
            return True
        else:
            return False



"""
    state json file structure
{
    state:currState
    previousState: prevState
    lastBought: price currency bought at
    amountBought:amount of currency bought
    
    
}


"""