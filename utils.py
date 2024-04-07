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

    def watcher(self, symbol, side):
        try:
            kl = self.bot.klines(symbol, timeframe=timeframe, limit = 1)
            start_price = kl.Close.iloc[-1]
            time = datetime.now().timetuple()
            while True:
                sleep(120)
                current_price = self.bot.klines(symbol, timeframe=timeframe, limit=1).Close.iloc[-1]
                pnl = round((current_price/(start_price / 100))-100, 2)*10
                if side == 'buy' and pnl > 20 or pnl < -50:
                    
                    if pnl>0: icon = '🟢'
                    elif pnl<=0: icon = '🔴'

                    self.send(icon +'Сделка BUY '+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(pnl)+'%')
                    break
                elif side == 'sell' and pnl < -20 or pnl >50:
                    
                    if -pnl>0: icon = '🟢'
                    elif -pnl<=0: icon = '🔴'

                    self.send(icon + 'Сделка SELL '+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(-pnl)+'%')
                    break

        except Exception as err:
            print('[ERROR]: '+ err)
