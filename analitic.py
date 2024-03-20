import time

class analitic:
	def __init__(self, bot):
		self.bot = bot


	def calculate_bollinger_bands(symbol, timeframe='1d', period=20, num_std_dev=2):
	    ohlcv = self.bot.klines(symbol, limit=period, timeframe=timeframe)
	    closes = [tick[4] for tick in ohlcv]

	    # Calculate SMA (Simple Moving Average)
	    sma = sum(closes) / period

	    # Calculate standard deviation
	    std_dev = (sum((x - sma) ** 2 for x in closes) / period) ** 0.5

	    # Calculate upper and lower Bollinger Bands
	    upper_band = sma + num_std_dev * std_dev
	    lower_band = sma - num_std_dev * std_dev

	    return upper_band, lower_band








	# Function to calculate RSI for a given symbol
	def calculate_rsi(symbol, timeframe='1d',period=14):
	    ohlcv = self.bot.klines(symbol, limit=period, timeframe=timeframe)
	    closes = [tick[4] for tick in ohlcv]
	    changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]
	    gain = [change if change > 0 else 0 for change in changes]
	    loss = [-change if change < 0 else 0 for change in changes]

	    avg_gain = sum(gain) / period
	    avg_loss = sum(loss) / period

	    if avg_loss == 0:
	        return 100
	    else:
	        rs = avg_gain / avg_loss
	        return 100 - (100 / (1 + rs))

	# Function to calculate EMA for a given symbol
	def calculate_ema(symbol, timeframe='1d', period=100):
	    ohlcv = self.bot.klines(symbol, limit=period, timeframe=timeframe)
	    closes = [tick[4] for tick in ohlcv]

	    # Calculate EMA using the formula: EMA = (close - EMA_prev) * multiplier + EMA_prev
	    multiplier = 2 / (period + 1)
	    ema_values = [closes[0]]
	    for i in range(1, len(closes)):
	        ema = (closes[i] - ema_values[i - 1]) * multiplier + ema_values[i - 1]
	        ema_values.append(ema)

	    return ema_values[-1]

	# Function to calculate Stochastic Oscillator for a given symbol
	def calculate_stochastic(symbol, timeframe='1d', k_period=14, d_period=3):
	    ohlcv = self.bot.klines(symbol, limit=k_period+d_period, timeframe=timeframe)
	    closes = [tick[4] for tick in ohlcv]

	    # Calculate %K
	    lowest_low = min(closes[:k_period])
	    highest_high = max(closes[:k_period])
	    current_close = closes[k_period]
	    percent_k = ((current_close - lowest_low) / (highest_high - lowest_low)) * 100

	    # Calculate %D (simple moving average of %K)
	    percent_d = sum(closes[:d_period]) / d_period

	    return percent_k, percent_d
	def calculate_support_resistance(symbol, timeframe='1d', window=20):
	    ohlcv = self.bot.klines(symbol, timeframe=timeframe)
	    closes = [tick[4] for tick in ohlcv]

	    support_level = min(closes[-window:])
	    resistance_level = max(closes[-window:])

	    return support_level, resistance_level



	def main():
	    rsi = calculate_rsi(symbol)
	    ema = calculate_ema(symbol)
	    percent_k, percent_d = calculate_stochastic(symbol)
	    support_level, resistance_level = calculate_support_resistance(symbol)
	    current_price = self.bot.klines(symbol, limit=1, timeframe='D').Close[-1]
	    upper_band, lower_band = calculate_bollinger_bands(symbol)
	    print(
	        f"{symbol} RSI: {rsi}, EMA: {ema}, Stochastic (%K, %D): {percent_k}, {percent_d}, Current Price: {current_price}")
        # Check for long signal conditions
        if rsi < 70 and rsi >55  and current_price > ema and percent_k > percent_d and current_price > support_level and current_price < upper_band:
	        # Replace 0.001 with your desired quantity
	        return 'up'
	    # Check for short signal conditions
	    elif rsi > 70 and current_price < ema and current_price < resistance_level and current_price > lower_band:
	        # Replace 0.001 with your desired quantity
	        return 'down'
	    


	    except Exception as e:
	        print(f"An error occurred: {str(e)}")
