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

    if balance != None: #and float(balance) > qty/leverage:

        balance = float(balance)
        pos = bot.get_positions()
        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for symbol in symbols:
                pos = bot.get_positions()
                if len(pos) >= max_pos and symbol in utils.poss:
                    break

                # Signal to buy or sell
                signal = analitic.main(symbol=symbol, timeframe=timeframe )
                
                if signal == 'long':
                    utils.poss.append(symbol)
                    kl = bot.klines(symbol=symbol, limit=1)
                    utils.send(f'🟩Found BUY signal fr #{symbol}\nPrice: '+str(kl.Close.iloc[-1])+'\nPOS count: '+str(utils.pos) +'\nPOS closed: '+str(utils.closed))
                    
                    th.Thread(target=utils.watcher, args=(symbol, 'buy', )).start()

                    #bot.set_mode(symbol)
                    
                    #sleep(2)
                    #bot.place_order_market(symbol, 'buy')

                    sleep(5)

                if signal == 'short':
                    utils.poss.append(symbol)

                    kl = bot.klines(symbol=symbol, limit=1)
                    utils.send(f'🟥Found SELL signal or #{symbol}\nPrice: '+str(kl.Close.iloc[-1])+'\nPOS count: '+str(utils.pos) +'\nPOS closed: '+str(utils.closed))
                    
                    th.Thread(target=utils.watcher, args=(symbol, 'sell', )).start()
                    #bot.set_mode(symbol)
                    #sleep(2)
                    #bot.place_order_market(symbol, 'sell')

                    sleep(5)


    print('Отдых')
    sleep(60*60*4)
