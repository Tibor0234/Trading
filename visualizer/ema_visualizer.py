import pandas as pd
import plotly.graph_objects as go

class EmaVisualizer:
    def get_emas(self, emas, since):
        ema_traces = []

        for ema in emas:
            color = self.get_ema_color(ema.length)

            # Szűrés since szerint
            filtered = [v for v in ema.values if since is None or v['time'] >= since]
            if not filtered:
                continue

            times = [pd.to_datetime(v['time'], unit='s') for v in filtered]
            values = [e['ema'] for e in filtered]

            trace = go.Scatter(
                x=times,
                y=values,
                mode='lines',
                line=dict(color=color, width=2),
                name=f'EMA {ema.length}',
                visible='legendonly'
            )
            ema_traces.append(trace)

        return ema_traces

    def get_ema_color(self, length, min_len=5, max_len=200):
        linear_ratio = (length - min_len) / (max_len - min_len)
        linear_ratio = min(max(linear_ratio, 0), 1)
        
        ratio = linear_ratio ** 0.1

        r = int(255 * ratio)
        g = 200
        b = int(255 * (1 - ratio))

        return f'#{r:02X}{g:02X}{b:02X}'
