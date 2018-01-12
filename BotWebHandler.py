from flask import  Flask
import FlipperBot
import os

app = Flask(__name__)
market = "BTC-XLM"

@app.route('/')
def show():
    if os.path.isfile(market + "Log.txt"):
        with open(market + "Log.txt", 'r') as myfile:
            text = myfile.read()
            return text
    else:
        return "No Log file"

@app.route('/tasks/run')
def runBot():
    bot = FlipperBot.FlipperV2(market, "f9e36fd45e184e3c8801188dd93c4628", 0.001, BuyMargin=35, SellMargin=65)
    bot.run()

if __name__ == '__main__':
    app.run(debug=True)
