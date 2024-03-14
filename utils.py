import ta
import telebot
from datetime import datetime

from config import *

class Utils(object):
    
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
    
    def send(self, text):
        self.tg.send_message(channel_id, text)

    def watcher(self, symbol, side):
        kl = self.bot.klines(symbol)
        start_price = kl[-1]
        time = datetime.now().timetuple()
        while True:
            rsi = ta.momentum.RSIIndicator(kl.Close).rsi().inloc[-1]
            if side == 'buy' and rsi <70:
                kl = self.bot.klines(symbol)
                current_price = kl[-1]
                self.tg.send('🟢Сделка BUY закрыта. \nВремя Открытия: '+ str(time[2]+'.'+time[1]+ ' '+time[3]+':'+time[4])+ '\nP&L: ' +str((current_price - start_price )* 10))
            if side == 'sell' and rsi >30:
                kl = self.bot.klines(symbol)
                current_price = kl[-1]
                self.tg.send('🔴Сделка SELL закрыта. \nВремя Открытия: '+ str(time[2]+'.'+time[1]+ ' '+time[3]+':'+time[4])+ '\nP&L: ' +str((start_price - current_price )* 10))

    # Some RSI strategy. Make your own using this example
    def rsi_signal(self, symbol):
        kl = self.bot.klines(symbol)
        ema = ta.trend.ema_indicator(kl.Close, window=200)
        rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
        if rsi.iloc[-3] < 30 and rsi.iloc[-2] < 30 and rsi.iloc[-1] > 30:
            return 'up'
        if rsi.iloc[-3] > 70 and rsi.iloc[-2] > 70 and rsi.iloc[-1] < 70:
            return 'down'
        else:
            return 'none'

    # William %R signal
    def williamsR(self, symbol):
        kl = self.bot.klines(symbol)
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


    def RES(self, elem, timeframe):
        kl = self.bot.klines(symbol=elem, timeframe=timeframe)
        # Initialize Bollinger Bands Indicator
        indicator_bb = ta.volatility.BollingerBands(close=kl["Close"], window=bb_ticks, window_dev=bb_std)

        # Add Bollinger Band high indicator
        upper_band = indicator_bb.bollinger_hband_indicator().iloc[-1]

        # Add Bollinger Band low indicator
        lower_band = indicator_bb.bollinger_lband_indicator().iloc[-1]

        rsi = ta.momentum.RSIIndicator(kl.Close).rsi().iloc[-1]

        ema = ta.trend.ema_indicator(kl.Close, window=100).iloc[-1]

        percent_k = ta.momentum.StochasticOscillator(high=kl.High, low = kl.Low, close=kl.Close, window=14).stoch()

        percent_d = ta.trend.SMAIndicator(percent_k, window=3).sma_indicator().iloc[-1]

        support_level = min(kl.Close[-20:])

        resistance_level = max(kl.Close[-20:])

        current_price = kl.Close.iloc[-1]

        
        print(elem + ' ' + str(rsi < 70) + ' ' +str(rsi >50) + ' ' +str(current_price > ema) + ' ' +str(percent_k.iloc[-1] > percent_d) + ' ' +str(current_price > support_level) +' ' + str(current_price < upper_band))
        if rsi < 70 and rsi >55  and current_price > ema and percent_k.iloc[-1] > percent_d and current_price > support_level:
            return 'up'

        elif rsi > 70 and current_price < ema and current_price < resistance_level and current_price > lower_band:
            return 'down'

        else:
            return 'none'