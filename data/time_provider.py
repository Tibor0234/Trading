class TimeProvider:
    instance = None

    @staticmethod
    def init_time_provider(ts):
        TimeProvider.instance = TimeProvider(ts)

    def __init__(self, ts):
        self.time = ts

    def set_time(self, ts):
        self.time = ts
    
    def get_time(self):
        return self.time