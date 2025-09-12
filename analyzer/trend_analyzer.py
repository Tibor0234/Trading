from analyzer.structures import Trend

class TrendAnalyzer:
    def get_current_trend(self, swing_lows, swing_highs):
        current_trend = self.current_trend_func(swing_lows, swing_highs)
        return current_trend

    def current_trend_func(self, swing_lows, swing_highs):
        trend = Trend(0)

        swing_lows_rev = swing_lows.iloc[::-1]
        swing_highs_rev = swing_highs.iloc[::-1]
        
        low_start_time = self.get_uptrend_lows_start(swing_lows_rev)

        if low_start_time is not None:
            high_start_time = self.get_uptrend_highs_start(swing_highs_rev)

            if high_start_time is not None:
                start_time, end_time, touchpoints, lowest_point, highest_point = self.get_uptrend_params(swing_lows_rev, swing_highs_rev, low_start_time, high_start_time)

                if start_time is not None:
                    trend = Trend(
                        direction=1,
                        start_time=start_time,
                        end_time=end_time,
                        touchpoints=touchpoints,
                        lowest_point=lowest_point,
                        highest_point=highest_point
                        )
        else:
            low_start_time = self.get_downtrend_lows_start(swing_lows_rev)

            if low_start_time is not None:
                high_start_time = self.get_downtrend_highs_start(swing_highs_rev)

                if high_start_time is not None:
                    start_time, end_time, touchpoints, lowest_point, highest_point = self.get_downtrend_params(swing_lows_rev, swing_highs_rev, low_start_time, high_start_time)

                    if start_time is not None:
                        trend = Trend(
                            direction=-1,
                            start_time=start_time,
                            end_time=end_time,
                            touchpoints=touchpoints,
                            lowest_point=lowest_point,
                            highest_point=highest_point
                            )

        return trend
    
    def get_uptrend_params(self, swing_lows_rev, swing_highs_rev, low_start_time, high_start_time):
        if low_start_time < high_start_time:
            prev_highs = swing_highs_rev[swing_highs_rev['time'] < high_start_time]

            if not prev_highs.empty:
                prev_high_time = prev_highs['time'].iloc[0]
                new_low_start = swing_lows_rev[(swing_lows_rev['time'] > prev_high_time) & (swing_lows_rev['time'] >= low_start_time)]

                if not new_low_start.empty:
                    new_low_start_time = new_low_start['time'].iloc[-1]
                    start_time = new_low_start_time

                else:
                    start_time = low_start_time
            else:
                start_time = low_start_time
        else:
            start_time = low_start_time

        low_segment = swing_lows_rev[swing_lows_rev['time'] >= start_time]
        high_segment = swing_highs_rev[swing_highs_rev['time'] >= start_time]

        low_touchpoints = len(low_segment)
        high_touchpoints = len(high_segment)

        if low_touchpoints >= 2 and high_touchpoints >= 1:
            touchpoints = low_touchpoints + high_touchpoints
        else:
            return None, None, None, None, None

        end_time = max(swing_lows_rev['time'].iloc[0], swing_highs_rev['time'].iloc[0])

        lowest_point = min(low_segment['low'])
        highest_point = max(high_segment['high'])

        return start_time, end_time, touchpoints, lowest_point, highest_point
        
    def get_uptrend_lows_start(self, swing_lows_rev):
        touchpoints = 1
        for i in range(len(swing_lows_rev)):
            curr_low = swing_lows_rev['low'].iloc[i]
            prev_low = swing_lows_rev['low'].iloc[min(i + 1, len(swing_lows_rev) - 1)]

            if curr_low > prev_low:
                touchpoints += 1
            else:
                if touchpoints >= 2:
                    start_time = swing_lows_rev['time'].iloc[i]

                    return start_time
                return None
            
    def get_uptrend_highs_start(self, swing_highs_rev):
        touchpoints = 1
        for i in range(len(swing_highs_rev)):
            curr_high = swing_highs_rev['high'].iloc[i]
            prev_high = swing_highs_rev['high'].iloc[min(i + 1, len(swing_highs_rev) - 1)]

            if curr_high > prev_high:
                touchpoints += 1
            else:
                if touchpoints >= 2:
                    start_time = swing_highs_rev['time'].iloc[i]
                    return start_time
                return None
            
    def get_downtrend_params(self, swing_lows_rev, swing_highs_rev, low_start_time, high_start_time):
        if high_start_time < low_start_time:
            prev_lows = swing_lows_rev[swing_lows_rev['time'] < low_start_time]

            if not prev_lows.empty:
                prev_low_time = prev_lows['time'].iloc[0]
                new_high_start = swing_highs_rev[(swing_highs_rev['time'] > prev_low_time) & (swing_highs_rev['time'] >= high_start_time)]
                
                if not new_high_start.empty:
                    new_high_start_time = new_high_start['time'].iloc[-1]
                    start_time = new_high_start_time

                else:
                    start_time = high_start_time
            else:
                start_time = high_start_time
        else:
            start_time = high_start_time

        low_segment = swing_lows_rev[swing_lows_rev['time'] >= start_time]
        high_segment = swing_highs_rev[swing_highs_rev['time'] >= start_time]

        low_touchpoints = len(low_segment)
        high_touchpoints = len(high_segment)

        if low_touchpoints >= 1 and high_touchpoints >= 2:
            touchpoints = low_touchpoints + high_touchpoints
        else:
            return None, None, None, None, None

        end_time = min(swing_lows_rev['time'].iloc[0], swing_highs_rev['time'].iloc[0])

        lowest_point = min(low_segment['low'])
        highest_point = max(high_segment['high'])

        return start_time, end_time, touchpoints, lowest_point, highest_point

    def get_downtrend_lows_start(self, swing_lows_rev):
        touchpoints = 1
        for i in range(len(swing_lows_rev)):
            curr_low = swing_lows_rev['low'].iloc[i]
            prev_low = swing_lows_rev['low'].iloc[min(i + 1, len(swing_lows_rev) - 1)]

            if curr_low < prev_low:
                touchpoints += 1
            else:
                if touchpoints >= 2:
                    start_time = swing_lows_rev['time'].iloc[i]
                    return start_time
                return None

    def get_downtrend_highs_start(self, swing_highs_rev):
        touchpoints = 1
        for i in range(len(swing_highs_rev)):
            curr_high = swing_highs_rev['high'].iloc[i]
            prev_high = swing_highs_rev['high'].iloc[min(i + 1, len(swing_highs_rev) - 1)]

            if curr_high < prev_high:
                touchpoints += 1
            else:
                if touchpoints >= 2:
                    start_time = swing_highs_rev['time'].iloc[i]
                    return start_time
                return None