import colorama
import VirtualEnvironments
import ExchangeFunctions
import ExchangeHandler

#we need this bot to use
class Bot:
    myPortfolio= None
    #
    def __init__(self,portfolio):
        self.myPortfolio = portfolio
        self.currentTransactions = []

    def run(self):
        currencyPairs = self.myPortfolio.getCurrencyPairs()
        for pair in currencyPairs:
           margin = ExchangeFunctions.AskBidMargin(pair.getCurrencyPair())
           if margin is not None:
               amount = self.getBuySellAmounts(pair,margin[0],margin[1])
               self.trade(margin[0], pair,amount, "BUY")
               self.trade(margin[1], pair,amount, "SELL")
               print(" ")
               print(self.myPortfolio.assets)

    def balanceAssets(self):
        pass

    def getBuySellAmounts(self, currencyPair, buyExchange, sellExchange):
        handler = ExchangeHandler.APIExchangeHandler(sellExchange)
        buyAsset = self.myPortfolio.getAssetAmount(buyExchange, currencyPair.currencyFrom)
        sellAsset = self.myPortfolio.getAssetAmount(sellExchange,currencyPair.currencyTo) * handler.getAskPrice(currencyPair.getCurrencyPair())
        if buyAsset > sellAsset:
            return sellAsset / handler.getAskPrice(currencyPair.getCurrencyPair())
        else:
            return buyAsset / handler.getAskPrice(currencyPair.getCurrencyPair()) #buy,sell

    def trade(self,exchange, currencyPair,amount,tradeType):
        handler = ExchangeHandler.APIExchangeHandler(exchange)

        if tradeType == "BUY" and self.myPortfolio.getAssetAmount(exchange,currencyPair.currencyFrom) < amount * +\
                handler.getAskPrice(currencyPair.getCurrencyPair()):
            print("not enough buy amount ")
            return
        elif tradeType == "SELL" and self.myPortfolio.getAssetAmount(exchange,currencyPair.currencyTo) < amount:
            print("not enough sell amount ")
            return

        print("Trading at " + exchange + " for " + currencyPair.getCurrencyPair() + " at " + str(amount) + " type " + tradeType)

        handler = ExchangeHandler.APIExchangeHandler(exchange)
        volumeTraded = None

        if tradeType == "BUY":
            price = handler.getAskPrice(currencyPair.getCurrencyPair())
            volumeTraded = amount * price

            self.myPortfolio.updateAsset(exchange, currencyPair.currencyFrom, (
                self.myPortfolio.getAssetAmount(exchange, currencyPair.currencyFrom) - volumeTraded))
            self.myPortfolio.updateAsset(exchange, currencyPair.currencyTo, (
                self.myPortfolio.getAssetAmount(exchange, currencyPair.currencyTo) + amount))

        elif tradeType == "SELL":
            price = handler.getBidPrice(currencyPair.getCurrencyPair())
            volumeTraded = price * amount
            self.myPortfolio.updateAsset(exchange, currencyPair.currencyFrom, (
                self.myPortfolio.getAssetAmount(exchange, currencyPair.currencyFrom) +volumeTraded))
            self.myPortfolio.updateAsset(exchange, currencyPair.currencyTo, (
                self.myPortfolio.getAssetAmount(exchange, currencyPair.currencyTo) - amount))

        if volumeTraded is None:
            print("Trade not made! Could not get volume traded")
            return

p = VirtualEnvironments.Portfolio(["BTC", "ETH", "BCH","AUD"], ["IndependentReserve","BTCMarkets","ACX"])
p.updateAsset("BTCMarkets","AUD", 1000)
p.updateAsset("BTCMarkets","ETH", 1.5)
p.updateAsset("BTCMarkets","BTC", 0.5)

p.updateAsset("IndependentReserve","AUD", 1000)
p.updateAsset("IndependentReserve","ETH", 1.5)
p.updateAsset("IndependentReserve","BTC", 0.5)

p.updateAsset("ACX","AUD", 1000)
p.updateAsset("ACX","ETH", 1.5)
p.updateAsset("ACX","BTC", 0.5)

print(p.assets)

b = Bot(p)

while(True):
    b.run()






