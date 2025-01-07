import pandas as pd
import numpy as np
from scipy.stats import linregress

class CandlestickAnalyser:
    def __init__(self,dataframe:pd.DataFrame):
        """
        Initialize the CandlestickAnalyzer with a DataFrame.
        
        Args:
            dataframe (pd.DataFrame): DataFrame with columns ['OPEN', 'HIGH', 'LOW', 'CLOSE'].
        """
        self.df = dataframe.copy()
        self.patterns ={} #store detected patterns
        required_columns = {'OPEN', 'HIGH', 'LOW', 'CLOSE'}
        if not required_columns.issubset(self.df.columns):
            raise ValueError(f"The DataFrame must contain the following columns: {required_columns}")


    def add_pattern(self,pattern_name,condition):
        """
        Adds a pattern column to the DataFrame based on a condition.
        
        Args:
            pattern_name (str): Name of the candlestick pattern.
            condition (pd.Series): Boolean Series indicating the pattern's presence.
        """
        self.df[pattern_name] = condition
        self.patterns[pattern_name] = condition
    

    def detect_murubuzo(self):

        bullish_marubuzo = (
        (self.df["OPEN"] < self.df['CLOSE']) &  # Bullish candle
        (self.df['LOW'] >= 0.995 * self.df["OPEN"]) &  # Low is close to open
        (self.df['HIGH'] <= 1.005 * self.df['CLOSE'])  # High is close to close
    )
        
        bearish_marubuzo = (
        (self.df["OPEN"] > self.df['CLOSE']) &  # Bearish candle
        (self.df['LOW'] >= 0.995 * self.df['CLOSE']) &  # Low is close to close
        (self.df['HIGH'] <= 1.005 * self.df["OPEN"])  # High is close to open
    )
        
        self.add_pattern("bullish_marubuzo",bullish_marubuzo)
        self.add_pattern("bearish_marubuzo",bearish_marubuzo)

    def detect_doji(self):
        doji =(abs((self.df['OPEN']-self.df['CLOSE'])) <= .005*self.df['CLOSE'])
        self.add_pattern("doji",doji)

    def determine_slope(self,window=14):
        slopes = []
        for i in range(len(self.df['CLOSE']) - window + 1):
            y = self.df['CLOSE'][i:i + window]
            x = range(len(y))
            slope, _, _, _, _ = linregress(x, y)
            slopes.append(slope)
        return [None] * (window - 1) + slopes  # Add None for initial values

        # # Calculate the slope over the past n days
        # slope = self.df['CLOSE'].rolling(window=days).apply(lambda x: np.polyfit(range(len(x)), x, 1)[0])
        # return slope

    def detect_hammer_hanging_man_and_shooting_star(self):
        """
        Detect hammer and hanging man patterns based on slope and shadow/body ratio.
        """
        slope = self.determine_slope()
        
        # Calculate shadow-to-body ratios
        upper_shadow = self.df['HIGH'] - np.maximum(self.df['OPEN'], self.df['CLOSE'])
        lower_shadow = np.minimum(self.df['OPEN'], self.df['CLOSE']) - self.df['LOW']
        real_body = abs(self.df['OPEN'] - self.df['CLOSE'])

        # Define hammer and hanging man conditions
        hammer = (
            (slope < 0) &  # Negative slope
            (lower_shadow >= 2 * real_body) &  # Long lower shadow
            (upper_shadow <= real_body)  # Small upper shadow
        )

        hanging_man = (
            (slope > 0) &  # Positive slope
            (lower_shadow >= 2 * real_body) &  # Long lower shadow
            (upper_shadow <= real_body)  # Small upper shadow
        )

        shooting_star = (
            (slope >0) &  # upward trend
            (upper_shadow >= 2 * real_body) &       # Long upper shadow
            (lower_shadow <= 0.1 * real_body) &     # Minimal lower shadow
            (self.df['CLOSE'] < self.df['HIGH'])    # Close below the high
            )

        # Add patterns to the DataFrame
        self.add_pattern("hammer", hammer)
        self.add_pattern("hanging_man", hanging_man)
        self.add_pattern("shooting_star",shooting_star)

    def detect_all_patterns(self):
        """
        Detect all predefined candlestick patterns.
        Add individual pattern detection functions here.
        """
        self.detect_murubuzo()
        self.detect_doji()
        self.detect_hammer_hanging_man_and_shooting_star()
        # Add more pattern detections here as methods are implemented

    def get_results(self):
        """
        Return the DataFrame with detected patterns.
        """
        return self.df

class MultiCandlestickAnalyser:
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe.copy()
        self.patterns = {}

    def detect_engulfing(self):
        bullish_engulfing = (
            (self.df['CLOSE'].shift(1) < self.df['OPEN'].shift(1)) &  # Previous candle bearish
            (self.df['CLOSE'] > self.df['OPEN']) &                    # Current candle bullish
            (self.df['OPEN'] < self.df['CLOSE'].shift(1)) &           # Current open below previous close
            (self.df['CLOSE'] > self.df['OPEN'].shift(1))             # Current close above previous open
        )

        bearish_engulfing = (
            (self.df['CLOSE'].shift(1) > self.df['OPEN'].shift(1)) &  # Previous candle bullish
            (self.df['CLOSE'] < self.df['OPEN']) &                    # Current candle bearish
            (self.df['OPEN'] > self.df['CLOSE'].shift(1)) &           # Current open above previous close
            (self.df['CLOSE'] < self.df['OPEN'].shift(1))             # Current close below previous open
        )

        self.patterns['bullish_engulfing'] = bullish_engulfing
        self.patterns['bearish_engulfing'] = bearish_engulfing

    def get_patterns(self):
        """
        Returns the detected patterns as a dictionary.
        """
        return self.patterns

# # Volume confirmation
def volume_confirmation(days,df):
    """Check if current volume exceeds 10-day average volume."""
    
    df['Avg_Volume'] = df['VOLUME'].rolling(window=days).mean()
    df['Volume_Confirmed'] = df['VOLUME'] > 1.1 * df['Avg_Volume']
    return df

def sma(dataframe,column_name,timeperiod):
    dataframe[f"SMA_{timeperiod}"] = dataframe[column_name].rolling(window=timeperiod).mean()
    return dataframe

def ema(dataframe,column_name,timeperiod):
    dataframe[f"EMA_{timeperiod}"] = dataframe[column_name].ewm(span=timeperiod, adjust=False).mean()
    return dataframe


def moving_average_crossover(dataframe,column_name,short_time,long_time):

    ema(dataframe,column_name,timeperiod=short_time)
    ema(dataframe,column_name,timeperiod=long_time)
    dataframe["ma_crossover"] = dataframe[f'EMA_{short_time}']-dataframe[f'EMA_{long_time}']
    return dataframe
