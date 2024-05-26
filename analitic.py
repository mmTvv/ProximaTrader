import time, ta
from time import sleep
class analitic:
	def __init__(self, bot):
		self.bot = bot

	def rsi(self, data, period = 14):
		rsi = ta.momentum.RSIIndicator(close = data['Close'], window = period).rsi()
		return rsi

	def main(self, symbol):
		try:
			df_data_240 = self.bot.klines(symbol, timeframe = 240, limit = 28)
			df_data_60 = self.bot.klines(symbol, timeframe = 60, limit = 28)
			current_price = self.bot.klines(symbol, timeframe = timeframe, limit = 1)['Close'].iloc[-1]
			rsi_data_240 = self.rsi(df_data_240)
			rsi_data_60 = self.rsi(df_data_60)
			if rsi_data_240.iloc[-2] > 70 and rsi_data_240.iloc[-3] < 70 and rsi_data_240.iloc[-1] > rsi_data_240.iloc[-2] and rsi_data_60.iloc[-1] > 70:
				# Replace 0.001 with your desired quantity
				print(f'{symbol} - {rsi_data.iloc[-1]}')
				return {"side":'long', "price": current_price}
			# Check for short signal conditions
			elif rsi_data.iloc[-1]> 100:
				# Replace 0.001 with your desired quantity

				return {"side": "short", "price": current_price}

			else:
				return {"side": "none", "price": current_price}
		except Exception as err:
			pass
			#print(f'[ERROR]: {symbol} skipped {err}')