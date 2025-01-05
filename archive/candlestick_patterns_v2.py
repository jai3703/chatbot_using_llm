class CandleStick:
    def __init__(self, row):
        self.open = row["OPEN"]
        self.close = row["CLOSE"]
        self.high = row["HIGH"]
        self.low = row["LOW"]
        self.volume = row["VOLUME"]
        self.date = row["DATE"]
        self.length = self.high - self.low
        self.bodyLength = abs(self.open - self.close)
        self.lowerWick = self.__get_lower_wick_length()
        self.upperWick = self.__get_upper_wick_length()

    def __get_lower_wick_length(self):
        return (self.open if self.open <= self.close else self.close) - self.low

    def __get_upper_wick_length(self):
        return self.high - (self.open if self.open >= self.close else self.close)

    def is_bullish(self):
        return self.open < self.close

    def is_bearish(self):
        return self.open > self.close


class SingleCandlePattern(CandleStick):
    def is_doji(self, tolerance=0.005):
        return abs(self.open - self.close) <= tolerance * self.open

    def is_four_price_doji(self):
        return self.is_doji() and (self.high == self.low == self.open)

    def is_long_legged_doji(self):
        return self.is_doji() and self.upperWick < self.lowerWick

    def is_gravestone_doji(self):
        return self.is_doji() and (self.lowerWick == 0 or self.upperWick >= 3 * self.lowerWick)

    def is_dragonfly_doji(self):
        return self.is_doji() and (self.upperWick == 0 or self.lowerWick >= 3 * self.upperWick)

    def is_hammer(self):
        return self.is_bullish() and (self.lowerWick >= 2 * self.bodyLength > self.upperWick >= 0)

    def is_hanging_man(self):
        return self.is_bearish() and (self.lowerWick >= 2 * self.bodyLength > self.upperWick >= 0)

    def is_bullish_murubozu(self, tolerance=0.005):
        return self.is_bullish() and (
            (self.low >= self.open * (1 - tolerance)) and (self.high <= self.close * (1 + tolerance))
        )

    def is_bearish_murubozu(self, tolerance=0.005):
        return self.is_bearish() and (
            (self.low >= self.close * (1 - tolerance)) and (self.high <= self.open * (1 + tolerance))
        )





# # Example Usage
# if __name__ == "__main__":
#     # Assuming 'df' is your DataFrame with columns OPEN, CLOSE, HIGH, LOW, VOLUME, DATE
#     processed_df = process_dataframe(df)
#     print(processed_df.head())
