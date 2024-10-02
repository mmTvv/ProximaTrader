import ta
import telebot
from datetime import datetime
from time import sleep
from analitic import Strategy  # Теперь использует новую стратегию
import pandas as pd
import mplfinance as mpf
import matplotlib
from datetime import datetime

from config import *

matplotlib.use('Agg')

class Utils(object):
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
        self.strategy = Strategy(bot)  # Используем новую стратегию
        
        self.indent = 5
        self.pos = 0
        self.closed = 0
        self.poss = []
        self.pnl = 0
        self.summary_pnl = 0
        self.stat_pnl = []
    
    def send(self, text):
        self.tg.send_message(channel_id, text, parse_mode='HTML')

    def draw(self, symbol, text, price1, price2=None):
        # Получение данных по свечам
        data = self.bot.klines(symbol, timeframe=15, limit=48)
        if data.empty:
            return
        data.index = data.index.astype(float) / 1000
        data.index = pd.to_datetime(data.index, unit='s')
        # Настраиваем фигуру
        add_plot = [
            mpf.make_addplot([price1] * len(data), color='white', linestyle='-', label=f'вход: {price1}')
        ]

        # Добавляем линию продажи, если она есть
        if price2 is not None:
            add_plot.append(mpf.make_addplot([price2] * len(data), color='blue', linestyle='-', label=f'выход: {price2}'))
        
        # Рисуем свечной график и сохраняем его
        mpf.plot(data[['Open', 'High', 'Low', 'Close', 'Volume']], type='candle', style='nightclouds', 
                 addplot=add_plot, title=f"{symbol} свечи на похоронах моей психики", ylabel='Price (USD)', savefig='candels.png')

        # Отправляем график в Telegram
        img = open('candels.png', 'rb')
        self.tg.send_photo(channel_id, img, caption=text, parse_mode='HTML')

    def watcher(self, symbol, side, start_price):
        time = datetime.now().timetuple()
        self.pos += 1
        indent = 10
        max_pnl = 0
        sl = False
        
        while True:
            if max_pnl >= 25:
                indent = 15
            elif max_pnl >= 70:
                indent = 20
            sleep(30)
            
            # Получаем данные по символу (часовой таймфрейм)
            data = self.bot.klines(symbol, timeframe=60, limit=50)
            if data.empty:
                continue

            current_price = data['Close'].iloc[-1]
            pnl = round((current_price / (start_price / 100)) - 100, 2) * 10

            # Получение данных для Chandelier Exit и проверка ATR
            long_stop, short_stop, direction = self.strategy.chandelier_exit(data)
            atr = self.strategy.calculate_atr(data)

            # Логика выхода из позиции (для long-позиций)
            if side == 'buy':
                if pnl > max_pnl:
                    max_pnl = pnl
                
                # Условие выхода: цена пересекает линию Chandelier Exit или PnL ниже порога
                if pnl < max_pnl - indent:
                    icon = '✔️' if pnl > 0 else '🚫'

                    self.closed += 1
                    self.summary_pnl += round(pnl, 2)
                    self.pnl = self.summary_pnl / self.closed
                    self.poss.remove(symbol)
                    
                    self.draw(symbol, 
                        icon + ' <b>BUY</b> <code>' + symbol + '</code>\n' +
                        '<b>Время Открытия:</b> ' + str(time[2]) + '.' + str(time[1]) + ' ' + str(time[3]) + ':' + str(time[4]) + '\n' +
                        '<b>P&L x10:</b> ' + str(pnl) + '%\n' +
                        '<b>OPEN:</b> <code>' + str(start_price) + '</code>\n' +
                        '<b>CLOSE:</b> <code>' + str(current_price) + '</code>\n' +
                        '<b>AVR PNL:</b> ' + str(self.pnl) + '\n' +
                        '<b>MAX PNL:</b> ' + str(max_pnl) + '\n' + 
                        '<b>Orders:</b> ' + str(self.closed) + '/' + str(self.pos) +'\n\n'
                        f'<b>https://www.bybit.com/trade/usdt/{symbol}</b>', start_price, current_price
                    )
                    break
               
            # Логика выхода из позиции (для short-позиций)
            elif side == 'sell':
                pnl = -pnl
                if pnl > max_pnl:
                    max_pnl = pnl

                # Условие выхода: цена пересекает линию Chandelier Exit или PnL ниже порога
                if pnl >= max_pnl - indent:
                    icon = '✔️' if pnl > 0 else '🚫'

                    self.closed += 1
                    self.summary_pnl += round(pnl, 2)
                    self.pnl = self.summary_pnl / self.closed
                    self.poss.remove(symbol)
                    
                    self.draw(symbol,
                        icon + ' <b>SELL</b> <code>' + symbol + '</code>\n' +
                        '<b>Время Открытия:</b> ' + str(time[2]) + '.' + str(time[1]) + ' ' + str(time[3]) + ':' + str(time[4]) + '\n' +
                        '<b>P&L x10:</b> ' + str(pnl) + '%\n' +
                        '<b>OPEN:</b> <code>' + str(start_price) + '</code>\n' +
                        '<b>CLOSE:</b> <code>' + str(current_price) + '</code>\n' +
                        '<b>AVR PNL:</b> ' + str(self.pnl) + '\n' +
                        '<b>MAX PNL:</b> ' + str(max_pnl) + '\n' + 
                        '<b>Orders:</b> ' + str(self.closed) + '/' + str(self.pos) +'\n\n'
                        f'<b>https://www.bybit.com/trade/usdt/{symbol}</b>', start_price, current_price
                    )
                    break
            print(f'{symbol} {current_price} {pnl}')
