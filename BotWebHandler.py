from flask import  Flask
import FlipperBot

bot = FlipperBot.Flipper("BTC-ADA","f9e36fd45e184e3c8801188dd93c4628",0.001,BuyMargin=35,SellMargin=65)
app = Flask(__name__)

@app.route('/')
def show():
    return bot.getLog()

@app.route('/tasks/run')
def runBot():
    bot.run(time=60.0)

if __name__ == '__main__':
    app.run(debug=True)
