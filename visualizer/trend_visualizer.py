import plotly.graph_objects as go
import pandas as pd
import time

class TrendVisualizer:
    def get_current_trend(self, current_trend, since, to):
        if current_trend.direction == -1:
            return self.get_downtrend_trace(current_trend, since, to)
        elif current_trend.direction == 0:
            return self.get_neutral_trace()
        else:
            return self.get_uptrend_trace(current_trend, since, to)

    def get_neutral_trace(self):
        trace = dict(
            type='scatter',
            mode='lines',
            x=[None],
            y=[None],
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(color='rgba(128, 128, 128, 0)'),
            hoverinfo='skip',
            name='Not Trending',
            showlegend=True
        )
        return trace
    
    def get_uptrend_trace(self, current_trend, since, to):
        if current_trend.start_time < since:
            return None

        start_time = pd.to_datetime(current_trend.start_time, unit='s')
        end_time = pd.to_datetime(to, unit='s')
        low = current_trend.lowest_point
        high = current_trend.highest_point

        color = f'rgba(0, 255, 0, {0.15:.2f})'

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
            name=f'Uptrend {current_trend.touchpoints}tp',
        )
        return trace
    
    def get_downtrend_trace(self, current_trend, since, to):
        if current_trend.start_time < since:
            return None

        start_time = pd.to_datetime(current_trend.start_time, unit='s')
        end_time = pd.to_datetime(to, unit='s')
        high = current_trend.highest_point
        low = current_trend.lowest_point

        color = f'rgba(255, 0, 0, {0.15:.2f})'

        x = [start_time, end_time, end_time, start_time, start_time]
        y = [high, high, low, low, high]

        trace = dict(
            type='scatter',
            mode='lines',
            x=x,
            y=y,
            fill='toself',
            fillcolor=color,
            line=dict(color=color),
            hoverinfo='skip',
            name=f'Downtrend {current_trend.touchpoints}tp',
        )
        return trace
