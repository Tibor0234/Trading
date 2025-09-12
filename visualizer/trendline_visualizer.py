import plotly.graph_objects as go
import pandas as pd
import numpy as np
import time

class TrendlineVisualizer:
    def get_support_trendlines(self, support_trendlines, since, to):
        trendline_traces = []

        for trendline in support_trendlines:
            if trendline.base_time < since:
                continue

            x_vals = np.array([trendline.base_time, to])
            y_start = trendline.get_y_on_line(trendline.base_time)
            y_now = trendline.get_y_on_line(to)
            y_vals = np.array([y_start, y_now])

            x_times = pd.to_datetime(x_vals, unit='s')

            trace = go.Scatter(
                x=x_times,
                y=y_vals,
                mode='lines',
                line=dict(color='magenta', width=2),
                name=f'Support Trendline {trendline.touchpoints}tp'
            )
            trendline_traces.append(trace)

            lower = trendline.get_tolerance_low(y_vals)
            upper = trendline.get_tolerance_high(y_vals)

            tolerance_zone = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=list(upper) + list(lower[::-1]),
                fill='toself',
                fillcolor='rgba(255, 0, 255, 0.2)',
                line=dict(color='rgba(255, 0, 255, 0)'),
                hoverinfo='skip',
                showlegend=False
            )
            trendline_traces.append(tolerance_zone)

        return trendline_traces

    def get_resistance_trendlines(self, resistance_trendlines, since, to):
        trendline_traces = []

        for trendline in resistance_trendlines:
            if trendline.base_time < since:
                continue

            x_vals = np.array([trendline.base_time, to])
            y_vals = np.array([
                trendline.get_y_on_line(trendline.base_time),
                trendline.get_y_on_line(to)
            ])
            x_times = pd.to_datetime(x_vals, unit='s')

            trace = go.Scatter(
                x=x_times,
                y=y_vals,
                mode='lines',
                line=dict(color='cyan', width=2),
                name=f'Resistance Trendline {trendline.touchpoints}tp'
            )
            trendline_traces.append(trace)

            lower = trendline.get_tolerance_low(y_vals)
            upper = trendline.get_tolerance_high(y_vals)

            tolerance_zone = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=list(upper) + list(lower[::-1]),
                fill='toself',
                fillcolor='rgba(0, 255, 255, 0.2)',
                line=dict(color='rgba(0, 255, 255, 0)'),
                hoverinfo='skip',
                showlegend=False
            )
            trendline_traces.append(tolerance_zone)

        return trendline_traces