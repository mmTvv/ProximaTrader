from config import *

from pybit.unified_trading import HTTP
import pandas as pd
from time import sleep

class ByBit:
	def __init__(self):
		self.session = HTTP(
		    api_key=api,
		    api_secret=secret,
		    testnet=False
		)
		
			
	# Getting balance on Bybit Derivatrives Asset (in USDT)
	def get_balance(self):
	    try:
	        resp = self.session.get_wallet_balance(accountType="CONTRACT", coin="USDT")['result']['list'][0]['coin'][0]['walletBalance']
	        resp = float(resp)
	        return resp
	    except Exception as err:
	        print(err)


	# Getting all available symbols from Derivatives market (like 'BTCUSDT', 'XRPUSDT', etc)
	def get_tickers(self):
	    try:
	        resp = self.session.get_tickers(category="linear")['result']['list']
	        symbols = []
	        for elem in resp:
	            if 'USDT' in elem['symbol'] and not 'USDC' in elem['symbol']:
	                symbols.append(elem['symbol'])
	        return symbols
	    except Exception as err:
	        print(err)


	# Klines is the candles of some symbol (up to 1500 candles). Dataframe, last elem has [-1] index
	def klines(self, symbol, limit=500):
	    try:
	        resp = self.session.get_kline(
	            category='linear',
	            symbol=symbol,
	            interval=timeframe,
	            limit=limit
	        )['result']['list']
	        resp = pd.DataFrame(resp)
	        resp.columns = ['Time', 'Open', 'High', 'Low', 'Close', 'Volume', 'Turnover']
	        resp = resp.set_index('Time')
	        resp = resp.astype(float)
	        resp = resp[::-1]
	        return resp
	    except Exception as err:
	        print(err)

	# Getting your current positions. It returns symbols list with opened positions
	def get_positions(self):
	    try:
	        resp = self.session.get_positions(
	            category='linear',
	            settleCoin='USDT'
	        )['result']['list']
	        pos = []
	        for elem in resp:
	            pos.append(elem['symbol'])
	        return pos
	    except Exception as err:
	        print(err)

	# Getting last 50 PnL. I used it to check strategies performance
	def get_pnl(self):
	    try:
	        resp = self.session.get_closed_pnl(category="linear", limit=50)['result']['list']
	        pnl = 0
	        for elem in resp:
	            pnl += float(elem['closedPnl'])
	        return pnl
	    except Exception as err:
	        print(err)

	# Changing mode and leverage: 
	def set_mode(self, symbol):
	    try:
	        resp = self.session.switch_margin_mode(
	            category='linear',
	            symbol=symbol,
	            tradeMode=mode,
	            buyLeverage=leverage,
	            sellLeverage=leverage
	        )
	        print(resp)
	    except Exception as err:
	        print(err)

	# Getting number of decimal digits for price and qty
	def get_precisions(self,symbol):
	    try:
	        resp = self.session.get_instruments_info(
	            category='linear',
	            symbol=symbol
	        )['result']['list'][0]
	        price = resp['priceFilter']['tickSize']
	        if '.' in price:
	            price = len(price.split('.')[1])
	        else:
	            price = 0
	        qty = resp['lotSizeFilter']['qtyStep']
	        if '.' in qty:
	            qty = len(qty.split('.')[1])
	        else:
	            qty = 0

	        return price, qty
	    except Exception as err:
	        print(err)

	# Placing order with Market price. Placing TP and SL as well
	def place_order_market(self,symbol, side):
	    price_precision = self.get_precisions(symbol)[0]
	    qty_precision = self.get_precisions(symbol)[1]
	    mark_price = self.session.get_tickers(
	        category='linear',
	        symbol=symbol
	    )['result']['list'][0]['markPrice']
	    mark_price = float(mark_price)
	    


	    order_qty = round(qty/mark_price, qty_precision)
	    sleep(2)
	    if side == 'buy':
	        try:
	            tp_price = round(mark_price + mark_price * tp, price_precision)
	            sl_price = round(mark_price - mark_price * sl, price_precision)
	            resp = self.session.place_order(
	                category='linear',
	                symbol=symbol,
	                side='Buy',
	                orderType='Market',
	                qty=order_qty,
	                takeProfit=tp_price,
	                stopLoss=sl_price,
	                tpTriggerBy='Market',
	                slTriggerBy='Market'
	            )
	            print(resp)
	            
	        except Exception as err:
	            print(err)

	    if side == 'sell':
	        try:
	            tp_price = round(mark_price - mark_price * tp, price_precision)
	            sl_price = round(mark_price + mark_price * sl, price_precision)
	            resp = self.session.place_order(
	                category='linear',
	                symbol=symbol,
	                side='Sell',
	                orderType='Market',
	                qty=order_qty,
	                takeProfit=tp_price,
	                stopLoss=sl_price,
	                tpTriggerBy='Market',
	                slTriggerBy='Market'
	            )
	            print(resp)
	       
	        except Exception as err:
	            print(err)

	    return {'side': side, 'symbol': symbol, 'price': mark_price}

