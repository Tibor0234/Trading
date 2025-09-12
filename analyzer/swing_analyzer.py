import pandas as pd

class SwingAnalyzer:
    def get_swing_lows(self, df):
        swing_lows = self.swing_lows_func(df)
        return swing_lows
    
    def get_swing_highs(self, df):
        swing_highs = self.swing_highs_func(df)
        return swing_highs

    def update_swing_lows(self, df):
        swing_lows = self.swing_lows_func(df)
        if swing_lows.reset_index(drop=True).equals(self.swing_lows.reset_index(drop=True)):
            return False

        self.swing_lows = swing_lows
        return True
    
    def update_swing_highs(self, df):
        swing_highs = self.swing_highs_func(df)
        if swing_highs.reset_index(drop=True).equals(self.swing_highs.reset_index(drop=True)):
            return False
        
        self.swing_highs = swing_highs
        return True

    def swing_lows_func(self, df):
        lows = []

        for i in range(len(df) - 1):
            open1, close1 = df.iloc[i][['open', 'close']]
            open2, close2 = df.iloc[i + 1][['open', 'close']]

            is_low = (open1 >= close1 and open2 < close2) or (open1 > close1 and open2 <= close2)

            if is_low:
                current_low = df['low'].iloc[i]
                next_low = df['low'].iloc[i + 1]

                if current_low < next_low:
                    low = current_low
                    time = df['time'].iloc[i]
                else:
                    low = next_low
                    time = df['time'].iloc[i + 1]
                
                lows.append({'time': time, 'low': low})

        if not lows:
            return pd.DataFrame(columns=['time', 'low'])

        lows_df = pd.DataFrame(lows)

        swing_lengths = []

        for index in range(len(lows_df)):
            current_low = lows_df['low'].iloc[index]

            length = 1
            while True:
                left_start = max(0, index - length)
                right_end = min(len(lows_df), index + length + 1)

                window = lows_df['low'].iloc[left_start:right_end]

                if current_low <= window.min() and (left_start > 0 or right_end < len(lows_df)):
                    length += 1
                else:
                    break

            swing_lengths.append(length - 1)

        swing_lows = lows_df.copy()
        swing_lows['swing_length'] = swing_lengths
        return swing_lows

    def swing_highs_func(self, df):
        highs = []

        for i in range(len(df) - 1):
            open1, close1 = df.iloc[i][['open', 'close']]
            open2, close2 = df.iloc[i + 1][['open', 'close']]

            is_high = (open1 <= close1 and open2 > close2) or (open1 < close1 and open2 >= close2)

            if is_high:
                current_high = df['high'].iloc[i]
                next_high = df['high'].iloc[i + 1]

                if current_high > next_high:
                    high = current_high
                    time = df['time'].iloc[i]
                else:
                    high = next_high
                    time = df['time'].iloc[i + 1]
                
                highs.append({'time': time, 'high': high})

        if not highs:
            return pd.DataFrame(columns=['time', 'high'])

        highs_df = pd.DataFrame(highs)

        swing_lengths = []

        for index in range(len(highs_df)):
            current_high = highs_df['high'].iloc[index]

            length = 1
            while True:
                left_start = max(0, index - length)
                right_end = min(len(highs_df), index + length + 1)

                window = highs_df['high'].iloc[left_start:right_end]

                if current_high >= window.max() and (left_start > 0 or right_end < len(highs_df)):
                    length += 1
                else:
                    break

            swing_lengths.append(length - 1)

        swing_highs = highs_df.copy()
        swing_highs['swing_length'] = swing_lengths
        return swing_highs
    
    def is_new_potential_low(self, cache_df):
        last_candles_df = cache_df[-2:]

        open1, close1 = last_candles_df.iloc[0][['open', 'close']]
        open2, close2  = last_candles_df.iloc[1][['open', 'close']]

        if (open1 >= close1 and open2 < close2) or (open1 > close1 and open2 <= close2):
            return True
        return False
    
    def is_new_potential_high(self, cache_df):
        last_candles_df = cache_df[-2:]

        open1, close1 = last_candles_df.iloc[0][['open', 'close']]
        open2, close2 = last_candles_df.iloc[1][['open', 'close']]

        if (open1 <= close1 and open2 > close2) or (open1 < close1 and open2 >= close2):
            return True
        return False