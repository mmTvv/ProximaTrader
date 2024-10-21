import ta
import pandas as pd
import traceback

class Strategy:
    def __init__(self, bot):
        self.bot = bot

    def order_blocks(self, data):
        """ Определяем ордер-блоки (зоны, где умные деньги входили в рынок) на старшем таймфрейме """
        high_volumes = data['Volume'].rolling(window=20).max()
        order_block_zones = data.loc[data['Volume'] == high_volumes, ['High', 'Low']]
        return order_block_zones

    def bos(self, data):
        """ Определяем Break of Structure (пробой структуры) """
        highs = data['High'].rolling(window=20).max()
        lows = data['Low'].rolling(window=20).min()
        bos_signal = (data['Close'] > highs) | (data['Close'] < lows)
        return bos_signal

    def liquidity_zones(self, data):
        """ Определяем зоны ликвидности """
        liquidity_grabs = data['Low'].rolling(window=5).min() # Пример: минимумы могут указывать на захваты ликвидности
        return liquidity_grabs

    def main(self, symbol):
        """ Анализируем несколько таймфреймов: дневной, 4 часа и 15 минут """
        try:
            # Получаем данные с разных таймфреймов
            daily_data = self.bot.klines(symbol, timeframe='D', limit=200)
            h4_data = self.bot.klines(symbol, timeframe='240', limit=200)
            m15_data = self.bot.klines(symbol, timeframe='15', limit=200)
            if daily_data is None or daily_data.empty or h4_data is None or h4_data.empty or m15_data is None or m15_data.empty:
                raise ValueError(f"No data received for {symbol}")
            # Анализируем ордер-блоки и пробои структуры на дневном графике
            daily_order_blocks = self.order_blocks(daily_data)
            daily_bos_signal = self.bos(daily_data)

            # Анализируем средний таймфрейм (4 часа)
            h4_order_blocks = self.order_blocks(h4_data)
            h4_bos_signal = self.bos(h4_data)

            # Анализируем мелкий таймфрейм (15 минут)
            m15_liquidity_zones = self.liquidity_zones(m15_data)
            m15_bos_signal = self.bos(m15_data)

            current_price = m15_data['Close'].iloc[-1]

            # Вход в лонг, если сигналы на всех таймфреймах совпадают
            if daily_bos_signal.iloc[-1] and h4_bos_signal.iloc[-1] and m15_bos_signal.iloc[-1]:
                return {
                    "side": 'long',
                    'price': current_price,
                    'sl': m15_liquidity_zones.iloc[-1],  # Стоп-лосс на уровне ликвидности
                    'tp': current_price + (current_price / 100)  # Тейк-профит
                }

            # Вход в шорт, если сигналы на всех таймфреймах совпадают
            elif not daily_bos_signal.iloc[-1] and not h4_bos_signal.iloc[-1] and not m15_bos_signal.iloc[-1]:
                return {
                    "side": 'short',
                    'price': current_price,
                    'sl': m15_liquidity_zones.iloc[-1],  # Стоп-лосс за зоной ликвидности
                    'tp': current_price - (current_price / 100)  # Тейк-профит
                }

            # Нет сигнала
            return {"side": "none", "price": current_price}

        except Exception as err:
            print(f'[ERROR]: {symbol} skipped due to {traceback.print_exc()}')
            return {"side": "none", "price": None}
