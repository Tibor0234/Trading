class Ema:
    def __init__(self, length, values):
        self.length = length
        self.k = 2 / (length + 1)
        self.values = values

    def get_current_value(self):
        return self.values[-1]['ema']
    
    def get_value_at(self, ts):
        for item in reversed(self.values):
            if item['time'] <= ts:
                return item['ema']
        return None
    
    def add(self, time, value):
        self.values.append({
            'time': time,
            'ema': value
        })