import datetime
import pandas as pd
import plotly.graph_objects as go
import plotly.subplots as sp
import pandas_ta as pta
from plotly.subplots import make_subplots
# -------------------- Helper -------------------- #
def ensure_date(df):
    """Ensure dataframe has a Date column from index if needed."""
    if 'Date' not in df.columns:
        df = df.reset_index()
    if 'Date' not in df.columns:
        return None  # still no Date (e.g., fundamentals)
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.tz_localize(None)
    df = df.dropna(subset=['Date'])
    return df

def filter_data(df, num_period=None, start_date=None, end_date=None):
    df = df.copy()
    df = ensure_date(df)
    if df is None:
        return None

    # Custom range
    if num_period == 'cst' and start_date and end_date:
        try:
            start_date = pd.to_datetime(start_date).tz_localize(None)
            end_date = pd.to_datetime(end_date).tz_localize(None)
            df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
            return df
        except Exception:
            return df

    # Predefined periods
    if num_period:
        today = datetime.date.today()
        if num_period == 'ytd':
            start = pd.to_datetime(f"{today.year}-01-01")
            df = df[df['Date'] >= start]
        elif num_period.endswith('d'):
            days = int(num_period.replace('d', ''))
            start = pd.to_datetime(today - datetime.timedelta(days=days))
            df = df[df['Date'] >= start]
        elif num_period.endswith('mo'):
            months = int(num_period.replace('mo', ''))
            start = pd.to_datetime(today - pd.DateOffset(months=months))
            df = df[df['Date'] >= start]
        elif num_period.endswith('y'):
            years = int(num_period.replace('y', ''))
            start = pd.to_datetime(today - pd.DateOffset(years=years))
            df = df[df['Date'] >= start]
        # 'max' = do nothing

    return df


# --------------------- Table Functions --------------------- #
def plotly_table(dataframe):
    row_even = '#f9f9f9'
    row_odd = "#869bb1"
    header_bg = "#595c5f"
    header_font_color = 'white'
    cell_font_color = 'black'

    fill_colors = []
    for col_idx, col in enumerate([list(dataframe.index)] + [dataframe[c].tolist() for c in dataframe.columns]):
        col_colors = []
        for row_idx in range(len(col)):
            col_colors.append(row_odd if row_idx % 2 == 0 else row_even)
        fill_colors.append(col_colors)

    custom_headers = ['Close', 'High', 'Low', 'Open', 'Volume']

    fig = go.Figure(data=[go.Table(
        columnwidth=[100] + [150]*len(dataframe.columns),
        header=dict(
            values=["<b></b>"] + [f"<b>{header}</b>" for header in custom_headers],
            fill_color=header_bg,
            line_color=header_bg,
            font=dict(color=header_font_color, size=14),
            align='center',
            height=35
        ),
        cells=dict(
            values=[[f"<b>{v}</b>" for v in dataframe.index]] + [dataframe[c].tolist() for c in dataframe.columns],
            fill_color=fill_colors,
            line_color='white',
            font=dict(color=cell_font_color, size=13),
            align='left',
            height=30
        )
    )])
    fig.update_layout(autosize=True, margin=dict(l=10, r=10, t=10, b=10), height=400)
    return fig

def plotly_table2(dataframe):
    row_even = '#f9f9f9'
    row_odd = "#869bb1"
    header_bg = "#595c5f"
    header_font_color = 'white'
    cell_font_color = 'black'

    fill_colors = []
    for col_idx, col in enumerate([list(dataframe.index)] + [dataframe[c].tolist() for c in dataframe.columns]):
        col_colors = []
        for row_idx in range(len(col)):
            col_colors.append(row_odd if row_idx % 2 == 0 else row_even)
        fill_colors.append(col_colors)

    fig = go.Figure(data=[go.Table(
        header=dict(
            values=["<b><b>"] + ["<b>"+str(i)[:10]+"<b>" for i in dataframe.columns],
            fill_color=header_bg,
            line_color=header_bg,
            font=dict(color=header_font_color, size=14),
            align='center',
            height=35
        ),
        cells=dict(
            values=[["<b>"+str(i)+"<b>" for i in dataframe.index]]+[dataframe[i] for i in dataframe.columns],
            fill_color=fill_colors,
            line_color='white',
            font=dict(color=cell_font_color, size=13),
            align='left',
            height=30
        )
    )])
    row_height = 30
    header_height = 35
    table_height = header_height + (len(dataframe) * row_height)

    fig.update_layout(
        margin=dict(l=10, r=10, t=10, b=10),
        height=table_height
    )
    return fig

