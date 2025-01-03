import ta
import telebot
from datetime import datetime
from time import sleep
import pandas as pd
import mplfinance as mpf
import matplotlib
import matplotlib.pyplot as plt
from config import *
from analitic import Strategy
from threading import Thread as th
matplotlib.use('Agg')

class Utils(object):
    def __init__(self, bot):
        self.tg = telebot.TeleBot(telegram)
        self.bot = bot
        self.strategy = Strategy(bot)
        th(target= self.pnl_pic).start()
        self.indent = 15
        self.pos = 0
        self.closed = 0
        self.poss = []
        self.pnl = 0
        self.summary_pnl = 0
        self.pnl_list = []
        self.hours_pnl=[]
        self.draw('BTCUSDT', 'TEST STARTUP', 70000,65000)
    
    def pnl_pic(self):
        while True:
            sleep(60*60)
            b = 100
            # Сохранение значения в список
            for p in self.hours_pnl:
                b = b + (b * p /100)
            b = b - 100
            self.pnl_list.append(b)
    
            # Построение графика
            plt.plot(self.pnl_list, marker='o', markersize=8, markerfacecolor='red', markeredgewidth=2, markeredgecolor='black')
            plt.title('График ПНЛ Часовые Свечи')
            plt.xlabel('Index')
            plt.ylabel('Value')
            plt.grid(True)
            plt.savefig("pnl.png")
            img = open('pnl.png', 'rb')
            self.hours_pnl=[]
            self.tg.send_photo(channel_id, img, caption="<b>Hours P&L</b>", parse_mode='HTML')

        
    def send(self, text):
        self.tg.send_message(channel_id, text, parse_mode='HTML')

    def draw(self, symbol, text, price1, price2=None):
        # Получаем данные для свечного графика
        data = self.bot.klines(symbol, timeframe=15, limit=48)
        data.index = data.index.astype(float) / 1000
        data.index = pd.to_datetime(data.index, unit='s')
        # Создаем дополнительный график для отображения уровней
        add_plot = [
            mpf.make_addplot([price1] * len(data), color='white', linestyle='-', label=f'Начальная цена: {price1}')
        ]

        # Если имеется уровень закрытия позиции, добавляем его
        if price2 is not None:
            add_plot.append(mpf.make_addplot([price2] * len(data), color='blue', linestyle='-', label=f'Цена закрытия: {price2}'))
        
        # Строим график с добавлением свечей и дополнительных линий
        mpf.plot(data[['Open', 'High', 'Low', 'Close', 'Volume']], type='candle', style='nightclouds', 
                 addplot=add_plot, title=f"{symbol} Свечной график", ylabel='Price (USD)', savefig='candles.png')

        # Отправляем график в Telegram
        img = open('candles.png', 'rb')
        self.tg.send_photo(channel_id, img, caption=text, parse_mode='HTML')

    def watcher(self, symbol, side, start_price):
        time = datetime.now().timetuple()
        self.pos += 1
        max_pnl = 0
        entry_price = start_price
        pre_exit = False
        exit_signal = False
        #ТУТ БУДЕМ РАСЧИТЫВАТЬ СТОПЛОСС!!!!
        sleep(90)
        while True:
            sleep(30)
            
            data = self.strategy.main(symbol)
            current_price = data['price']
            # Рассчитываем текущий PnL
            if side == 'long':
                pnl = (current_price - entry_price) / entry_price * 100 * leverage  # Плечо 10x
            elif side == 'short':
                pnl = (entry_price - current_price) / entry_price * 100 * leverage
            else:
                pnl = 0

            # Обновляем максимальный PnL
            if pnl > max_pnl:
                max_pnl = pnl

            # Проверка на выход по стоп-лоссу или тейк-профиту
            
            if side == 'long':
                if data['direction'] == -1:
                    if pre_exit == True:
                        exit_signal = True
                    else:
                        pre_exit = True
                else: 
                    pre_exit = False

            elif side == 'short':
                if data['direction'] == 1:
                    if pre_exit == True:
                        exit_signal = True
                    else:
                        pre_exit = True
                else:
                    pre_exit = False

            if pnl < (max_pnl - 20):
                exit_signal = True 
            

            # Если сработал сигнал выхода, закрываем позицию
            if exit_signal:
                icon = '✅' if pnl > 0 else '❌'

                self.closed += 1
                self.summary_pnl += round(pnl, 2)
                self.pnl = self.summary_pnl / self.closed
                self.hours_pnl.append(round(pnl, 2))
                # Рисуем график с отмеченными точками входа и выхода
                self.draw(symbol, 
                    icon + f' <b>{side.upper()}</b> <code>{symbol}</code>\n' +
                    f'<b>Дата закрытия:</b> {time[2]}.{time[1]} {time[3]}:{time[4]}\n' +
                    f'<b>P&L x10:</b> {round(pnl, 2)}%\n' +
                    f'<b>Открытие:</b> <code>{entry_price}</code>\n' +
                    f'<b>Закрытие:</b> <code>{current_price}</code>\n' +
                    f'<b>Средний PNL:</b> {round(self.pnl, 2)}%\n' +
                    f'<b>Максимальный PNL:</b> {round(max_pnl, 2)}%\n' + 
                    f'<b>Всего сделок:</b> {self.closed}/{self.pos}\n\n' +
                    f'<b>https://www.bybit.com/trade/usdt/{symbol}</b>', entry_price, current_price
                )
                if symbol in self.poss:
                    sleep(60)
                    self.poss.remove(symbol)
                break

            print(f'{symbol} Текущая цена: {round(current_price, 8)}, PnL: {round(pnl, 2)}%')

