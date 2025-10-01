import plotly.graph_objects as go
import pandas as pd
from data.log_handler import log_chart

class Visualizer():
    def __init__(self, candlestick_visualizer, trade_visualizer, swing_visualizer, trendline_visualizer, order_zone_visualizer, trend_visualizer, ema_visualizer, session_visualizer):
        self.candlestick_visualizer = candlestick_visualizer
        self.trade_visualizer = trade_visualizer
        self.swing_visualizer = swing_visualizer
        self.trendline_visualizer = trendline_visualizer
        self.order_zone_visualizer = order_zone_visualizer
        self.trend_visualizer = trend_visualizer
        self.ema_visualizer = ema_visualizer
        self.session_visualizer = session_visualizer

    def visualize_from_trade(self, trade):
        symbol = trade.symbol
        timeframe = trade.timeframe
        framework = trade.strategy.fw
        timeframe_obj = trade.timeframe_obj
        chart = framework.get_candles_df_with_open_candle(symbol, timeframe)
        since = chart['time'].iloc[0]
        to = chart['time'].iloc[-1]

        if trade.close_price is None:
            to_trade = to + (timeframe_obj.timestamp * 10)
        else:
            to_trade = to

        if trade.visual_open_time is None:
            if timeframe_obj.candle.is_new_candle:
                trade.visual_open_time = chart['time'].iloc[-2]
            else:
                trade.visual_open_time = chart['time'].iloc[-1]

        long_trades, short_trades = ([trade], None) if trade.direction == 1 else (None, [trade])

        swing_lows = trade.details.get('swing_lows_visual')
        swing_highs = trade.details.get('swing_highs_visual')
        support_trendlines = trade.details.get('support_trendlines_visual')
        resistance_trendlines = trade.details.get('resistance_trendlines_visual')
        demand_zones = trade.details.get('demand_zones_visual')
        supply_zones = trade.details.get('supply_zones_visual')
        current_trend = trade.details.get('current_trend_visual')
        emas = trade.details.get('emas_visual')

        fig = go.Figure()
        candlestick_traces = self.candlestick_visualizer.get_candlesticks(chart)
        fig.add_trace(candlestick_traces)
        session_open_traces = self.session_visualizer.get_session_opens(chart)
        fig.add_traces(session_open_traces)
        volume_traces = self.candlestick_visualizer.get_volumes(chart)
        fig.add_trace(volume_traces)

        if long_trades is not None:
            long_trade_traces = self.trade_visualizer.get_long_trades(long_trades, to_trade)
            fig.add_traces(long_trade_traces)
        if short_trades is not None:
            short_trade_traces = self.trade_visualizer.get_short_trades(short_trades, to_trade)
            fig.add_traces(short_trade_traces)
        if swing_lows is not None:
            low_traces = self.swing_visualizer.get_swing_lows(swing_lows, since)
            if low_traces is not None:
                fig.add_trace(low_traces)
        if swing_highs is not None:
            high_traces = self.swing_visualizer.get_swing_highs(swing_highs, since)
            if high_traces is not None:
                fig.add_trace(high_traces)
        if support_trendlines is not None:
            support_traces = self.trendline_visualizer.get_support_trendlines(support_trendlines, since, to)
            fig.add_traces(support_traces)
        if resistance_trendlines is not None:
            resistance_traces = self.trendline_visualizer.get_resistance_trendlines(resistance_trendlines, since, to)
            fig.add_traces(resistance_traces)
        if demand_zones is not None:
            demand_traces = self.order_zone_visualizer.get_demand_zones(demand_zones, since, to)
            fig.add_traces(demand_traces)
        if supply_zones is not None:
            supply_traces = self.order_zone_visualizer.get_supply_zones(supply_zones, since, to)
            fig.add_traces(supply_traces)
        if current_trend is not None:
            trend_traces = self.trend_visualizer.get_current_trend(current_trend, since, to)
            if current_trend is not None:
                fig.add_trace(trend_traces)
        if emas is not None:
            ema_traces = self.ema_visualizer.get_emas(emas, since)
            fig.add_traces(ema_traces)
        
        layout = self.get_layout(symbol, timeframe)
        fig.update_layout(layout)

        chart_path = log_chart(symbol, timeframe, fig)
        return chart_path

    def visualize_from_input(self, timeframe):
        last_candle = timeframe.candle.convert_to_df()
        chart = pd.concat([timeframe.cache_df, last_candle], ignore_index=True)

        fig = go.Figure()
        candlestick_traces = self.candlestick_visualizer.get_candlesticks(chart)
        fig.add_trace(candlestick_traces)
        session_open_traces = self.session_visualizer.get_session_opens(chart)
        fig.add_traces(session_open_traces)
        volume_traces = self.candlestick_visualizer.get_volumes(chart)
        fig.add_trace(volume_traces)

        layout = self.get_layout(timeframe.symbol, timeframe.timeframe)
        fig.update_layout(layout)

        fig.show()
    
    def get_layout(self, symbol, timeframe):
        return dict(
            title=f'{symbol} - {timeframe}',
            plot_bgcolor='black',
            paper_bgcolor='black',
            font=dict(color='white'),
            xaxis=dict(
                showgrid=True,
                gridcolor='gray',
                zerolinecolor='gray',
                linecolor='white',
                rangeslider=dict(visible=False),
                anchor='y2'
            ),
            yaxis=dict(
                title='Price',
                showgrid=True,
                gridcolor='gray',
                zerolinecolor='gray',
                linecolor='white',
                anchor='x',
                domain=[0.2, 1]
            ),
            yaxis2=dict(
                title='Volume',
                showgrid=False,
                linecolor='white',
                anchor='x',
                domain=[0, 0.2]
            ),
            showlegend=True
        )        