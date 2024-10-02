import ta
import pandas as pd

class Strategy:
    def __init__(self, bot, atr_multiplier=1.0, atr_window=14):
        self.bot = bot
        self.atr_multiplier = atr_multiplier  # Множитель для ATR
        self.atr_window = atr_window
        self.rsi_indent = 6

    def rsi(self, data, period=21):
        """ Рассчитывает RSI """
        return ta.momentum.RSIIndicator(close=data['Close'], window=period).rsi()

    def ema(self, data, period=50):
        """ Рассчитывает EMA """
        return ta.trend.EMAIndicator(close=data['Close'], window=period).ema_indicator()

    def chandelier_exit(self, data, window=1, multiplier=1.8):
        """ Рассчитывает Chandelier Exit """
        high, low, close = data['High'], data['Low'], data['Close']
        atr = ta.volatility.AverageTrueRange(high, low, close, window=window).average_true_range()

        long_stop = high.rolling(window=window).max() - atr * multiplier
        short_stop = low.rolling(window=window).min() + atr * multiplier

        # Определение направления тренда
        direction = pd.Series(index=data.index, dtype='int')
        direction.iloc[0] = 1 if close.iloc[0] > short_stop.iloc[0] else -1

        for i in range(1, len(data)):
            if close.iloc[i] > short_stop.iloc[i - 1]:
                direction.iloc[i] = 1  # Лонг тренд
            elif close.iloc[i] < long_stop.iloc[i - 1]:
                direction.iloc[i] = -1  # Шорт тренд
            else:
                direction.iloc[i] = direction.iloc[i - 1]  # Без изменений

        return long_stop, short_stop, direction

    def calculate_atr(self, data, window=14):
        """ Рассчитывает Average True Range (ATR) """
        high, low, close = data['High'], data['Low'], data['Close']
        return ta.volatility.AverageTrueRange(high, low, close, window=window).average_true_range().iloc[-1]

    def calculate_volumes(self, data):
        """ Рассчитывает изменения объёмов для фильтрации сделок """
        volumes = data['Volume']
        return volumes.diff().fillna(0)

    def filter_by_volatility(self, df_data, symbol):
        """ Фильтрует монеты по волатильности """
        current_atr = self.calculate_atr(df_data)
        average_atr = ta.volatility.AverageTrueRange(df_data['High'], df_data['Low'], df_data['Close'], window=self.atr_window).average_true_range().iloc[-self.atr_window:].mean()
        threshold = average_atr * self.atr_multiplier

        if current_atr < threshold:
            print(f'[INFO]: {symbol} отфильтрован из-за низкой волатильности (Current ATR: {current_atr}, Threshold: {threshold})')
            return False
        return True

    def main(self, symbol):
        try:
            # Получение данных
            df_data = self.bot.klines(symbol, timeframe=60, limit=50)
            current_price = df_data['Close'].iloc[-1]

            # Расчёт индикаторов
            rsi_data = self.rsi(df_data)
            ema_data = self.ema(df_data)
            long_stop, short_stop, direction = self.chandelier_exit(df_data)
            atr_data = self.calculate_atr(df_data)
            volume_diff = self.calculate_volumes(df_data)

            # Стратегия на покупку
            if (
                rsi_data.iloc[-1] > rsi_data.iloc[-2] + self.rsi_indent and
                direction.iloc[-1] == 1 and
                current_price > ema_data.iloc[-1] and
                volume_diff.iloc[-1] > 0 and
                current_price > long_stop.iloc[-1] + (long_stop.iloc[-1]/100*5)      
               ):
                return {
                    "side": 'long',
                    'rsi': rsi_data,
                    'price': current_price,
                    'sl': long_stop.iloc[-1]
                }

            # Стратегия на продажу
            elif (
                rsi_data.iloc[-1] < rsi_data.iloc[-2] + self.rsi_indent and
                direction.iloc[-1] == -1 and
                current_price < ema_data.iloc[-1] and
                volume_diff.iloc[-1] > 0 and
                current_price < long_stop.iloc[-1] - (long_stop.iloc[-1]/100*5)
            ):
                return {
                    "side": 'short',
                    'rsi': rsi_data.iloc[-1],
                    'price': current_price,
                    'sl': short_stop.iloc[-1]
                }

            # Нет сигнала
            return {"side": "none", "price": current_price}

        except Exception as err:
            print(f'[ERROR]: {symbol} skipped due to {err}')
            return {"side": "none", "price": None}
