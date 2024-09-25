import ta
from time import sleep

class analitic:
    def __init__(self, bot):
        self.bot = bot

    def rsi(self, data, period=14):
        """ Рассчитывает RSI """
        rsi = ta.momentum.RSIIndicator(close=data['Close'], window=period).rsi()
        return rsi

    def chandelier_exit(self, data, window=1, multiplier=1.8):
        """ Рассчитывает Chandelier Exit """
        high = data['High']
        low = data['Low']
        close = data['Close']
        atr = ta.volatility.AverageTrueRange(high, low, close, window=window).average_true_range()
        chandelier_exit = high.rolling(window=window).max() - atr * multiplier
        return chandelier_exit

    def main(self, symbol):
        try:
            # Получение данных на часовом таймфрейме
            df_data_60 = self.bot.klines(symbol, timeframe=60, limit=28)
            current_price = df_data_60['Close'].iloc[-1]

            # Рассчет RSI и Chandelier Exit на часовом таймфрейме
            rsi_data_60 = self.rsi(df_data_60)
            chandelier_exit_60 = self.chandelier_exit(df_data_60)

            # Фильтрация: Отсеиваем монеты с уже высоким RSI (например, RSI выше 80 для long)
            if rsi_data_60.iloc[-1] > 80:
                return {"side": "none", "price": current_price}

            # Стратегия: сигнал на покупку
            # Условие - RSI только что пересек 70 снизу и цена выше Chandelier Exit
            if rsi_data_60.iloc[-2] < 70 and rsi_data_60.iloc[-1] > 70 and current_price > chandelier_exit_60.iloc[-1]:
                print(f'{symbol} - RSI: {rsi_data_60.iloc[-1]}, Chandelier Exit: {chandelier_exit_60.iloc[-1]}')
                return {"side": 'long', "price": current_price}

            # Стратегия: сигнал на продажу
            # Условие - RSI только что пересек 30 сверху и цена ниже Chandelier Exit
            elif rsi_data_60.iloc[-2] > 30 and rsi_data_60.iloc[-1] < 30 and current_price < chandelier_exit_60.iloc[-1]:
                print(f'{symbol} - RSI: {rsi_data_60.iloc[-1]}, Chandelier Exit: {chandelier_exit_60.iloc[-1]}')
                return {"side": 'short', "price": current_price}

            # Если нет сигнала
            else:
                return {"side": "none", "price": current_price}

        except Exception as err:
            pass
            # Можно добавить логирование ошибки для отладки
            # print(f'[ERROR]: {symbol} skipped {err}')
