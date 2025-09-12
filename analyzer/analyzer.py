class Analyzer:
    def __init__(self, swing_analyzer, trendline_analyzer, order_zone_analyzer, trend_analyzer, ema_analyzer):   
        self.swing_analyzer = swing_analyzer
        self.trendline_analyzer = trendline_analyzer
        self.order_zone_analyzer = order_zone_analyzer
        self.trend_analyzer = trend_analyzer
        self.ema_analyzer = ema_analyzer