from flask import  Flask
import FlipperBot
import os

app = Flask(__name__)
market1 = "BTC-XLM"
market2 = "BTC-NAV"
market3 = "BTC-ETH"

@app.route('/1')
def show1():
    return displayMarketLog(market1)

@app.route('/2')
def show2():
    return displayMarketLog(market2)

@app.route('/3')
def show3():
    return displayMarketLog(market3)

@app.route('/tasks/run1')
def runBot1():
    bot = FlipperBot.FlipperV2(market1, "f9e36fd45e184e3c8801188dd93c4628", 0.0012, BuyMargin=35, SellMargin=65)
    bot.run()
    return "OK"

@app.route('/tasks/run2')
def runBot2():
    bot = FlipperBot.FlipperV2(market2, "f9e36fd45e184e3c8801188dd93c4628", 0.0012, BuyMargin=35, SellMargin=65)
    bot.run()
    return "OK"

@app.route('/tasks/run3')
def runBot3():
    bot = FlipperBot.FlipperV2(market3, "f9e36fd45e184e3c8801188dd93c4628", 0.0012, BuyMargin=35, SellMargin=65)
    bot.run()
    return "OK"

def displayMarketLog(market):
    if os.path.isfile(market + " Log.txt"):
        with open(market + " Log.txt", 'r') as myfile:
            text = myfile.read()
            return text.replace('\n', '<br>')
    else:
        return "No Log file"

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=80, debug=True)
