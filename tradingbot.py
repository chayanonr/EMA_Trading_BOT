import ccxt
import pandas as pd
import pytz

# Set up the Binance exchange
exchange = ccxt.binance({
    'apiKey': '',
    'secret': '',
    'enableRateLimit': True,
})

# Get historical price data
symbol = 'BTC/USDT'
ohlcv = exchange.fetch_ohlcv(symbol, timeframe='4h', limit=1000)  # Adjust limit as needed
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Set timezone to UTC+7
utc7 = pytz.timezone('Asia/Bangkok')
df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.utc).dt.tz_convert(utc7)

# Calculate EMA12
df['EMA12'] = df['close'].ewm(span=12, adjust=False).mean()

# Implement Buy/Sell Signals
df['buy_signal'] = df['close'] > df['EMA12']
df['sell_signal'] = df['close'] < df['EMA12']

# Set start and finish dates
start_date = pd.Timestamp('2023-01-01', tz=utc7)
finish_date = pd.Timestamp('2023-02-01', tz=utc7)
df = df[(df['timestamp'] >= start_date) & (df['timestamp'] <= finish_date)]

# Initialize variables
initial_balance = 1000  # Initial balance in USDT
balance = initial_balance
btc_balance = 0
position = None
entry_price = None
exit_price = None
profit_loss = 0

# Track trade information
trades = []

# Backtest Your Strategy
for i, row in df.iterrows():
    if row['buy_signal']:
        if position == 'short':
            # Close short position
            profit_loss += (entry_price - row['close']) * abs(btc_balance)
            balance += abs(btc_balance) * row['close']
            trades.append({'buy_date': entry_date, 'buy_price': entry_price, 'sell_date': row['timestamp'], 'sell_price': row['close'], 'buy_position': 'short', 'sell_position': 'long', 'profit_loss': (entry_price - row['close']) * abs(btc_balance), 'buy_amount': abs(btc_balance) * row['close'], 'total_asset': balance})
            btc_balance = 0
        # Buy long
        if balance > 0:
            btc_balance = 0.7 * balance / row['close']  # Use 70% of total capital for long position
            entry_price = row['close']
            entry_date = row['timestamp']
            position = 'long'
            balance *= 0.3  # Adjust remaining balance after buying
    elif row['sell_signal']:
        if position == 'long':
            # Close long position
            profit_loss += (row['close'] - entry_price) * abs(btc_balance)
            balance += abs(btc_balance) * row['close']
            trades.append({'buy_date': entry_date, 'buy_price': entry_price, 'sell_date': row['timestamp'], 'sell_price': row['close'], 'buy_position': 'long', 'sell_position': 'short', 'profit_loss': (row['close'] - entry_price) * abs(btc_balance), 'buy_amount': abs(btc_balance) * row['close'], 'total_asset': balance})
            btc_balance = 0
        # Sell short
        if balance > 0:
            btc_balance = -0.7 * balance / row['close']  # Use 70% of total capital for short position
            entry_price = row['close']
            entry_date = row['timestamp']
            position = 'short'
            balance *= 0.3  # Adjust remaining balance after selling short

# Close any remaining position at the end
if position == 'long':
    profit_loss += (df.iloc[-1]['close'] - entry_price) * abs(btc_balance)
    balance += abs(btc_balance) * df.iloc[-1]['close']
    trades.append({'buy_date': entry_date, 'buy_price': entry_price, 'sell_date': df.iloc[-1]['timestamp'], 'sell_price': df.iloc[-1]['close'], 'buy_position': 'long', 'sell_position': 'close', 'profit_loss': (df.iloc[-1]['close'] - entry_price) * abs(btc_balance), 'buy_amount': abs(btc_balance) * df.iloc[-1]['close'], 'total_asset': balance})
elif position == 'short':
    profit_loss += (entry_price - df.iloc[-1]['close']) * abs(btc_balance)
    balance += abs(btc_balance) * df.iloc[-1]['close']
    trades.append({'buy_date': entry_date, 'buy_price': entry_price, 'sell_date': df.iloc[-1]['timestamp'], 'sell_price': df.iloc[-1]['close'], 'buy_position': 'short', 'sell_position': 'close', 'profit_loss': (entry_price - df.iloc[-1]['close']) * abs(btc_balance), 'buy_amount': abs(btc_balance) * df.iloc[-1]['close'], 'total_asset': balance})

# Calculate final balance including profit/loss and remaining BTC value
final_balance = balance

# Print results
print(f"Start Date: {start_date}")
print(f"Finish Date: {finish_date}")
print(f"Initial Balance: {initial_balance} USDT")
print(f"Final Balance: {final_balance:.2f} USDT")
print("\nTrades:")
for trade in trades:
    print(f"Buy Date: {trade['buy_date']}, Buy Price: {trade['buy_price']}, Sell Date: {trade['sell_date']}, Sell Price: {trade['sell_price']}, Buy Position: {trade['buy_position']}, Sell Position: {trade['sell_position']}, Buy Amount: {trade['buy_amount']}, Total Asset: {trade['total_asset']}, Profit/Loss: {trade['profit_loss']}")