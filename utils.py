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

        self.start = []
        self.pos = 0
        self.closed = 0
        self.poss = []
        self.pnl = 0
        self.summary_pnl = 0
        self.stat_pnl = []
    
    def send(self, text):
        self.tg.send_message(channel_id, text)

    def stats(self):
        while True:
            sleep(60)
            self.stat_pnl.append(self.pnl)
            self.pnl = 0

    def watcher(self, symbol, side, start_price):
        
        time = datetime.now().timetuple()
        self.pos += 1
        while True:
            sleep(30)

            data = self.bot.klines(symbol, timeframe = timeframe, limit = 28)    
            rsi = ta.momentum.RSIIndicator(close = data['Close'], window = 14).rsi()
            
            current_price = data.Close.iloc[-1]
            pnl = round((current_price/(start_price / 100))-100, 2)*10
            print(f'{symbol} {current_price} {pnl}')
            
            if side == 'buy' and rsi.iloc[-1]<68:
                if pnl>0: icon = '✔️'
                elif pnl<=0: icon = '🚫'

                self.closed +=1
                self.summary_pnl = (self.summary_pnl + round(pnl, 2))
                self.pnl = self.summary_pnl/self.closed
                self.poss.remove(symbol)
                self.send(icon +'Сделка BUY #'+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(pnl)+'%\nOPEN: '+str(start_price)+'\nCLOSE: '+str(current_price)+'\nTotal PNL: '+str(self.pnl)+'\norders: '+str(self.closed)+'/'+str(self.pos))
                        
                break
            elif side == 'sell' and data['side'] != 'short':
                if -pnl>0: icon = '✔️'
                elif -pnl<=0: icon = '🚫'

                self.closed +=1
                self.summary_pnl = (self.summary_pnl + round(-pnl, 2))
                self.pnl = self.summary_pnl / self.closed
                self.poss.remove(symbol)
                self.send(icon + 'Сделка SELL #'+ symbol +' закрыта. \nВремя Открытия: '+ str(str(time[2])+'.'+str(time[1])+ ' '+str(time[3])+':'+str(time[4]))+ '\nP&L x10: ' +str(-pnl)+'%\nOPEN: '+str(start_price)+'\nCLOSE: '+str(current_price)+'\nTotal PNL: '+str(self.pnl)+'\norders: '+str(self.closed)+'/'+str(self.pos))
                    
                break
'''            except Exception as err:
                print(f'{symbol} {err} {data}')

    except Exception as err:
        print('[ERROR]: '+ str(err))
'''