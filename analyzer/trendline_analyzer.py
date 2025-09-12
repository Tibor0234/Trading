from analyzer.structures import Trendline

class TrendlineAnalyzer:
    def __init__(self, tolerance, timestamp):
        self.tolerance = tolerance
        self.timestamp = timestamp

    def get_support_trendlines(self, swing_lows):
        support_trendlines = self.support_trendlines_func(swing_lows)
        return support_trendlines
    
    def get_resistance_trendlines(self, swing_highs):
        resistance_trendlines = self.resistance_trendlines_func(swing_highs)
        return resistance_trendlines

    def support_trendlines_func(self, swing_lows):
        swing_lows = swing_lows.reset_index(drop=True)
        global_min_index = swing_lows['low'][::-1].idxmin()

        trendlines = []

        a_index = global_min_index

        while a_index < len(swing_lows) - 1:
            a_point = swing_lows.iloc[a_index]

            b_index = a_index + 1
            while b_index < len(swing_lows):
                b_point = swing_lows.iloc[b_index]

                base_time = float(a_point['time'])

                x1, y1 = 0, a_point['low']
                x2, y2 = float(b_point['time']) - base_time, float(b_point['low'])

                if (x2 - x1) == 0: 
                    b_index += 1
                    continue

                m = (y2 - y1) / (x2 - x1)
                c = y1

                if m < 0:
                    b_index += 1
                    continue

                valid = True
                touchpoints = 2
                m_standard = self.get_m_standard_abs(x2, y1, y2)
                restart = False

                for i in range(a_index + 1, len(swing_lows)):
                    c_index = i
                    if c_index == b_index:
                        continue

                    c_point = swing_lows.iloc[c_index]
                    x = c_point['time'] - base_time
                    
                    y = float(swing_lows['low'].iloc[i])
                    y_on_line = m * x + c
                    
                    if y < y_on_line - abs(y_on_line * self.tolerance):
                        valid = False
                        break
                    elif abs(y - y_on_line) <= y_on_line * self.tolerance:
                        if c_point['time'] > b_point['time']:
                            b_index = c_index
                            valid = False
                            restart = True
                            break
                        else:
                            touchpoints += 1
                if restart:
                    continue

                if valid:
                    trendlines.append(
                        Trendline(
                            m=m,
                            c=c,
                            base_time=base_time,
                            touchpoints=touchpoints,
                            end_time=x2,
                            tolerance=self.tolerance,
                            slope=m_standard
                            )
                    )
                    a_index = b_index
                    break
                else:
                    b_index += 1
            else:
                a_index += 1

        return trendlines
    
    def resistance_trendlines_func(self, swing_highs):
        swing_highs = swing_highs.reset_index(drop=True)
        global_max_index = swing_highs['high'][::-1].idxmax()

        trendlines = []

        a_index = global_max_index

        while a_index < len(swing_highs) - 1:
            a_point = swing_highs.iloc[a_index]

            b_index = a_index + 1
            while b_index < len(swing_highs):
                b_point = swing_highs.iloc[b_index]

                base_time = float(a_point['time'])

                x1, y1 = 0, a_point['high']
                x2, y2 = float(b_point['time']) - base_time, float(b_point['high'])

                if (x2 - x1) == 0:
                    b_index += 1
                    continue
                
                m = (y2 - y1) / (x2 - x1)
                c = y1
                
                if m > 0:
                    b_index += 1
                    continue

                valid = True
                touchpoints = 2
                m_standard = self.get_m_standard_abs(x2, y1, y2)
                restart = False

                for i in range(a_index + 1, len(swing_highs)):
                    c_index = i
                    if c_index == b_index:
                        continue

                    c_point = swing_highs.iloc[c_index]
                    x = c_point['time'] - base_time

                    y = float(swing_highs['high'].iloc[i])
                    y_on_line = m * x + c

                    if y > y_on_line + abs(y_on_line * self.tolerance):
                        valid = False
                        break
                    elif abs(y - y_on_line) <= y_on_line * self.tolerance:
                        if c_point['time'] > b_point['time']:
                            b_index = c_index
                            valid = False
                            restart = True
                            break
                        else:
                            touchpoints += 1
                if restart:
                    continue

                if valid:
                    trendlines.append(
                        Trendline(
                            m=m,
                            c=c,
                            base_time=base_time,
                            touchpoints=touchpoints,
                            end_time=x2,
                            tolerance=self.tolerance,
                            slope=m_standard
                            )
                    )
                    a_index = b_index
                    break
                else:
                    b_index += 1
            else:
                a_index += 1

        return trendlines
    
    def get_m_standard_abs(self, x2, y1, y2):
        x2_standard = x2 / self.timestamp / 60
        price_range = abs(y1 - y2)
        price_range_pct = price_range / min(y1, y2)
        price_range_standard = price_range_pct / self.tolerance
        m_standard = price_range_standard / (x2_standard - 0)

        return m_standard