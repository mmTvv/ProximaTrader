import time, ta
from config import *
from time import sleep
class analitic:
	def __init__(self, bot):
		self.bot = bot

	def rsi(self, data, period = 14);
		rsi = ta.momentum.RSIIndicator(close = data['Close'], window = period)
		return rsi

	def main(self, symbol, timeframe):
		try:
			df_data = self.bot.klines(symbol, timeframe = timeframe, limit = 28)
			rsi_data = self.rsi(df_data)

			if rsi_data.iloc[-1] > 70 and rsi_data.iloc[-3] < 60:
				# Replace 0.001 with your desired quantity

				return {"side":'long', "price": current_price}
			# Check for short signal conditions
			elif rsi_data.iloc[-1]:
				# Replace 0.001 with your desired quantity

				return {"side": "short", "price": current_price}

			else:
				return {"side": "none", "price": current_price}
		except Exception as err:
			pass
			#print(f'[ERROR]: {symbol} skipped {err}')

	
