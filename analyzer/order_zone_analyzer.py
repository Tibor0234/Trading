from analyzer.structures import OrderZone

class OrderZoneAnalyzer:
    def __init__(self, tolerance):
        self.tolerance = tolerance

    def get_demand_zones(self, swing_lows):
        demand_zones = self.demand_zones_func(swing_lows)
        return demand_zones
    
    def get_supply_zones(self, swing_highs):
        supply_zones = self.supply_zones_func(swing_highs)
        return supply_zones

    def demand_zones_func(self, swing_lows):
        used_indices = set()
        zones = []

        for i in range(len(swing_lows)):
            if i in used_indices:
                continue

            a_low = swing_lows['low'].iloc[i]

            tolerance = a_low * self.tolerance

            zone_low = a_low - tolerance
            zone_high = a_low + tolerance

            start_time = swing_lows['time'].iloc[i]
            end_time = swing_lows['time'].iloc[i]

            group_indices = [i]
            valid = True

            j = i + 1
            while j < len(swing_lows):
                if j in group_indices:
                    j += 1
                    continue

                b_low = swing_lows['low'].iloc[j]
                b_time = swing_lows['time'].iloc[j]

                if zone_low <= b_low <= zone_high:
                    zone_low = min(zone_low, b_low - tolerance)
                    zone_high = max(zone_high, b_low + tolerance)
                    group_indices.append(j)

                    if b_time > end_time:
                        end_time = b_time

                    valid = False
                    j = i + 1
                    continue
                elif b_low < zone_low:
                    valid = False
                    break
                elif b_low > zone_high and start_time < b_time < end_time:
                    valid = True
                j += 1
                    
            if end_time - start_time == 0:
                valid = False

            if valid:
                zones.append(
                    OrderZone(
                        zone_low=zone_low,
                        zone_high=zone_high,
                        start_time=start_time,
                        end_time=end_time,
                        touchpoints=len(group_indices),
                        tolerance=self.tolerance
                    )
                )
                used_indices.update(group_indices)

        return zones
    
    def supply_zones_func(self, swing_highs):
        used_indices = set()
        zones = []

        for i in range(len(swing_highs)):
            if i in used_indices:
                continue

            a_high = swing_highs['high'].iloc[i]
            tolerance = a_high * self.tolerance

            zone_low = a_high - tolerance
            zone_high = a_high + tolerance

            start_time = swing_highs['time'].iloc[i]
            end_time = swing_highs['time'].iloc[i]

            group_indices = [i]
            valid = False

            j = i + 1
            while j < len(swing_highs):
                if j in group_indices:
                    j += 1
                    continue

                b_high = swing_highs['high'].iloc[j]
                b_time = swing_highs['time'].iloc[j]

                if zone_low <= b_high <= zone_high:
                    zone_low = min(zone_low, b_high - tolerance)
                    zone_high = max(zone_high, b_high + tolerance)
                    group_indices.append(j)

                    if b_time > end_time:
                        end_time = b_time

                    valid = False
                    j = i + 1
                    continue
                elif b_high > zone_high:
                    valid = False
                    break
                elif b_high < zone_low and start_time < b_time < end_time:
                    valid = True
                j += 1

            if end_time - start_time == 0:
                valid = False

            if valid:
                zones.append(
                    OrderZone(
                        zone_low=zone_low,
                        zone_high=zone_high,
                        start_time=start_time,
                        end_time=end_time,
                        touchpoints=len(group_indices),
                        tolerance=self.tolerance
                        )
                )
                used_indices.update(group_indices)

        return zones