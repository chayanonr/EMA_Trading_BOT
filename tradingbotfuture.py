import ccxt
import pandas as pd
import numpy as np

# Initialize the Binance exchange
exchange = ccxt.binance({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
})

# Set trading pair and timeframe
symbol = 'BTC/USDT'
timeframe = '1h'

# Fetch historical price data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe)
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

# Calculate EMA12 and EMA26
df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()
df['EMA26'] = df['close'].ewm(span=26, adjust=False).mean()

# Implement Buy/Sell Signals
df['buy_long_signal'] = (df['EMA12'] > df['EMA26']) & (df['EMA12'].shift(1) <= df['EMA26'].shift(1))
df['buy_short_signal'] = (df['EMA12'] < df['EMA26']) & (df['EMA12'].shift(1) >= df['EMA26'].shift(1))

# Initialize variables
btc_balance = 0
balance = 10  # Initial balance in USDT
total_asset = balance

# Live trading loop
for i, row in df.iterrows():
    if row['buy_long_signal']:
        # Buy long
        order = exchange.create_market_buy_order(symbol, amount=0.7 * balance / row['close'])
        balance -= order['cost']

    elif row['buy_short_signal']:
        # Sell short
        order = exchange.create_market_sell_order(symbol, amount=0.7 * balance / row['close'])
        balance += order['cost']

    # Calculate total asset
    total_asset = balance + btc_balance * row['close']

    print(f"Timestamp: {row['timestamp']} - Close Price: {row['close']} - Total Asset: {total_asset}")
