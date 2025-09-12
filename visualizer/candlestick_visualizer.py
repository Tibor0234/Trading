import plotly.graph_objects as go
import pandas as pd
import numpy as np

class CandlestickVisualizer:
    def get_candlesticks(self, chart):
        chart['datetime'] = pd.to_datetime(chart['time'], unit='s')

        candlesticks = go.Candlestick(
            x=chart['datetime'],
            open=chart['open'],
            high=chart['high'],
            low=chart['low'],
            close=chart['close'],
            increasing_line_color='green',
            decreasing_line_color='red',
            name='Candle',
            showlegend=False
        )

        return candlesticks
    
    def get_volumes(self, chart):
        chart['datetime'] = pd.to_datetime(chart['time'], unit='s')
        colors = np.where(chart['close'] >= chart['open'], 'green', 'red')

        volume = go.Bar(
            x=chart['datetime'],
            y=chart['volume'],
            marker=dict(
                color=colors,
                line=dict(width=0)
                ),
            name='Volume',
            yaxis='y2',
            showlegend=False
        )

        return volume