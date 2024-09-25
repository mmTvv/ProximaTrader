import ta
import telebot
from datetime import datetime
from time import sleep
from analitic import Strategy  # Теперь использует новую стратегию

from config import *

class Utils(object):
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
        self.strategy = Strategy(bot)  # Используем новую стратегию

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

            # Получаем данные по символу (часовой таймфрейм)
            data = self.bot.klines(symbol, timeframe=60, limit=28)
            rsi = ta.momentum.RSIIndicator(close=data['Close'], window=14).rsi()
            chandelier_exit = self.strategy.chandelier_exit(data)

            current_price = data['Close'].iloc[-1]
            pnl = round((current_price / (start_price / 100)) - 100, 2) * 10

            print(f'{symbol} {current_price} {pnl}')
            
            # Логика выхода из позиции (для long-позиций)
            if side == 'buy':
                # Закрываем сделку, если RSI падает ниже 70 или цена ниже Chandelier Exit
                if rsi.iloc[-1] < 70 or current_price < chandelier_exit.iloc[-1]:
                    if pnl > 0:
                        icon = '✔️'
                    else:
                        icon = '🚫'

                    self.closed += 1
                    self.summary_pnl += round(pnl, 2)
                    self.pnl = self.summary_pnl / self.closed
                    self.poss.remove(symbol)
                    
                    self.send(
                        icon + ' Сделка BUY #' + symbol + ' закрыта. \n' +
                        'Время Открытия: ' + str(time[2]) + '.' + str(time[1]) + ' ' + str(time[3]) + ':' + str(time[4]) + '\n' +
                        'P&L x10: ' + str(pnl) + '%\n' +
                        'OPEN: ' + str(start_price) + '\n' +
                        'CLOSE: ' + str(current_price) + '\n' +
                        'Total PNL: ' + str(self.pnl) + '\n' +
                        'orders: ' + str(self.closed) + '/' + str(self.pos)
                    )
                    break

            # Логика выхода из позиции (для short-позиций)
            elif side == 'sell':
                # Закрываем сделку, если RSI поднимается выше 30 или цена выше Chandelier Exit
                if rsi.iloc[-1] > 30 or current_price > chandelier_exit.iloc[-1]:
                    if -pnl > 0:
                        icon = '✔️'
                    else:
                        icon = '🚫'

                    self.closed += 1
                    self.summary_pnl += round(-pnl, 2)
                    self.pnl = self.summary_pnl / self.closed
                    self.poss.remove(symbol)
                    
                    self.send(
                        icon + ' Сделка SELL #' + symbol + ' закрыта. \n' +
                        'Время Открытия: ' + str(time[2]) + '.' + str(time[1]) + ' ' + str(time[3]) + ':' + str(time[4]) + '\n' +
                        'P&L x10: ' + str(-pnl) + '%\n' +
                        'OPEN: ' + str(start_price) + '\n' +
                        'CLOSE: ' + str(current_price) + '\n' +
                        'Total PNL: ' + str(self.pnl) + '\n' +
                        'orders: ' + str(self.closed) + '/' + str(self.pos)
                    )
                    break
