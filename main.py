from config import *
import utils
import bybit
import pandas as pd
import ta
from time import sleep
import threading as th
from analitic import Strategy
import sys
import time 
from pprint import pprint
bot = bybit.ByBit()
utils = utils.Utils(bot)
analitic = Strategy(bot)

blacklist = {
             'long': [],
            'short': []
            }

symbols = bot.get_tickers()
balance = bot.get_balance()

def check(symbol, side):
    time.sleep(15*60)
    data = analitic.main(symbol=symbol)
    while data['side'] == side:
        data = analitic.main(symbol=symbol)
        time.sleep(15*60)
    blacklist[side].remove(symbol)

if balance == None:
    print('Cant connect to API')
    sys.exit(1)
print(f'[INFO] Your balance: {balance} USDT')

for symbol in symbols:
    data = analitic.main(symbol=symbol)
    if data['side'] == 'long':
        blacklist['long'].append(symbol)
        th.Thread(target=check, args=(symbol, data['side'])).start()

    elif data['side'] == 'short':
        blacklist['short'].append(symbol)
        th.Thread(target=check, args=(symbol, data['side'])).start()

pprint(blacklist)
while True:
    if balance != None: #and float(balance) > qty/leverage:

        balance = float(balance)
        pos = bot.get_positions()
        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for symbol in symbols:
                if symbol not in utils.poss and symbol not in blacklist['long'] and symbol not in blacklist['short']:
                    try:
                        pos = bot.get_positions()
                        
                        data = analitic.main(symbol=symbol)
                        
                        if data['side'] == 'long':
                            utils.poss.append(symbol)
                            print(f'[+] {symbol}: long')
                            th.Thread(target=utils.watcher, args=(symbol, 'buy', data['price'],)).start()
                            utils.draw(symbol=symbol, text=f'<b>[+] LONG</b> <code>{symbol}</code>\n<b>price</b> <code>{round(data["price"], 7)}</code>\n<b>sl</b> <code>{round(data["sl"],7)}</code>', price1=data["price"])
                            #bot.set_mode(symbol)
                            #sleep(2)
                            #bot.place_order_market(symbol, 'buy')

                            sleep(5)

                        if data['side'] == 'short':
                            utils.poss.append(symbol)

                            th.Thread(target=utils.watcher, args=(symbol, 'sell', data['price'])).start()
                            utils.draw(symbol=symbol, text=f'<b>[+] SHORT</b> <code>{symbol}</code>\n<b>price</b> <code>{round(data["price"], 7)}</code>\n<b>sl</b> <code>{round(data["sl"],7)}</code>', price1=data["price"])
                            #bot.set_mode(symbol)
                            #sleep(2)
                            #bot.place_order_market(symbol, 'sell')

                            sleep(5)

                        if data['side'] == "none" or data['side'] == 'err':
                            pass
                            
                    except Exception as e:
                        utils.send(f'ERROR: {e}')



    #print(f'🟩 BUY - {utils.poss} norders: '+str(utils.closed)+'/'+str(utils.pos))
    #utils.send(f'SLEEP : 15 MIN\n🟩 BUY - {utils.poss} \norders: '+str(utils.closed)+'/'+str(utils.pos))
    #print('\n---------------\nStart sleep: 900\n---------------\n')
    sleep(15*60)