# -------------------- Global Chart Theme -------------------- #
CHART_THEME = {
    "paper_bgcolor": "#0e1117",
    "plot_bgcolor": "#0e1117",
    "font": dict(color="white", size=12),
    "margin": dict(l=20, r=20, t=50, b=40),
    "legend": dict(
        orientation="h",
        y=-0.25, x=0.5, xanchor="center",
        bgcolor="rgba(0,0,0,0)"
    ),
    "xaxis": dict(showgrid=True, gridcolor="rgba(255,255,255,0.2)", griddash="dot"),
    "yaxis": dict(showgrid=True, gridcolor="rgba(255,255,255,0.2)", griddash="dot"),
    "hoverlabel": dict(bgcolor="#2a2a40", font=dict(color="white"))
}


# -------------------- Price Line Chart -------------------- #
def close_chart(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = go.Figure()
    colors = {"Open": "#4fc3f7", "Close": "#ffffff", "High": "#29b6f6", "Low": "#ef5350"}
    for col, color in colors.items():
        fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe[col],
                                 mode='lines', name=col,
                                 line=dict(width=2, color=color)))

    fig.update_layout(title="Price Line Chart", height=500, **CHART_THEME)
    return fig



# -------------------- Moving Average -------------------- #
def Moving_Average(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = ensure_date(dataframe)
    if dataframe is None:
        return go.Figure()

    dataframe['SMA_20'] = pta.sma(dataframe['Close'], 20)
    dataframe['SMA_50'] = pta.sma(dataframe['Close'], 50)
    dataframe['SMA_200'] = pta.sma(dataframe['Close'], 200)

    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = go.Figure()
    price_colors = {"Open": "#4fc3f7", "Close": "#ffffff", "High": "#29b6f6", "Low": "#ef5350"}
    for col, color in price_colors.items():
        fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe[col],
                                 mode='lines', name=col,
                                 line=dict(width=1, color=color)))
    ma_colors = {"SMA_20": "purple", "SMA_50": "orange", "SMA_200": "green"}
    for col, color in ma_colors.items():
        fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe[col],
                                 mode='lines', name=col,
                                 line=dict(width=2, color=color, dash="dot")))

    fig.update_layout(title="Price with Moving Averages", height=500, **CHART_THEME)
    return fig


# -------------------- RSI -------------------- #
def RSI(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = ensure_date(dataframe)
    if dataframe is None:
        return go.Figure()

    dataframe['RSI'] = pta.rsi(dataframe['Close'])
    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dataframe['Date'], y=dataframe['RSI'],
        mode="lines", name="RSI",
        line=dict(color="#ff9800", width=2)
    ))

    # Highlight zones
    fig.add_hrect(y0=70, y1=100, fillcolor="#e57373", opacity=0.15, line_width=0)
    fig.add_hrect(y0=0, y1=30, fillcolor="#81c784", opacity=0.15, line_width=0)

    fig.update_layout(title="RSI (Relative Strength Index)", yaxis_range=[0, 100],
                      height=350, **CHART_THEME)
    return fig



# -------------------- Candlestick -------------------- #
def candlestick(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = go.Figure(data=[go.Candlestick(
        x=dataframe['Date'],
        open=dataframe['Open'],
        high=dataframe['High'],
        low=dataframe['Low'],
        close=dataframe['Close'],
        name="Price",
        increasing_line_color="#298b4f",  # Green
        decreasing_line_color="#dd2020",  # Red
        increasing_fillcolor="#298b4f",
        decreasing_fillcolor="#dd2020",
        line_width=1.2
    )])

    fig.update_layout(
        title="Candlestick Chart",
        height=500,
        paper_bgcolor="#0e1117",
        plot_bgcolor="#0e1117",
        font=dict(color="white", size=12),
        margin=dict(l=20, r=20, t=50, b=40),
        xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.15)", griddash="dot"),
        yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.15)", griddash="dot"),
        hoverlabel=dict(bgcolor="#2a2a40", font=dict(color="white")),
        showlegend=False
    )

    return fig



