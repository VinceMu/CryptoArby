import ExchangeFunctions
import ExchangeHandler
import datetime

class Portfolio:
    assets = {}
    exchanges = []
    currencies = []

 #{exchange:[currency:amount]}

    def __init__(self, Currencies, Exchanges):
        for exchange in Exchanges:
            currencyAsset = {}
            for currency in Currencies:
                currencyAsset[currency] = 0
            self.assets[exchange] = currencyAsset
        self.exchanges = Exchanges
        self.currencies = Currencies
        print(self.assets)

    def updateAsset(self,Exchange,Currency,Amount):
        if Currency not in self.assets[Exchange]:
            return
        currencyAsset = self.assets.get(Exchange)
        currencyAsset[Currency] = Amount


    def getAssetAmount(self,Exchange,Currency):
        CurrencyAsset = self.assets.get(Exchange)
        return CurrencyAsset[Currency]

    def getPortfolioValue(self, exchange):
        handler = ExchangeHandler.APIExchangeHandler(exchange)
        value = 0
        for exchangeP in self.assets.keys():
            for currency in self.assets[exchange]:
                value += handler.getLastPrice(currency)
        return value

    def getCurrencyPairs(self):
        pairs = []
        for base in currencyPair.CURRENCY_FROM:
            if base not in self.currencies:
                continue
            for currency in self.currencies:
                if base == currency:
                    continue
                pairs.append(currencyPair(currency,base))
        for p in pairs:
            if p.getCurrencyPair() not in currencyPair.ALL_CURRENCY_PAIRS:
                pairs.remove(p)
        return pairs

class Transaction:
    currencyFrom = None
    currencyTo = None

    timeCreated = None

    def __init__(self,fromCurrency, toCurrency,fromAmt,toAmt,fromExchange,toExchange):
        self.currencyFrom = (fromCurrency,fromAmt,fromExchange)
        self.currencyTo = (toCurrency,toAmt,toExchange)
        self.timeCreated = datetime.datetime.now()


class currencyPair:

    currencyFrom = None
    currencyTo = None

    ALL_CURRENCY_PAIRS = ["BTCAUD", "ETHAUD", "BCHAUD", "ETHBTC", "BCHBTC"]
    CURRENCY_FROM = ["AUD","BTC"]

    def __init__(self, toCurrency,fromCurrency):
        self.currencyFrom = fromCurrency
        self.currencyTo = toCurrency

    def getCurrencyPair(self):
        return self.currencyTo + self.currencyFrom