import ta
from config import *

class Utils(object):
    
    def __init__(self, bot):
        self.bot = telebot.TeleBot(telegram)
    
    def send(self, text):
        self.bot.send_message(channel_id, text)


    # Some RSI strategy. Make your own using this example
    def rsi_signal(symbol):
        kl = bot.klines(symbol)
        ema = ta.trend.ema_indicator(kl.Close, window=200)
        rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
        if rsi.iloc[-3] < 30 and rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
            return 'up'
        if rsi.iloc[-3] > 70 and rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
            return 'down'
        else:
            return 'none'

    # William %R signal
    def williamsR(symbol):
        kl = bot.klines(symbol)
        w = ta.momentum.WilliamsRIndicator(kl.High, kl.Low, kl.Close, lbp=24).williams_r()
        ema_w = ta.trend.ema_indicator(w, window=24)
        if w.iloc[-1] < -99.5:
            return 'up'
        elif w.iloc[-1] > -0.5:
            return 'down'
        elif w.iloc[-1] < -75 and w.iloc[-2] < -75 and w.iloc[-2] < ema_w.iloc[-2] and w.iloc[-1] > ema_w.iloc[-1]:
            return 'up'
        elif w.iloc[-1] > -25 and w.iloc[-2] > -25 and w.iloc[-2] > ema_w.iloc[-2] and w.iloc[-1] < ema_w.iloc[-1]:
            return 'down'
        else:
            return 'none'

    def analys(elem):
       kl = bot.klines(symbol)