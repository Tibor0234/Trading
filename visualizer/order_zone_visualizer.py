import plotly.graph_objects as go
import pandas as pd

class OrderZoneVisualizer:
    def get_demand_zones(self, demand_zones, since, to):
        traces = []

        for zone in demand_zones:
            if zone.start_time < since:
                continue

            start_time = pd.to_datetime(zone.start_time, unit='s')
            end_time = pd.to_datetime(to, unit='s')
            low = zone.zone_low
            high = zone.zone_high
            touchpoints = zone.touchpoints

            color = f'rgba(255, 0, 255, 0.4)'

            x = [start_time, end_time, end_time, start_time, start_time]
            y = [low, low, high, high, low]

            trace = dict(
                type='scatter',
                mode='lines',
                x=x,
                y=y,
                fill='toself',
                fillcolor=color,
                line=dict(color=color),
                hoverinfo='skip',
                name=f'Demand Zone {touchpoints}tp',
            )
            traces.append(trace)

        return traces

    def get_supply_zones(self, supply_zones, since, to):
        traces = []

        for zone in supply_zones:
            if zone.start_time < since:
                continue

            start_time = pd.to_datetime(zone.start_time, unit='s')
            end_time = pd.to_datetime(to, unit='s')
            low = zone.zone_low
            high = zone.zone_high
            touchpoints = zone.touchpoints

            color = 'rgba(0, 255, 255, 0.4)'

            x = [start_time, end_time, end_time, start_time, start_time]
            y = [low, low, high, high, low]

            trace = dict(
                type='scatter',
                mode='lines',
                x=x,
                y=y,
                fill='toself',
                fillcolor=color,
                line=dict(color=color),
                hoverinfo='skip',
                name=f'Supply Zone {touchpoints}tp',
            )
            traces.append(trace)

        return traces