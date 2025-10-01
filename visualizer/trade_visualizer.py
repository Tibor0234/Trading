import plotly.graph_objects as go
import pandas as pd
import time

class TradeVisualizer:
    def get_long_trades(self, open_trades, to):
        long_trades = []

        for trade in open_trades:
            entry_price = trade.entry_price
            open_time = trade.visual_open_time
            tp = trade.take_profit
            sl = trade.stop_loss
            risk_pct = trade.risk_pct

            x_times = pd.to_datetime([open_time, to], unit='s')

            entry_trace = go.Scatter(
                x=x_times,
                y=[entry_price, entry_price],
                mode='lines',
                line=dict(color='darkgreen', width=2),
                name=f'Long Trade {risk_pct}%'
            )

            tp_trace = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=[entry_price, entry_price, tp, tp],
                fill='toself',
                fillcolor='rgba(0, 255, 0, 0.25)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )

            sl_trace = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=[entry_price, entry_price, sl, sl],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.25)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )

            long_trades.extend([entry_trace, tp_trace, sl_trace])

        return long_trades
    
    def get_short_trades(self, open_trades, to):
        short_trades = []

        for trade in open_trades:
            entry_price = trade.entry_price
            open_time = trade.visual_open_time
            tp = trade.take_profit
            sl = trade.stop_loss
            risk_pct = trade.risk_pct

            x_times = pd.to_datetime([open_time, to], unit='s')

            entry_trace = go.Scatter(
                x=x_times,
                y=[entry_price, entry_price],
                mode='lines',
                line=dict(color='darkred', width=2),
                name=f'Short Trade {risk_pct}%'
            )

            tp_trace = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=[entry_price, entry_price, tp, tp],
                fill='toself',
                fillcolor='rgba(0, 255, 0, 0.25)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )

            sl_trace = go.Scatter(
                x=list(x_times) + list(x_times[::-1]),
                y=[entry_price, entry_price, sl, sl],
                fill='toself',
                fillcolor='rgba(255, 0, 0, 0.25)',
                line=dict(color='rgba(0,0,0,0)'),
                hoverinfo='skip',
                showlegend=False
            )

            short_trades.extend([entry_trace, tp_trace, sl_trace])

        return short_trades
