import plotly.graph_objects as go
from datetime import datetime, time as dtime
from zoneinfo import ZoneInfo

class SessionVisualizer:
    def get_session_opens(self, chart):
        traces = []

        lowest = chart['low'].min()
        highest = chart['high'].max()

        last_ny_open = None
        last_london_open = None
        last_tokyo_open = None

        for ts in chart['time']:
            # New York
            ny_time = datetime.fromtimestamp(ts, tz=ZoneInfo("America/New_York"))
            if ny_time.isoweekday() < 6:
                ny_open = datetime.combine(ny_time.date(), dtime(9, 30), tzinfo=ZoneInfo("America/New_York")).timestamp()
                if ts == ny_open:
                    last_ny_open = ts

            # London
            london_time = datetime.fromtimestamp(ts, tz=ZoneInfo("Europe/London"))
            if london_time.isoweekday() < 6:
                london_open = datetime.combine(london_time.date(), dtime(8, 0), tzinfo=ZoneInfo("Europe/London")).timestamp()
                if ts == london_open:
                    last_london_open = ts

            # Tokyo
            tokyo_time = datetime.fromtimestamp(ts, tz=ZoneInfo("Asia/Tokyo"))
            if tokyo_time.isoweekday() < 6:
                tokyo_open = datetime.combine(tokyo_time.date(), dtime(9, 0), tzinfo=ZoneInfo("Asia/Tokyo")).timestamp()
                if ts == tokyo_open:
                    last_tokyo_open = ts

        # Csak az utolsókat adjuk hozzá
        if last_ny_open is not None:
            traces.append(self._make_vline(last_ny_open, "New York Open", lowest, highest))
        if last_london_open is not None:
            traces.append(self._make_vline(last_london_open, "London Open", lowest, highest))
        if last_tokyo_open is not None:
            traces.append(self._make_vline(last_tokyo_open, "Tokyo Open", lowest, highest))

        return traces

    def _make_vline(self, ts, name, lowest, highest):
        dt = datetime.fromtimestamp(ts, tz=ZoneInfo("UTC"))

        if name == "New York Open":
            color = "yellow"
        if name == "London Open":
            color = "orange"
        if name == "Tokyo Open":
            color = "gold"

        return go.Scatter(
            x=[dt, dt],
            y=[lowest, highest],
            mode="lines",
            line=dict(color=color, width=1.5, dash="dot"),
            name=name,
            xaxis="x",
            yaxis="y",
            visible='legendonly'
        )
