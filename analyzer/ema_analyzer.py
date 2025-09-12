from analyzer.indicators import Ema

class EmaAnalyzer:
    def get_ema(self, length, df):
        prices = df['close'].tolist()
        times = df['time'].tolist()
        ema_values = []
        k = 2 / (length + 1)

        sma = sum(prices[:length]) / length
        ema_values.append(sma)

        for price in prices[length:]:
            prev_ema = ema_values[-1]
            ema = (price - prev_ema) * k + prev_ema
            ema_values.append(ema)

        ema_times = times[length - 1:]
        ema_list = []
        for time, value in zip(ema_times, ema_values):
            ema_list.append({
                'time': time,
                'ema': value
            })

        return Ema(length, ema_list)

    def update_ema(self, ema, df):
        price = df['close'].iloc[-1]
        time = df['time'].iloc[-1]

        prev_ema = ema.get_current_value()
        ema_value = (price - prev_ema) * ema.k + prev_ema

        ema.add(time, ema_value)