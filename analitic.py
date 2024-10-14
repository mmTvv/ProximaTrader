import ta
import pandas as pd

class Strategy:
    def __init__(self, bot):
        self.bot = bot

    def atr(self, data, period=1):
        """ Рассчитывает ATR """
        high, low, close = data['High'], data['Low'], data['Close']
        return ta.volatility.AverageTrueRange(high, low, close, window=period).average_true_range()

    def chandelier_exit(self, data, atr_multiplier=1.8):
        """ Рассчитывает уровни Chandelier Exit для длинных и коротких позиций """
        atr = self.atr(data)
        chandelier_long = data['High'].rolling(window=22).max() - atr_multiplier * atr
        chandelier_short = data['Low'].rolling(window=22).min() + atr_multiplier * atr
        return chandelier_long, chandelier_short

    def ema(self, data, period):
        """ Рассчитывает EMA """
        return ta.trend.EMAIndicator(close=data['Close'], window=period).ema_indicator()

    def rsi(self, data, period=14):
        return ta.momentum.RSIIndicator(data['Close'], period).rsi()
        
    def get_volume(self, data):
        """ Получает объём торгов """
        return data['Volume']

    def main(self, symbol):
        try:
            # Получение данных
            df_data = self.bot.klines(symbol, timeframe=60, limit=200)

            # Форматирование в Hiken Ashi
            df_data = self.bot.heikinashi(df_data)

            current_price = df_data['Close'].iloc[-1]

            # Расчёт индикаторов
            chandelier_long, chandelier_short = self.chandelier_exit(df_data)
            ema_200 = self.ema(df_data, 100)
            atr_value = self.atr(df_data).iloc[-1]
            volume = self.get_volume(df_data)
            rsi = self.rsi(df_data)

            # Условия для входа в лонг (стратегия)
            if (
                current_price+(current_price/10) > chandelier_long.iloc[-1]  # Цена выше уровня Chandelier Long
                and current_price > chandelier_long.iloc[-2]
                and current_price > ema_200.iloc[-1]  # Цена выше EMA 200
                and volume.iloc[-1] * 2 > volume.iloc[-2]  # Увеличение объёма
                and rsi.iloc[-1] > rsi.iloc[-2] +1 > rsi.iloc[-3] +2> rsi.iloc[-4] +3
            ):
                # Расчёт стоп-лосса и тейк-профита
                sl = current_price - 0.015 * current_price  # Стоп-лосс на уровне Chandelier Long
                tp = chandelier_short.iloc[-1]  # Тейк-профит на 1%

                return {
                    "side": 'long',
                    'price': current_price,
                    'sl': sl,
                    'tp': 100000
                }

            # Условия для входа в шорт (стратегия)
            elif (
                current_price - (current_price/10) < chandelier_short.iloc[-1]  # Цена ниже уровня Chandelier Short
                and current_price < chandelier_short.iloc[-2]
                and current_price < ema_200.iloc[-1]  # Цена ниже EMA 200
                and volume.iloc[-1] * 2 > volume.iloc[-2]  # Увеличение объёма
                and rsi.iloc[-4] > rsi.iloc[-3] +1 > rsi.iloc[-2] +2 > rsi.iloc[-1] +3
            ):
                # Расчёт стоп-лосса и тейк-профита
                sl = current_price - 0.015 * current_price  # Стоп-лосс на уровне Chandelier Short
                tp = chandelier_long.iloc[-1]  # Тейк-профит на 1%

                return {
                    "side": 'short',
                    'price': current_price,
                    'sl': sl,
                    'tp': 100000
                }

            # Нет сигнала
            return {"side": "none", "price": current_price}

        except Exception as err:
            print(f'[ERROR]: {symbol} skipped due to {err}')
            return {"side": "none", "price": None}
