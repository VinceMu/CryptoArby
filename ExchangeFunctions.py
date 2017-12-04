import ExchangeHandler
import colorama
import os
import re
import math

def List(Market, Currency):
    colorama.init(convert=True,autoreset=True)
    market = ExchangeHandler.APIExchangeHandler(Market)
    print(Market + " For: " + Currency)
    print("Bidding Price: " + colorama.Fore.RED + str(market.getBidPrice(Currency)))
    print("Asking Price: " + colorama.Fore.GREEN + str(market.getAskPrice(Currency)))



def AskBidMarginPrint(Currency):
    marketdict= {}
    for ApiFile in os.listdir("JSONAPI"):
        market = ExchangeHandler.APIExchangeHandler(re.sub('\.json$', '', ApiFile))
        bidPrice = market.getBidPrice(Currency)
        askPrice = market.getAskPrice(Currency)
        commission = market.getTradingCommission()
        if bidPrice is None or askPrice is None or commission is None:
            continue
        marketdict[market.getExchangeName()] = [bidPrice, askPrice, commission]

    lowestAskingPrice = next(iter(marketdict.items()))
    highestBiddingPrice = next(iter(marketdict.items()))

    for market in marketdict.items():
        if lowestAskingPrice[1][1] > market[1][1]:
            lowestAskingPrice = market
        if highestBiddingPrice[1][0] < market[1][0]:
            highestBiddingPrice = market

    percentageColor = colorama.Fore.MAGENTA
    if(1- lowestAskingPrice[1][1]/highestBiddingPrice[1][0] >lowestAskingPrice[1][2] + highestBiddingPrice[1][2] ):
        percentageColor = colorama.Fore.GREEN

    print("buy: " + str(lowestAskingPrice[0]) + " " + str(lowestAskingPrice[1][1]) + " sell: " + str(highestBiddingPrice[0]) + " " + str(highestBiddingPrice[1][0]))
    print("percentage difference " +  percentageColor+ str(1- lowestAskingPrice[1][1]/highestBiddingPrice[1][0]) + "%")

def AskBidMargin(Currency):
    marketdict= {}
    for ApiFile in os.listdir("JSONAPI"):
        market = ExchangeHandler.APIExchangeHandler(re.sub('\.json$', '', ApiFile))
        bidPrice = market.getBidPrice(Currency)
        askPrice = market.getAskPrice(Currency)
        commission = market.getTradingCommission()
        if bidPrice is None or askPrice is None or commission is None:
            continue
        marketdict[market.getExchangeName()] = [bidPrice, askPrice, commission]

    lowestAskingPrice = None
    highestBiddingPrice = None

    for market in marketdict.items():
        if lowestAskingPrice is None or lowestAskingPrice[1][1] > market[1][1]:
            lowestAskingPrice = market
        if highestBiddingPrice is None or highestBiddingPrice[1][0] < market[1][0]:
            highestBiddingPrice = market

    if 1 - lowestAskingPrice[1][1] / highestBiddingPrice[1][0] > lowestAskingPrice[1][2] + highestBiddingPrice[1][2]:
        return lowestAskingPrice[0],  highestBiddingPrice[0] #(buy, sell)
    else:
        return None

