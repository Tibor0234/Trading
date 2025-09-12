class Trendline:
    def __init__(self, m, c, base_time, touchpoints, end_time, tolerance, slope):
        self.m = m
        self.c = c
        self.base_time = base_time
        self.touchpoints = touchpoints
        self.end_time = end_time
        self.tolerance = tolerance
        self.slope = slope

    def get_y_on_line(self, x):
        return self.m * (x - self.base_time) + self.c
    
    def get_tolerance_low(self, y):
        return y * (1 - self.tolerance)
    
    def get_tolerance_high(self, y):
        return y * (1 + self.tolerance)

class OrderZone:
    def __init__(self, zone_low, zone_high, start_time, end_time, touchpoints, tolerance):
        self.zone_low = zone_low
        self.zone_high = zone_high
        self.start_time = start_time
        self.end_time = end_time
        self.touchpoints = touchpoints
        self.tolerance = tolerance

    def get_zone_low_prec(self):
        return self.zone_low * (1 + self.tolerance)
    
    def get_zone_high_prec(self):
        return self.zone_high * (1 - self.tolerance)

class Trend:
    def __init__(self, direction, start_time = None, end_time = None, touchpoints = None, lowest_point = None, highest_point = None):
        self.direction = direction
        self.start_time = start_time
        self.end_time = end_time
        self.touchpoints = touchpoints
        self.lowest_point = lowest_point
        self.highest_point = highest_point