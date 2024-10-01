import ccxt
import pandas as pd

# Fetch historical data
symbol = 'BTC/USDT'
timeframe = '1d'
binance = ccxt.binance()
ohlcv = binance.fetch_ohlcv(symbol, timeframe)
data = pd.DataFrame(ohlcv, columns=['Timestamp', 'Open', 'High', 'Low', 'Close', 'Volume'])
data['Timestamp'] = pd.to_datetime(data['Timestamp'], unit='ms').dt.tz_localize('UTC').dt.tz_convert('Asia/Bangkok')
data.set_index('Timestamp', inplace=True)

# Calculate EMAs
data['EMA_12'] = data['Close'].ewm(span=12, adjust=False).mean()
data['EMA_26'] = data['Close'].ewm(span=26, adjust=False).mean()

# Detect crossups and cross downs
def detect_cross(data, short_ema, long_ema):
    """
    Detects crossups and cross downs between two EMAs.

    Parameters:
    data (pandas.DataFrame): The input data.
    short_ema (str): The short EMA column name.
    long_ema (str): The long EMA column name.

    Returns:
    pandas.Series: A boolean series indicating the crossups and cross downs.
    """
    cross = pd.Series(index=data.index)
    cross[(short_ema > long_ema) & (cross.shift() != (short_ema > long_ema))] = 1
    cross[(short_ema < long_ema) & (cross.shift() != (short_ema < long_ema))] = -1
    cross.ffill(inplace=True)
    return cross

data['Cross'] = detect_cross(data, 'EMA_12', 'EMA_26')

# Generate buy and sell signals
def generate_signals(data, cross_column):
    """
    Generates buy and sell signals based on the crossups and cross downs.

    Parameters:
    data (pandas.DataFrame): The input data.
    cross_column (str): The cross column name.

    Returns:
    pandas.Series: A boolean series indicating the buy and sell signals.
    """
    signals = pd.Series(index=data.index)
    signals[cross_column == 1] = True
    signals[cross_column == -1] = False
    return signals

signals = generate_signals(data, data['Cross'])

# Set start and end dates
start_date = '2022-01-01'
end_date = '2022-02-01'
data = data[start_date:end_date]

# Initialize total revenue and remaining capital
total_revenue = 0
remaining_capital = 10000

# Initialize buy and sell dataframes
buy_data = pd.DataFrame(columns=['Date', 'Price'])
sell_data = pd.DataFrame(columns=['Date', 'Price'])

# Iterate over the signals and execute trades
for i in range(1, len(signals)):
    if signals.iloc[i] and not signals.iloc[i-1]:
        # Execute a buy trade
        buy_price = data.iloc[i]['Close']
        buy_data = buy_data.append({'Date': data.index[i], 'Price': buy_price}, ignore_index=True)
        remaining_capital -= remaining_capital * (buy_price / 10000)
    elif not signals.iloc[i] and signals.iloc[i-1]:
        # Execute asell trade
        sell_price = data.iloc[i]['Close']
        sell_data = sell_data.append({'Date': data.index[i], 'Price': sell_price}, ignore_index=True)
        total_revenue += remaining_capital * ((sell_price / 10000) - (buy_price / 10000))
        remaining_capital = remaining_capital * (sell_price / 10000)

# Print the results
print(f'Start date: {start_date}')
print(f'End date: {end_date}')
print(f'Total revenue: {total_revenue:.2f}%')
print(f'Remaining capital: {remaining_capital:.2f}')
print(f'Buy dates and prices:')
print(buy_data)
print(f'Sell dates and prices:')
print(sell_data)