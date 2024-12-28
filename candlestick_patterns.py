import pandas as pd

#some parts of code taken from https://medium.com/@letspython3.x/learn-and-implement-candlestick-patterns-python-6de09854fa3e with some minor modifications


class CandleStick:
    def __init__(self, data: dict):
        self.open = data["OPEN"]
        self.close = data["CLOSE"]
        self.high = data["HIGH"]
        self.low = data["LOW"]
        self.volume = data["VOLUME"]
        self.date = data["DATE"]
        self.length = self.high - self.low
        self.bodyLength = abs(self.open - self.close)
        self.lowerWick = self.__get_lower_wick_length()
        self.upperWick = self.__get_upper_wick_length()

    def __repr__(self):
        return (f"CandleStick(open={self.open}, close={self.close},"
                f" high={self.high}, low={self.low}, volume={self.volume}")
  
    def is_bullish(self):
        return self.open < self.close
  
    def is_bearish(self):
        return self.open > self.close
    
    def __get_lower_wick_length(self):
        """Calculate and return the length of lower shadow or wick."""
        return (self.open if self.open <= self.close else self.close) - self.low

    def __get_upper_wick_length(self):
        """Calculate and return the length of upper shadow or wick."""
        return self.high - (self.open if self.open >= self.close else self.close)


# Candlesticks_pattern
# 1. Single Candlestick pattern
#     - Marubuzo -> Open=Low, High = Close (0.5% relaxation)
#     - Dojis -> Open = Close (0.5-1% relaxation)
#     - Paper_umbrella ->  length of lower shadow > length of real body


class SingleCandlePattern(CandleStick):
    """Pattern formed by the single candle."""

    def is_doji(self):
        """Doji - When Open price = Close price."""
        return self.open == self.close

    def is_four_price_doji(self):
        """Doji - When Open price = Close = low = High price."""
        return self.is_doji() and (self.high == self.low == self.open)

    def is_long_legged_doji(self):
        """upperWick is smaller than lowerWick."""
        return self.is_doji() and self.upperWick < self.lowerWick

    def is_gravestone_doji(self):
        """
        Long Upper wick/shadow and no lower wick.
        Gravestone doji 
        """
        return self.is_doji() and (self.lowerWick == 0 or self.upperWick >= 3*self.lowerWick)

    def is_dragonfly_doji(self):
        """
        Long Lower wick/shadow and no upper wick; looks like "T"
        Bullish dragonfly doji.
        """
        return self.is_doji() and (self.upperWick == 0 or self.lowerWick >= 3*self.upperWick)
    
    def is_hammer(self):
        """The Hammer is a bullish reversal pattern."""
        return self.is_bullish() and bool(self.lowerWick >= 2 * self.bodyLength > self.upperWick >= 0)
    
    def is_hanging_man(self):
        """The Hanging Man is a bearish reversal pattern."""
        return self.is_bearish() and bool(self.lowerWick >= 2 * self.bodyLength > self.upperWick >= 0)
    
    def is_bullish_murubozu(self):
        """ Murubozu pattern"""
        return self.is_bullish() and ((.99*self.open <= self.low <= self.open) and (self.close <=  self.high <= 1.01*self.close))
    
    def is_bearish_murubozu(self):
        """ Murubozu pattern"""
        return self.is_bearish() and ((.99*self.close <= self.low <= self.close) and (self.open <=  self.high <= 1.01*self.open))

