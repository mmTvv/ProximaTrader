import ta, time
import pandas as pd
import traceback
import numpy as np

import pandas as pd
import numpy as np

def chandelier_exit(df, atr_period=1, atr_multiplier=1.85, use_close=True, await_bar_confirmation=True):
    """
    Chandelier Exit strategy in Python
    :param df: DataFrame with columns ['open', 'high', 'low', 'close']
    :param atr_period: ATR period
    :param atr_multiplier: Multiplier for ATR to calculate stop levels
    :param use_close: If True, use close price for extremum calculation
    :param await_bar_confirmation: If True, waits for bar confirmation
    :return: DataFrame with 'long_stop', 'short_stop', 'buy_signal', 'sell_signal' columns
    """
    high, low, close = df['High'], df['Low'], df['Close']
    
    # Calculate True Range and ATR as Pandas Series
    tr = pd.Series(np.maximum.reduce([high - low, abs(high - close.shift(1)), abs(low - close.shift(1))]), index=df.index)
    atr = atr_multiplier * tr.rolling(window=atr_period).mean()

    # Calculate long and short stops
    if use_close:
        long_stop = close.rolling(window=atr_period).max() - atr
        short_stop = close.rolling(window=atr_period).min() + atr
    else:
        long_stop = high.rolling(window=atr_period).max() - atr
        short_stop = low.rolling(window=atr_period).min() + atr

    # Adjust stop levels based on the previous bar's close
    long_stop_prev = long_stop.shift(1)
    long_stop = np.where(close.shift(1) > long_stop_prev, np.maximum(long_stop, long_stop_prev), long_stop)

    short_stop_prev = short_stop.shift(1)
    short_stop = np.where(close.shift(1) < short_stop_prev, np.minimum(short_stop, short_stop_prev), short_stop)

    # Determine direction (1 for long, -1 for short)
    dir_ = np.where(close > short_stop_prev, 1, np.where(close < long_stop_prev, -1, np.nan))
    dir_ = pd.Series(dir_, index=df.index).ffill().fillna(1).astype(int)

    # Generate buy and sell signals
    buy_signal = (dir_ == 1) & (dir_.shift(1) == -1)
    sell_signal = (dir_ == -1) & (dir_.shift(1) == 1)

    # Prepare the result
    result = pd.DataFrame({
        'long_stop': long_stop,
        'short_stop': short_stop,
        'buy_signal': buy_signal,
        'sell_signal': sell_signal,
        'direction': dir_
    })

    if await_bar_confirmation:
        result['buy_signal'] &= df['Close'] == df['Close']  # placeholder for bar confirmation
        result['sell_signal'] &= df['Close'] == df['Close']  # placeholder for bar confirmation

    return result


# Основная функция для принятия торговых решений
def CE(df, symbol, window=-1):
    chandelier = chandelier_exit(df)

    # Проверка и исполнение торговых сигналов
    if chandelier['buy_signal'].iloc[window]:
        #print(f'{symbol} {chandelier.iloc[-1]}')
        return {
                'side': 'buy',
                'ce_direction': chandelier['direction'].iloc[window]
            }
    elif chandelier['sell_signal'].iloc[window]:
        #print(f'{symbol} {chandelier.iloc[-1]}')
        return {
                'side': 'sell',
                'ce_direction': chandelier['direction'].iloc[window]
            }
    else:
        return {
                'side': 'none',
                'ce_direction': chandelier['direction'].iloc[window]
            }

def calculate_williams_r(df, length=21):
    high = df['High'].rolling(window=length).max()
    low = df['Low'].rolling(window=length).min()
    williams_r = -100 * (high - df['Close']) / (high - low)
    return williams_r

# Функция расчета EMA от Williams %R
def calculate_ema(series, length=13):
    return series.ewm(span=length, adjust=False).mean()

# Проверка условий перекупленности и перепроданности
def check_conditions(williams_r, ema, window):
    overbought = ema.iloc[window] > -20
    oversold = ema.iloc[window] < -80
    return overbought, oversold

# Основная функция для принятия торговых решений
def WILLAMS_R(df, symbol, williams_r_length=21, ema_length=13):
    try:
        williams_r = calculate_williams_r(df, williams_r_length)
        ema = calculate_ema(williams_r, ema_length)

        if len(ema) < 3 or len(williams_r) < 3:
            return {
                'side': 'none',
                'overbought': [None],
                'oversold': [None]
            }

        overbought_1, oversold_1 = check_conditions(williams_r, ema, -1)
        overbought_2, oversold_2 = check_conditions(williams_r, ema, -2)
        overbought_3, oversold_3 = check_conditions(williams_r, ema, -3)

        #print(f'{overbought_1} - {oversold_1} : {overbought_2} - {oversold_2} : {overbought_3} - {oversold_3}')
        if (overbought_1 == False and overbought_2 == True and overbought_3 == True) or (overbought_1 == False and overbought_2 == False and overbought_3 == True):
            return {
                'side': 'sell',
                'overbought': [overbought_1],
                'oversold': [oversold_1],
                }
        elif (oversold_1 == False and oversold_2 == True and oversold_3 == True) or (oversold_1 == False and oversold_2 == False and oversold_3 == True):
            return {
                'side': 'buy',
                'overbought': [overbought_1],
                'oversold': [oversold_1]
                }
        else:
            return {
                'side': 'none', 
                'overbought': [overbought_1],
                'oversold': [oversold_1]
                }
    except:
        print(f'Error {symbol} as {e}')
        return trading_decision(symbol)

class Strategy:
    def __init__(self, bot):
        self.bot = bot

    
    def main(self, symbol):
        """ Анализируем """
        try:
            df_hours = self.bot.klines(symbol, 60, 50)
            df = self.bot.klines(symbol, 'D', 50)
            if len(df) < 25:
                return {
                    "side": "none", 
                    "price": current_price,
                    "direction": chandelier_1['ce_direction']
                }
            williams = WILLAMS_R(df, symbol)
            chandelier_1 = CE(df, symbol, -1)
            chandelier_2 = CE(df, symbol, -2)
            chandelier_hours = CE(df_hours, symbol, -1)
            current_price = df['Close'].iloc[-1]
            #print(f'{symbol} {chandelier} {williams}')
            #print(f"{symbol}  {williams['side'] == 'buy'}  {chandelier_2['side'] == 'buy'}  {chandelier_1['ce_direction'] == 1}")
            #print(f"{symbol}  {williams['side'] == 'sell'}  {chandelier_2['side'] == 'sell'}  {chandelier_1['ce_direction'] == -1}\n\n")
            if williams['side'] == 'buy' and chandelier_2['side'] == 'buy' and chandelier_1['ce_direction'] == 1 and chandelier_hours['ce_direction'] == 1:
                
                return {
                    "side": "long",
                    "price": current_price,
                    "direction": chandelier_1['ce_direction']
                }

            # Вход в шорт, если сигналы на всех таймфреймах совпадают
            elif williams['side'] == 'sell' and chandelier_2['side'] == 'sell' and chandelier_1['ce_direction'] == -1 and chandelier_hours['ce_direction'] == -1:
                
                return {
                    "side": "short",
                    "price": current_price,
                    "direction": chandelier_1['ce_direction']
                }

            # Нет сигнала
            return {
                    "side": "none", 
                    "price": current_price,
                    "direction": chandelier_1['ce_direction']
                }

        except Exception as err:
            print(f'[ERROR]: {symbol} skipped due to {traceback.print_exc()}')
            time.sleep(60)
            return {"side": "none", "price": None}
