from config import *
import utils
import bybit
import pandas as pd
import ta
from time import sleep


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
        #print(f'Balance: {balance}')

        pos = bot.get_positions()
        #print(f'You have {len(pos)} positions: {pos}')

        if len(pos) < max_pos:

            # Checking every symbol from the symbols list:
            for elem in symbols:
                pos = bot.get_positions()
                if len(pos) >= max_pos and elem in pos:
                    break

                # Signal to buy or sell
                signal = utils.RES(elem, 60)
                
                if signal == 'up':
                    kl = bot.klines(elem, 201)
                    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
                    ema = ta.trend.ema_indicator(kl.Close, window=200)
                    utils.send(f'🟩Found BUY signal for `{elem}`\nPrice: '+str(kl.Close.iloc[-1])+'\nRSI: '+str(rsi.iloc[-1])+'\nEMA-200: '+str(ema.iloc[-1])+'\nVolume: '+str(kl.Volume.iloc[-1]))
                    #set_mode(elem)
                    
                    sleep(2)
                    #place_order_market(elem, 'buy')

                    sleep(5)

                if signal == 'down':
                    kl = bot.klines(elem, 201)
                    rsi = ta.momentum.RSIIndicator(kl.Close).rsi()
                    ema = ta.trend.ema_indicator(kl.Close, window=200)
                    utils.send(f'🟥Found SELL signal for `{elem}`\nPrice: '+str(kl.Close.iloc[-1])+'\nRSI: '+str(rsi.iloc[-1])+'\nEMA-200: '+str(ema.iloc[-1])+'\nVolume: '+str(kl.Volume.iloc[-1]))
                    #set_mode(elem)
                    sleep(2)
                    #place_order_market(elem, 'sell')
                    
                    sleep(5)


    print('Waiting 2 mins')
    sleep(120)
