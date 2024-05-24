from config import *
import utils
import bybit
import pandas as pd
import ta
from time import sleep
import threading as th
from analitic import analitic
import sys

bot = bybit.ByBit()
utils = utils.Utils(bot)
analitic = analitic(bot)

symbols = bot.get_tickers()
balance = bot.get_balance()

if balance == None:
    print('Cant connect to API')
    sys.exit(1)
print(f'[INFO] Your balance: {balance} USDT')

while True:
    if balance != None: #and float(balance) > qty/leverage:

        balance = float(balance)
        pos = bot.get_positions()
        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for symbol in symbols:
                try:
                    pos = bot.get_positions()
                    
                    data = analitic.main(symbol=symbol, timeframe=timeframe )

                    if data['side'] == 'long' and symbol not in utils.start and symbol not in utils.poss:
                        utils.poss.append(symbol)
                        
                        th.Thread(target=utils.watcher, args=(symbol, 'buy', data['price'],)).start()

                        #bot.set_mode(symbol)
                        #sleep(2)
                        #bot.place_order_market(symbol, 'buy')

                        sleep(5)

                    if data['side'] == 'short' and symbol not in utils.start and symbol not in utils.poss:
                        utils.poss.append(symbol)
                        sells.append(symbol)

                        th.Thread(target=utils.watcher, args=(symbol, 'sell', data['price'])).start()

                        #bot.set_mode(symbol)
                        #sleep(2)
                        #bot.place_order_market(symbol, 'sell')

                        sleep(5)

                    if data['side'] == "none" or data['side'] == 'err':
                        if symbol in utils.start:
                            pass
                except:
                    pass
<<<<<<< HEAD


    print(f'🟩 BUY - {utils.poss} norders: '+str(utils.closed)+'/'+str(utils.pos))
    utils.send(f'SLEEP : 15 MIN\n🟩 BUY - {utils.poss} \norders: '+str(utils.closed)+'/'+str(utils.pos))
=======
    print(f'SLEEP : 15 MIN\n🟩 BUY - {buys} \n🟥 SELL - {sells}\norders: '+str(utils.closed)+'/'+str(utils.pos))
    utils.send(f'SLEEP : 15 MIN\n🟩 BUY - {buys} \n🟥 SELL - {sells}\norders: '+str(utils.closed)+'/'+str(utils.pos))
>>>>>>> 5bf9288053003e5fbf6c4ce8e08a3368e37ac1f8
    print('\n---------------\nStart sleep: 900\n---------------\n')
    sleep(15*20)
