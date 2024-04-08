from config import *
import utils
import bybit
import pandas as pd
import ta
from time import sleep
import threading as th
from analitic import analitic

bot = bybit.ByBit()
utils = utils.Utils(bot)
analitic = analitic(bot)

symbols = bot.get_tickers()     # getting all symbols from the Bybit Derivatives

print(f'Your balance: {bot.get_balance()} USDT')

while True:
    balance = bot.get_balance()

    if balance == None:
        print('Cant connect to API')

    if balance != None and float(balance) > qty/leverage:

        balance = float(balance)
        pos = bot.get_positions()

        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for elem in symbols:
                pos = bot.get_positions()
                if len(pos) >= max_pos and elem in pos:
                    break

                # Signal to buy or sell
                signal = analitic.main(symbol=elem, timeframe=timeframe )
                
                if signal == 'long':
                    kl = bot.klines(symbol=elem, limit=1)
                    utils.send(f'🟩Found BUY signal for {elem}\nPrice: '+str(kl.Close.iloc[-1]))
                    
                    th.Thread(target=utils.watcher, args=(elem, 'buy', )).start()

                    #bot.set_mode(elem)
                    
                    sleep(2)
                    #bot.place_order_market(elem, 'buy')

                    sleep(5)

                if signal == 'short':

                    kl = bot.klines(symbol=elem, limit=1)
                    utils.send(f'🟥Found SELL signal for {elem}\nPrice: '+str(kl.Close.iloc[-1]))
                    
                    th.Thread(target=utils.watcher, args=(elem, 'sell', )).start()
                    #bot.set_mode(elem)
                    sleep(2)
                    #bot.place_order_market(elem, 'sell')

                    sleep(5)


    print('Отдых')
    sleep(1200)
