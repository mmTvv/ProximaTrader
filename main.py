from config import *
import utils
import bybit
import pandas as pd

bot = bybit.ByBit()
utils = utils.Utils(bot)

symbols = bot.get_tickers()     # getting all symbols from the Bybit Derivatives

print(f'Your balance: {bot.get_balance()} USDT')

while True:
    balance = bot.get_balance()

    if balance == None:
        print('Cant connect to API')

    if balance != None and float(balance) > qty/leverage:

        balance = float(balance)
        print(f'Balance: {balance}')

        pos = bot.get_positions()
        print(f'You have {len(pos)} positions: {pos}')

        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for elem in symbols:
                pos = bot.get_positions()
                if len(pos) >= max_pos and elem in pos:
                    break

                # Signal to buy or sell
                signal = williamsR(elem)

                if signal == 'up':
                    print(f'Found BUY signal for {elem}')
                    set_mode(elem)
                    sleep(2)
                    #place_order_market(elem, 'buy')
                    bot.send_message(channel_id, elem + ' - buy')
                    sleep(5)

                if signal == 'down':
                    print(f'Found SELL signal for {elem}')
                    set_mode(elem)
                    sleep(2)
                    #place_order_market(elem, 'sell')
                    
                    sleep(5)


    print('Waiting 2 mins')
    sleep(120)
