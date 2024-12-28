import yfinance as yf
import pandas as pd
import numpy as np

# Fetch data for multiple symbols
def fetch_data(symbols, period="1y"):
    """Fetch historical stock data for a list of symbols."""
    data = {}
    for symbol in symbols:
        try:
            df = yf.download(symbol, period=period)
            if not df.empty:
                data[symbol] = df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
    return data

# Detect candlestick patterns
def detect_patterns(df):
    """Detect candlestick patterns (e.g., engulfing, hammer)."""
    df['Bullish_Engulfing'] = (df['Close'] > df['Open'].shift()) & (df['Open'] < df['Close'].shift())
    df['Hammer'] = ((df['High'] - df['Low']) > 3 * (df['Open'] - df['Close'])) & \
                   ((df['High'] - df['Close']) < 0.3 * (df['High'] - df['Low'])) & \
                   ((df['Close'] - df['Low']) < 0.3 * (df['High'] - df['Low']))
    return df

# Volume confirmation
def volume_confirmation(df):
    """Check if current volume exceeds 10-day average volume."""
    df['Avg_Volume'] = df['Volume'].rolling(window=10).mean()
    df['Volume_Confirmed'] = df['Volume'] > 1.1 * df['Avg_Volume']
    return df

# Calculate support and resistance (pivot points)
def calculate_pivots(df):
    """Calculate pivot points for support/resistance."""
    df['Pivot'] = (df['High'].shift() + df['Low'].shift() + df['Close'].shift()) / 3
    df['Support'] = df['Pivot'] - (df['High'].shift() - df['Low'].shift())
    df['Resistance'] = df['Pivot'] + (df['High'].shift() - df['Low'].shift())
    return df

# Risk-reward calculation
def calculate_rr(entry, stop_loss, target):
    """Calculate the risk-reward ratio for a trade."""
    risk = entry - stop_loss
    reward = target - entry
    return reward / risk

# Backtest the strategy
def backtest_strategy(df, initial_balance=100000):
    """Simulate trading using the strategy on historical data."""
    balance = initial_balance
    trades = []

    for i in range(1, len(df)):
        row = df.iloc[i]
        if row['Bullish_Engulfing'] or row['Hammer']:
            if row['Volume_Confirmed']:
                entry = row['Close']
                stop_loss = row['Support']
                target = row['Resistance']

                if abs(stop_loss - entry) / entry <= 0.04:
                    rr_ratio = calculate_rr(entry, stop_loss, target)
                    if rr_ratio >= 1.5:
                        # Simulate trade
                        position_size = balance * 0.02  # Risk 2% per trade
                        shares = position_size / (entry - stop_loss)

                        balance += shares * (target - entry) if target > entry else -shares * (entry - stop_loss)

                        trades.append({
                            "Date": row.name,
                            "Entry": entry,
                            "Stop Loss": stop_loss,
                            "Target": target,
                            "Risk-Reward": rr_ratio,
                            "Balance": balance
                        })

    return pd.DataFrame(trades)

# Analyze stocks based on strategy
def analyze_stocks(data):
    """Analyze stocks and filter based on strategy criteria."""
    trade_opportunities = []

    for symbol, df in data.items():
        try:
            # Ensure the DataFrame has sufficient data
            if len(df) < 15:
                continue

            # Calculate indicators
            df = detect_patterns(df)
            df = volume_confirmation(df)
            df = calculate_pivots(df)

            # Get the latest row for evaluation
            latest = df.iloc[-1]

            # Evaluate conditions
            if latest['Bullish_Engulfing'] or latest['Hammer']:
                if latest['Volume_Confirmed']:
                    entry = latest['Close']
                    stop_loss = latest['Support']
                    target = latest['Resistance']

                    # Ensure support/resistance aligns with stop-loss
                    if abs(stop_loss - entry) / entry <= 0.04:
                        rr_ratio = calculate_rr(entry, stop_loss, target)

                        if rr_ratio >= 1.5:
                            trade_opportunities.append({
                                "Stock": symbol,
                                "Entry": round(entry, 2),
                                "Stop Loss": round(stop_loss, 2),
                                "Target": round(target, 2),
                                "Risk-Reward": round(rr_ratio, 2)
                            })

        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")

    return pd.DataFrame(trade_opportunities)

# Example usage
if __name__ == "__main__":
    symbols = ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ITC.NS"]  # Add your list of stocks
    stock_data = fetch_data(symbols)

    trade_opportunities = analyze_stocks(stock_data)

    if not trade_opportunities.empty:
        print("Trade Opportunities:")
        print(trade_opportunities)

        # Save to Excel for further review
        trade_opportunities.to_excel("trade_opportunities.xlsx", index=False)

    # Backtesting
    for symbol, df in stock_data.items():
        print(f"Backtesting for {symbol}")
        df = detect_patterns(df)
        df = volume_confirmation(df)
        df = calculate_pivots(df)
        backtest_results = backtest_strategy(df)
        print(backtest_results)

        # Save backtesting results
        backtest_results.to_excel(f"backtest_{symbol}.xlsx", index=False)
