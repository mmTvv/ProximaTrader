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

print(f'[INFO] Your balance: {bot.get_balance()} USDT')

print('[INFO] Start initialazing...')
print('[INFO] Init: ', end = ' ')
for symbol in symbols:
    try:
        signal = analitic.main(symbol=symbol, timeframe=timeframe )
        if signal['side'] == 'long' or signal['side'] == 'short':
            utils.start.append(symbol)
            
        if signal['side'] == 'err':
            symbols.remove(symbol)
    except:
        pass
print(utils.poss)
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
                try:
                    pos = bot.get_positions()
                    
                    data = analitic.main(symbol=symbol, timeframe=timeframe )

                    if data['side'] == 'long' and symbol not in utils.start and symbol not in utils.poss:
                        utils.poss.append(symbol)
                        utils.send(f'🟩 BUY - #{symbol}\nprice: '+str(data['price'])+'\norders: '+str(utils.closed)+'/'+str(utils.pos))
                        
                        th.Thread(target=utils.watcher, args=(symbol, 'buy', data['price'],)).start()

                        #bot.set_mode(symbol)
                        
                        #sleep(2)
                        #bot.place_order_market(symbol, 'buy')

                        sleep(5)

                    if data['side'] == 'short' and symbol not in utils.start and symbol not in utils.poss:
                        utils.poss.append(symbol)

                        utils.send(f'🟥 SELL - #{symbol}\nprice: '+str(data['price'])+'\norders: '+str(utils.closed)+'/'+str(utils.pos))
                        
                        th.Thread(target=utils.watcher, args=(symbol, 'sell', data['price'])).start()
                        #bot.set_mode(symbol)
                        #sleep(2)
                        #bot.place_order_market(symbol, 'sell')

                        sleep(5)

                    if data['side'] == "none" or data['side'] == 'err':
                        if symbol in utils.poss:
                            utils.poss.remove(symbol)
                except:
                    pass

    print('\n---------------\nStart sleep: 60\n---------------\n')
    sleep(60)
