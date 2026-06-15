import streamlit as st
import pandas as pd
import yfinance as yf
import datetime
from pages.utils.formatters import fmt_money
from pages.utils.plotly_figure import (
    MACD, RSI, Moving_Average, candlestick,
    close_chart, gold_silver_chart, plotly_table, plotly_table2
)
from pages.utils.watchlist import show_watchlist

st.set_page_config(
    page_title="Stock Analysis",
    page_icon=":page_with_curl:",
    layout="wide",
)

# =========================
# Custom CSS for Fonts & Headers
# =========================

# Load Google Font (Poppins)
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap" rel="stylesheet">
""", unsafe_allow_html=True)

# Apply custom font + adjust heading sizes
st.markdown("""
    <style>
    /* Global font */
    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }

    /* Header sizes */
    h1 {
        font-size: 2rem !important;  /* smaller than default */
        font-weight: 600 !important;
    }
    h2 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
    }
    h3 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
    }

    /* Streamlit subheader class */
    .stSubheader {
        font-size: 1.2rem !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Hide the "Running..." spinner at the top-right
hide_spinner = """
<style>
.css-1y0tads, .stSpinner {
    display: none !important;
}
</style>
"""
st.markdown(hide_spinner, unsafe_allow_html=True)

# =========================
# Assets Dictionary
# =========================
cryptos = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "Cardano": "ADA-USD"
}

commodities = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Wheat": "ZW=F",
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
}

companies = {
    "Apple": "AAPL",
    "Tesla": "TSLA",
    "Microsoft": "MSFT",
    "Amazon": "AMZN",
    "Google": "GOOGL",
    "NVIDIA": "NVDA",
    "Meta": "META",
}

indices = {
    "S&P 500": {"ticker": "^GSPC", "description": "Tracks the 500 largest publicly traded companies in the US."},
    "Dow Jones": {"ticker": "^DJI", "description": "30 large blue-chip companies in the US."},
    "NASDAQ Composite": {"ticker": "^IXIC", "description": "Heavily weighted toward technology and growth stocks."},
    "Russell 2000": {"ticker": "^RUT", "description": "Tracks 2000 small-cap US companies."},
    "FTSE 100": {"ticker": "^FTSE", "description": "100 largest companies on the London Stock Exchange."},
    "DAX (Germany)": {"ticker": "^GDAXI", "description": "40 largest German companies."},
    "Nikkei 225": {"ticker": "^N225", "description": "225 large companies in Japan."},
    "Hang Seng": {"ticker": "^HSI", "description": "Hong Kong’s main index."},
    "VIX (Volatility Index)": {"ticker": "^VIX", "description": "Measures expected volatility of the S&P 500."}
}

# -------------------------
# Cached Helpers
# -------------------------
@st.cache_data(ttl=3600)
def load_full_history(ticker: str):
    """Fetch full max history once per ticker (cached) and guarantee Date column."""
    try:
        df = yf.download(ticker, period="max", auto_adjust=False).reset_index()

        # 🔑 Flatten MultiIndex columns if they exist
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = [c[0] if c[0] != "" else c[1] for c in df.columns]

        # Normalize Date column
        if "Date" not in df.columns:
            if "Datetime" in df.columns:
                df = df.rename(columns={"Datetime": "Date"})
            elif "index" in df.columns:
                df = df.rename(columns={"index": "Date"})

        # Ensure proper dtype
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

        return df
    except Exception as e:
        st.error(f"Failed to fetch history for {ticker}: {e}")
        return pd.DataFrame()

def get_data_slice(ticker: str, start, end):
    """Slice from cached history instead of re-downloading."""
    df = load_full_history(ticker)
    if df.empty:
        return df
    return df.loc[(df["Date"] >= pd.to_datetime(start)) & (df["Date"] <= pd.to_datetime(end))]

@st.cache_data(ttl=3600)
def get_info(ticker: str) -> dict:
    """Fetch and cache ticker fundamentals/info."""
    try:
        return yf.Ticker(ticker).info
    except Exception as e:
        st.error(f"Failed to fetch info for {ticker}: {e}")
        return {}

