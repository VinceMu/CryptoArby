import threading
import os
import ExchangeFunctions
import colorama

CurrencyList = ["BTCAUD","ETHAUD","BCHAUD","ETHBTC","BCHBTC"]
colorama.init(convert=True, autoreset=True)


def currencyAskBidMargins():
    cls()
    for currency in CurrencyList:
        print("======" + currency+"======" + colorama.Fore.WHITE)
        ExchangeFunctions.AskBidMarginPrint(currency)
        print("")

def cls():
    os.system('cls' if os.name=='nt' else 'clear')

while True:
    currencyAskBidMargins()