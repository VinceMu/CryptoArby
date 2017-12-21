import bittrex
import datetime
import pandas as pd
import numpy as np
import threading
import logging
from enum import Enum


class FlipperStates(Enum):
    BUYING = 0
    SELLING = 1
    WAITING = 2

class Flipper:

    bittrexHandler = None
    market = None
    currencyFrom = None
    currencyTo = None

    currentState = None

    BUYMARGIN = None
    SELLMARGIN = None
    TRADINGCOMMISSION = 0.0025
    MINIMUMTRADE = 0.001
    PRICEMULTIPLIER = 1.006

    tradingAmount = None
    #balance = {}
    myLogger = None

    lastBought = None
    priceBought = None

    key = None
    secret = None

    """
    :param Market: market being traded
    :type market: str
    :param key: api key 
    :type key: str
    :param TradingAmount: unit of currency Trading in terms of the market being traded from.
    :type TradingAmount: float 
    """
    def __init__(self,Market,key,TradingAmount,BuyMargin=40.00,SellMargin=60.00):
        if TradingAmount < self.MINIMUMTRADE:
            raise ValueError("smaller than minimum trade size " + str(self.MINIMUMTRADE))
            exit(1)

        self.secret = input("secret:")
        self.key = key
        self.bittrexHandler = bittrex.Bittrex(api_key=key, api_secret=self.secret,api_version=bittrex.API_V2_0)
        self.market = Market

        self.BUYMARGIN = BuyMargin
        self.SELLMARGIN = SellMargin

        self.myLogger = logging.getLogger(Market + " Log")
        fileHandler = logging.FileHandler(Market + " Log.txt")
        formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
        fileHandler.setFormatter(formatter)
        self.myLogger.addHandler(fileHandler)
        self.myLogger.setLevel(logging.NOTSET)

        currencySplit = Market.split("-")
        self.currencyFrom = currencySplit[0]
        self.currencyTo = currencySplit[1]

        self.currentState = FlipperStates.BUYING
        self.tradingAmount = TradingAmount
        #self.balance[self.currencyFrom],self.balance[self.currencyTo] = self.getBalances()
        self.lastBought = 0
        #print(self.balance)

    def getBalances(self):
        currencyFromResponse = self.bittrexHandler.get_balance(self.currencyFrom)
        currencytoResponse = self.bittrexHandler.get_balance(self.currencyTo)
        currencyFromBalance = currencyFromResponse["result"]["Balance"]
        currencyToBalance = currencytoResponse["result"]["Balance"]
        return currencyFromBalance,currencyToBalance

    def getPrice(self,ordertype):
        orderBook = None
        if ordertype == "BUYING":
            orderBook = self.bittrexHandler.get_orderbook(market=self.market, depth_type=bittrex.SELL_ORDERBOOK)
        elif ordertype == "SELLING":
            orderBook = self.bittrexHandler.get_orderbook(market=self.market, depth_type=bittrex.BUY_ORDERBOOK)
        price = next(iter(orderBook["result"]["buy"]))["Rate"]
        return price

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

    def calculateRSI(self,period=14):
        rawSeries = myFlipper.getSeries(bittrex.TICKINTERVAL_ONEMIN)
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
        rs = u.ewm(com = period-1, min_periods=0,adjust=False,ignore_na=False).mean()/ \
             d.ewm(com=period - 1, min_periods=0, adjust=False, ignore_na=False).mean()
        return 100 - 100 / (1 + rs)

    def decide(self):

        if self.isOrderComplete() is False:
            self.myLogger.warning("Waiting for Order to be filled")
            print("waiting for Order")
            return

        RSISeries = self.calculateRSI(period=14)
        rsiVal = RSISeries.iloc[-1] #get current RSI Value

        self.myLogger.warning("Current Rsi Value is " + str(rsiVal))
        print("Current Rsi Value is " + str(rsiVal))


        if rsiVal < self.BUYMARGIN and self.currentState == FlipperStates.BUYING:
            self.priceBought = self.getPrice("BUYING") * self.PRICEMULTIPLIER
            amountToBuy = self.tradingAmount / self.priceBought  #amount of currencyTo to buy
            self.lastBought = amountToBuy * (1-self.TRADINGCOMMISSION)
            self.buy(amountToBuy)
            self.myLogger.warning("Buying  " + str(amountToBuy) + " " + self.currencyTo)
            print("Buying  " + str(amountToBuy) + " " + self.currencyTo)
            self.currentState = FlipperStates.SELLING

        elif rsiVal > self.SELLMARGIN and self.currentState == FlipperStates.SELLING:
            amountToSell = self.lastBought
            self.sell(amountToSell)
            self.myLogger.warning("selling  " + str(amountToSell) + " " + self.currencyTo)
            print("selling  " + str(amountToSell) + " " + self.currencyTo)
            self.currentState = FlipperStates.BUYING

        else:
            print("doing nothing")
            self.myLogger.warning("doing nothing")

    def run(self,time=60.0):
        threading.Timer(time, self.run).start()
        self.decide()

    def buy(self,amount):
        """self.bittrexHandler.trade_buy(market=self.market,
                                      quantity=amount,
                                      order_type=bittrex.ORDERTYPE_MARKET,
                                      time_in_effect=bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED,
                                      condition_type=bittrex.CONDITIONTYPE_NONE) - not working cos API 2 is bugged!"""

        buyHandler = bittrex.Bittrex(api_key=self.key, api_secret=self.secret,api_version=bittrex.API_V1_1)
        response = buyHandler.buy_limit(self.market, amount,self.getPrice(ordertype="BUYING"))
        return response

    def sell(self,amount):
        """self.bittrexHandler.trade_sell(market=self.market,
                                      quantity=amount,
                                      order_type=bittrex.ORDERTYPE_MARKET,
                                      time_in_effect=bittrex.TIMEINEFFECT_GOOD_TIL_CANCELLED,
                                      condition_type=bittrex.CONDITIONTYPE_NONE) - not working cos API 2 is bugged!"""
        sellHandler = bittrex.Bittrex(api_key=self.key, api_secret=self.secret, api_version=bittrex.API_V1_1)
        response = sellHandler.sell_limit(self.market, amount, self.getPrice(ordertype="SELLING"))
        return response


    def isOrderComplete(self):
        openOrders = self.bittrexHandler.get_open_orders(self.market)
        if not openOrders['result']:
            return True
        else:
            return False

myFlipper = Flipper("BTC-ZEC","f9e36fd45e184e3c8801188dd93c4628",0.001,BuyMargin=40,SellMargin=60)
myFlipper.run(time=60.0)