# -------------------------
# Asset Analysis Function
# -------------------------
def asset_analysis(selected_asset, ticker, asset_type, start_date, end_date):
    st.subheader(f"{selected_asset} ({ticker})")

    info = get_info(ticker)

    # --- Asset specific info ---
    if asset_type == "crypto":
        col1, col2, col3, col4 = st.columns(4)
        col1.markdown(f"**Circulating Supply:** {fmt_money(info.get('circulatingSupply'), currency=False)}")
        col2.markdown(f"**Market Cap:** {fmt_money(info.get('marketCap'), currency=True)}")
        col3.markdown(f"**Previous Close:** {fmt_money(info.get('previousClose'), currency=True)}")
        col4.markdown(f"**Open:** {fmt_money(info.get('open'), currency=True)}")

    elif asset_type == "commodity":
        col1, col2 = st.columns(2)
        col1.markdown(f"**Previous Close:** {fmt_money(info.get('previousClose'), currency=True)}")
        col2.markdown(f"**Open:** {fmt_money(info.get('open'), currency=True)}")

    elif asset_type == "company":
        col1, col2, col3 = st.columns(3)
        col1.markdown(f"**Previous Close:** {fmt_money(info.get('previousClose'), currency=True)}")
        col2.markdown(f"**Open:** {fmt_money(info.get('open'), currency=True)}")
        col3.markdown(f"**Employees:** {info.get('fullTimeEmployees', 'N/A')}")
        st.write("**Sector:**", info.get('sector', 'Not Available'))
        st.write("**Website:**", info.get('website', 'Not Available'))
        st.write(info.get('longBusinessSummary', 'Not Available'))

    elif asset_type == "index":
        st.markdown(f"**About {selected_asset}:**")
        st.markdown(f"{indices[selected_asset]['description']}")

    # --- Daily Metrics ---
    st.markdown("---")
    st.subheader("📊 Daily Metrics")

    data = get_data_slice(ticker, start_date, end_date)
    if not data.empty and len(data) >= 2:
        latest_close = float(data['Close'].iloc[-1])
        prev_close = float(data['Close'].iloc[-2])
        daily_change = latest_close - prev_close
        daily_change_pct = (daily_change / prev_close) * 100

        m1, m2, m3 = st.columns(3)
        m1.metric("Latest Close", fmt_money(latest_close))
        m2.metric("Daily Change", f"{daily_change:+.2f}")
        m3.metric("Change (%)", f"{daily_change_pct:+.2f}%")
    else:
        st.warning("Not enough data to calculate daily change.")

    if not data.empty:
        last_10_df = data.tail(10).sort_index(ascending=False).round(3)
        st.write("##### Historical Data (Last 10 days)")
        st.plotly_chart(plotly_table(last_10_df), use_container_width=True)

    # --- Charts ---
    period_options = ['5D', '1M', '6M', 'YTD', '1Y', '5Y', 'MAX', 'CUSTOM']
    period_map = {'5D': '5d', '1M': '1mo', '6M': '6mo', 'YTD': 'ytd', '1Y': '1y', '5Y': '5y', 'MAX': 'max', 'CUSTOM': 'cst'}

    num_period_label = st.radio("Select Time Period", period_options, horizontal=True, index=3, key=f"{asset_type}_period")
    num_period = period_map[num_period_label]

    col1, col2 = st.columns(2)
    with col1:
        chart_type = st.selectbox('Chart Type', ('Candle', 'Line'), key=f"{asset_type}_chart_type")
    with col2:
        if chart_type == 'Candle':
            indicators = st.selectbox('Indicator', ('RSI', 'MACD'), key=f"{asset_type}_indicator_candle")
        else:
            indicators = st.selectbox('Indicator', ('RSI', 'Moving Average', 'MACD'), key=f"{asset_type}_indicator_line")

    full_data = load_full_history(ticker)

    if chart_type == 'Candle' and indicators == 'RSI':
        st.plotly_chart(candlestick(full_data, num_period, start_date, end_date), use_container_width=True)
        st.plotly_chart(RSI(full_data, num_period, start_date, end_date), use_container_width=True)

    elif chart_type == 'Candle' and indicators == 'MACD':
        st.plotly_chart(candlestick(full_data, num_period, start_date, end_date), use_container_width=True)
        st.plotly_chart(MACD(full_data, num_period, start_date, end_date), use_container_width=True)

    elif chart_type == 'Line' and indicators == 'RSI':
        st.plotly_chart(close_chart(full_data, num_period, start_date, end_date), use_container_width=True)
        st.plotly_chart(RSI(full_data, num_period, start_date, end_date), use_container_width=True)

    elif chart_type == 'Line' and indicators == 'Moving Average':
        st.plotly_chart(Moving_Average(full_data, num_period, start_date, end_date), use_container_width=True)

    elif chart_type == 'Line' and indicators == 'MACD':
        st.plotly_chart(close_chart(full_data, num_period, start_date, end_date), use_container_width=True)
        st.plotly_chart(MACD(full_data, num_period, start_date, end_date), use_container_width=True)

