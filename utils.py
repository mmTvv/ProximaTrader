import ta
import telebot
from datetime import datetime
from time import sleep

from config import *

class Utils(object):
    
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
    
    def send(self, text):
        self.tg.send_message(channel_id, text)

    def watcher(self, symbol, side, timeframe):
        kl = self.bot.klines(symbol, timeframe=timeframe)
        start_price = kl.Close.iloc[-1]
        time = datetime.now().timetuple()
        while True:
            sleep(30)
            kl = self.bot.klines(symbol, timeframe=timeframe)
            rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
            if side == 'buy' and rsi.iloc[-3] > 70 and rsi.iloc[-1] < 70:
                current_price = kl.Close.iloc[-1]
                pnl = round(( (10/start_price) - (10/current_price) ) *10 *current_price , 3)
                if pnl>0: icon = '🟢'
                elif pnl<=0: icon = '🔴'
                self.send(icon +'Сделка BUY '+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L: ' +str(pnl)+'%')
                break
            elif side == 'sell' and rsi.iloc[-3] < 30 and rsi.iloc[-1] > 30:
                current_price = kl.Close.iloc[-1]
                pnl = round(( (10/current_price) - (10/start_price) ) *10 *current_price , 3)
                if pnl>0: icon = '🟢'
                elif pnl<=0: icon = '🔴'
                self.send(icon + 'Сделка SELL '+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L: ' +str(pnl)+'%')
                break

