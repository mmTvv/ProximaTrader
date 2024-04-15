import ta
import telebot
from datetime import datetime
from time import sleep
from analitic import analitic

from config import *

class Utils(object):
    
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
        self.analitic = analitic(bot)

        self.pos = 1
        self.closed = 1
        self.poss = []
        self.pnl = 0
        self.summary_pnl = 0
        
    
    def send(self, text):
        self.tg.send_message(channel_id, text)

    def watcher(self, symbol, side):
        
        try:
            kl = self.bot.klines(symbol, timeframe=timeframe, limit = 1)
            start_price = kl.Close.iloc[-1]
            time = datetime.now().timetuple()
            self.pos += 1
            while True:
                sleep(120)
                
                status = self.analitic.main(symbol=symbol, timeframe=timeframe)
                if side == 'buy' and status != 'long':
                    current_price = self.bot.klines(symbol, timeframe=timeframe, limit=1).Close.iloc[-1]
                    pnl = round((current_price/(start_price / 100))-100, 2)*10
                    if pnl>0: icon = '✔️'
                    elif pnl<=0: icon = '🚫'

                    self.send(icon +'Сделка BUY #'+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(pnl)+'%\nOPEN: '+str(start_price)+'\nCLOSE: '+str(current_price)+'\nTotal PNL: '+str(self.pnl))
                    self.closed +=1
                    self.summary_pnl = (self.summary_pnl + round(pnl, 2))
                    self.pnl = summary_pnl/self.closed
                    self.poss.remove(symbol)
                    break
                elif side == 'sell' and status != 'short':
                    current_price = self.bot.klines(symbol, timeframe=timeframe, limit=1).Close.iloc[-1]
                    pnl = round((current_price/(start_price / 100))-100, 2)*10
                    if -pnl>0: icon = '✔️'
                    elif -pnl<=0: icon = '🚫'

                    self.send(icon + 'Сделка SELL #'+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(-pnl)+'%\nOPEN: '+str(start_price)+'\nCLOSE: '+str(current_price)+'\nTotal PNL: '+str(self.pnl))
                    self.closed +=1
                    self.summary_pnl = (self.summary_pnl + round(-pnl, 2))
                    self.pnl = summary_pnl / self.closed
                    self.poss.remove(symbol)
                    break

        except Exception as err:
            print('[ERROR]: '+ str(err))