# =========================
# Gold vs Silver Function
# =========================
@st.cache_data(ttl=3600)
def load_gold_silver(start, end, freq="D"):
    try:
        data = yf.download(["GC=F", "SI=F"], start=start, end=end)["Close"]
    except Exception as e:
        st.error(f"Failed to load Gold/Silver data: {e}")
        return pd.DataFrame()

    if data.empty:
        return pd.DataFrame()

    # Flatten column names
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = [c[1] if c[1] else c[0] for c in data.columns]

    data = data.rename(columns={"GC=F": "Gold", "SI=F": "Silver"})
    if freq == "M":
        data = data.resample("M").last()

    return data.dropna()

# -------------------------
# Tabs
# -------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["💰 Cryptocurrencies", "🌾 Commodities", "🏢 Companies", "📈 Indices", "🥇 Gold vs Silver"]
)

with tab1:

    col1, col2, col3 = st.columns([1, 1, 1])  # wider for dropdown
    with col1:
        selected_asset = st.selectbox("Choose a Crypto:", list(cryptos.keys()), key="crypto_asset")
    with col2:
        start_date = st.text_input("Start Date (YYYY-MM-DD):", "2010-01-01", key="crypto_start")
    with col3:
        end_date = st.text_input("End Date (YYYY-MM-DD):", str(datetime.date.today()), key="crypto_end")
    asset_analysis(selected_asset, cryptos[selected_asset], "crypto", start_date, end_date)

with tab2:
    col1, col2, col3 = st.columns([1, 1, 1])  # wider for dropdown
    with col1:
        selected_asset = st.selectbox("Choose a Commodity:", list(commodities.keys()), key="commodity_asset")
    with col2:
        start_date = st.text_input("Start Date (YYYY-MM-DD):", "2010-01-01", key="commodity_start")
    with col3:
        end_date = st.text_input("End Date (YYYY-MM-DD):", str(datetime.date.today()), key="commodity_end")
    asset_analysis(selected_asset, commodities[selected_asset], "commodity", start_date, end_date)

with tab3:
    col1, col2, col3 = st.columns([1, 1, 1])  # wider for dropdown
    with col1:
        selected_asset = st.selectbox("Choose a Company:", list(companies.keys()), key="company_asset")
    with col2:
        start_date = st.text_input("Start Date (YYYY-MM-DD):", "2010-01-01", key="company_start")
    with col3:
        end_date = st.text_input("End Date (YYYY-MM-DD):", str(datetime.date.today()), key="company_end")
    asset_analysis(selected_asset, companies[selected_asset], "company", start_date, end_date)

with tab4:
    col1, col2, col3 = st.columns([1, 1, 1])  # wider for dropdown
    with col1:
        selected_asset = st.selectbox("Choose an Index:", list(indices.keys()), key="index_asset")
    with col2:
        start_date = st.text_input("Start Date (YYYY-MM-DD):", "2010-01-01", key="index_start")
    with col3:
        end_date = st.text_input("End Date (YYYY-MM-DD):", str(datetime.date.today()), key="index_end")
    asset_analysis(selected_asset, indices[selected_asset]["ticker"], "index", start_date, end_date)

with tab5:
    st.subheader("Gold vs Silver Comparison")
    col1, col2, col3 = st.columns([1, 1, 1])  # wider for dropdown
    with col1:
        freq_choice = st.selectbox("Select Frequency:", ["Daily", "Monthly"], key="gs_freq")
        freq = "D" if freq_choice == "Daily" else "M"
    with col2:
        start = st.text_input("Start Date (YYYY-MM-DD):", "2010-01-01", key="gs_start")
    with col3:
        end = st.text_input("End Date (YYYY-MM-DD):", str(datetime.date.today()), key="gs_end")

    df = load_gold_silver(start, end, freq)
    if df.empty:
        st.warning("No data found for this range.")
    else:
        mode = st.selectbox("View Mode:", ["Raw Prices", "Normalized Performance"], key="gs_mode")
        fig = gold_silver_chart(df, mode)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")
        st.subheader("📆 Data Table")
        st.dataframe(df)

        csv = df.to_csv().encode("utf-8")
        st.download_button("📥 Download CSV", csv, "gold_silver.csv", "text/csv")