# -------------------- MACD -------------------- #
def MACD(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = ensure_date(dataframe)
    if dataframe is None:
        return go.Figure()

    macd_df = pta.macd(dataframe['Close'])
    dataframe['MACD'] = macd_df.iloc[:,0]
    dataframe['Signal'] = macd_df.iloc[:,1]
    dataframe['Hist'] = macd_df.iloc[:,2]

    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['MACD'],
                             mode="lines", name="MACD", line=dict(color="#26c6da", width=2)))
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Signal'],
                             mode="lines", name="Signal", line=dict(color="#ff9800", width=2, dash="dot")))
    fig.add_trace(go.Bar(x=dataframe['Date'], y=dataframe['Hist'],
                         name="Histogram",
                         marker_color=["#66bb6a" if v>0 else "#ef5350" for v in dataframe['Hist']],
                         opacity=0.6))

    fig.update_layout(title="MACD (Moving Average Convergence Divergence)", height=350, **CHART_THEME)
    return fig

# -------------------- Dashboard -------------------- #
def trading_dashboard(dataframe, num_period=None, start_date=None, end_date=None):
    dataframe = ensure_date(dataframe)
    if dataframe is None:
        return go.Figure()

    dataframe['RSI'] = pta.rsi(dataframe['Close'])
    macd_df = pta.macd(dataframe['Close'])
    dataframe['MACD'] = macd_df.iloc[:,0]
    dataframe['Signal'] = macd_df.iloc[:,1]
    dataframe['Hist'] = macd_df.iloc[:,2]

    dataframe = filter_data(dataframe, num_period, start_date, end_date)
    if dataframe is None:
        return go.Figure()

    fig = sp.make_subplots(rows=3, cols=1, shared_xaxes=True,
                           row_heights=[0.5, 0.2, 0.3], vertical_spacing=0.05,
                           subplot_titles=("Candlestick + Volume", "RSI", "MACD"))

    # Candlestick + Volume
    fig.add_trace(go.Candlestick(
        x=dataframe['Date'],
        open=dataframe['Open'], high=dataframe['High'],
        low=dataframe['Low'], close=dataframe['Close'],
        name="Price"), row=1, col=1)
    fig.add_trace(go.Bar(x=dataframe['Date'], y=dataframe['Volume'],
                         name="Volume", marker_color="#90caf9", opacity=0.4), row=1, col=1)

    # RSI
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['RSI'],
                             mode="lines", name="RSI",
                             line=dict(color="#ff9800", width=2)), row=2, col=1)
    fig.add_hrect(y0=70, y1=100, fillcolor="#e57373", line_width=0, row=2, col=1)
    fig.add_hrect(y0=0, y1=30, fillcolor="#81c784", line_width=0, row=2, col=1)

    # MACD
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['MACD'],
                             mode="lines", name="MACD", line=dict(color="#26c6da", width=2)), row=3, col=1)
    fig.add_trace(go.Scatter(x=dataframe['Date'], y=dataframe['Signal'],
                             mode="lines", name="Signal", line=dict(color="#ff9800", width=2, dash="dot")), row=3, col=1)
    fig.add_trace(go.Bar(x=dataframe['Date'], y=dataframe['Hist'],
                         name="Histogram",
                         marker_color=["#66bb6a" if v>0 else "#ef5350" for v in dataframe['Hist']],
                         opacity=0.6), row=3, col=1)

    fig.update_layout(height=900, **CHART_THEME)
    return fig



def gold_silver_chart(df, mode="Raw Prices"):
    if mode == "Raw Prices":
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=df.index, y=df["Gold"], name="Gold", line=dict(color="gold", width=2)),
            secondary_y=False
        )
        fig.add_trace(
            go.Scatter(x=df.index, y=df["Silver"], name="Silver", line=dict(color="silver", width=2)),
            secondary_y=True
        )
        fig.update_yaxes(title_text="Gold Price (USD)", secondary_y=False)
        fig.update_yaxes(title_text="Silver Price (USD)", secondary_y=True)
        fig.update_layout(title="Gold vs Silver - Raw Prices", template="plotly_white", height=500)
    else:
        df_norm = df / df.iloc[0] * 100
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm["Gold"], name="Gold", line=dict(color="gold", width=2)))
        fig.add_trace(go.Scatter(x=df_norm.index, y=df_norm["Silver"], name="Silver", line=dict(color="silver", width=2)))
        fig.update_layout(
            title=f"Gold vs Silver Performance (Rebased to 100 at {df_norm.index[0].date()})",
            xaxis_title="Date",
            yaxis_title="Index (Start=100)",
            template="plotly_white",
            height=500
        )
    return fig
