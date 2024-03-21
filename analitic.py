import time, ta

class analitic:
	def __init__(self, bot):
		self.bot = bot


	def main(self, symbol, timeframe):
		try:
			df = self.bot.klines(symbol, timeframe, limit =20)
			rsi = ta.momentum.RSIIndicator(df.Close).rsi()

			if rsi.iloc[-1] < 70 and rsi.iloc[-1] >55 and rsi.iloc[-3] < 50:
				# Replace 0.001 with your desired quantity
				return 'up'
			# Check for short signal conditions
			elif rsi.iloc[-1] > 70:
				# Replace 0.001 with your desired quantity
				#return 'down'
				pass
		except Exception as err:
			print('ERROR: ' + err)