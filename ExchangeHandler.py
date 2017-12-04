import json
import requests as r


class APIExchangeHandler:

    exchangeJSON = None

    def __init__(self, market):
        with open("JSONAPI/" + market+".json") as json_data:
            self.exchangeJSON = json.load(json_data)

    def getAskPrice(self,currency):
        try:
            askPrice = r.get(self.exchangeJSON["Commands"][currency]["TickURL"])
        except KeyError:
            return

        if self.exchangeJSON["Commands"]["AskPrice"] in askPrice.json():
            return float(askPrice.json()[self.exchangeJSON["Commands"]["AskPrice"]])
        else:
            for key in askPrice.json().keys():
                try:
                    innerDict = dict(askPrice.json().get(key))
                    if self.exchangeJSON["Commands"]["AskPrice"] in innerDict.keys():
                        return float(innerDict.get(self.exchangeJSON["Commands"]["AskPrice"] ))
                except TypeError:
                    continue

    def getBidPrice(self,currency):
        try:
            askPrice = r.get(self.exchangeJSON["Commands"][currency]["TickURL"])
        except KeyError:
            return
        if self.exchangeJSON["Commands"]["BidPrice"] in askPrice.json():
            return float(askPrice.json()[self.exchangeJSON["Commands"]["BidPrice"]])
        else:
            for key in askPrice.json().keys():
                try:
                    innerDict = dict(askPrice.json().get(key))
                    if self.exchangeJSON["Commands"]["BidPrice"] in innerDict.keys():
                        return float(innerDict.get(self.exchangeJSON["Commands"]["BidPrice"]))
                except TypeError:
                    continue

        def getBidPrice(self, currency):
            try:
                askPrice = r.get(self.exchangeJSON["Commands"][currency]["TickURL"])
            except KeyError:
                return
            if self.exchangeJSON["Commands"]["BidPrice"] in askPrice.json():
                return float(askPrice.json()[self.exchangeJSON["Commands"]["BidPrice"]])
            else:
                for key in askPrice.json().keys():
                    try:
                        innerDict = dict(askPrice.json().get(key))
                        if self.exchangeJSON["Commands"]["BidPrice"] in innerDict.keys():
                            return float(innerDict.get(self.exchangeJSON["Commands"]["BidPrice"]))
                    except TypeError:
                        continue

        def getLastPrice(self, currency):
            try:
                askPrice = r.get(self.exchangeJSON["Commands"][currency]["TickURL"])
            except KeyError:
                return
            if self.exchangeJSON["Commands"]["LastPrice"] in askPrice.json():
                return float(askPrice.json()[self.exchangeJSON["Commands"]["LastPrice"]])
            else:
                for key in askPrice.json().keys():
                    try:
                        innerDict = dict(askPrice.json().get(key))
                        if self.exchangeJSON["Commands"]["LastPrice"] in innerDict.keys():
                            return float(innerDict.get(self.exchangeJSON["Commands"]["LastPrice"]))
                    except TypeError:
                        continue

    def getExchangeName(self):
        return self.exchangeJSON["Name"]

    def getTradingCommission(self):
        return self.exchangeJSON["Trading Fee"]
