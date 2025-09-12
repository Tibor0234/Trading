import plotly.graph_objects as go
import pandas as pd

class SwingVisualizer:
    def get_swing_lows(self, swing_lows, since=None):
        if since is not None:
            swing_lows = swing_lows[swing_lows['time'] >= since].copy()
        if swing_lows.empty:
            return None

        swing_lows['datetime'] = pd.to_datetime(swing_lows['time'], unit='s')
        return go.Scatter(
            x=swing_lows['datetime'],
            y=swing_lows['low'],
            mode='markers',
            marker=dict(color='magenta', size=8, symbol='triangle-up'),
            name='Swing Low'
        )

    def get_swing_highs(self, swing_highs, since=None):
        if since is not None:
            swing_highs = swing_highs[swing_highs['time'] >= since].copy()
        if swing_highs.empty:
            return None

        swing_highs['datetime'] = pd.to_datetime(swing_highs['time'], unit='s')
        return go.Scatter(
            x=swing_highs['datetime'],
            y=swing_highs['high'],
            mode='markers',
            marker=dict(color='cyan', size=8, symbol='triangle-down'),
            name='Swing High'
        )
