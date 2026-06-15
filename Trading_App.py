import streamlit as st
import yfinance as yf
import requests
import pandas as pd
import datetime
from pages.utils.watchlist import show_watchlist
import threading

st.set_page_config(
    page_title="Trading App",
    page_icon="📉",
    layout="wide"
)


# ---- HERO ----
st.markdown(
    """
    <div style="
        text-align: center; 
        padding: 60px 20px; 
        border-radius: 16px; 
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364); 
        color: white;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
    ">
        <h1 style="font-size: 3em; margin-bottom: 10px;">🚀 Stock Market Analysis & Forecasting</h1>
        <h3 style="margin-top: 0; font-weight: 400; font-size: 1.5em;">
            A Smarter, Data-Driven Approach to Market Trends
        </h3>
        <p style="font-size: 1.1em; color: #dcdcdc; margin-top: 15px;">
            Stay ahead of the markets with real-time insights, forecasts, and smart tools.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)
st.markdown("---")

# ---- MARKET SNAPSHOT ----
st.subheader("🌍 Market Snapshot")

indices = {"S&P 500": "^GSPC", "Dow Jones": "^DJI", "Nasdaq": "^IXIC"}
cols = st.columns(len(indices))

for i, (name, ticker) in enumerate(indices.items()):
    try:
        price = yf.Ticker(ticker).history(period="1d")["Close"].iloc[-1]
        cols[i].metric(name, f"{price:,.2f}")
    except Exception:
        cols[i].metric(name, "N/A")

st.markdown("---")

# ---- MARKET SENTIMENT ----
st.subheader("🧭 Market Sentiment")

@st.cache_data(ttl=3600)  # cache for 1 hour
def fetch_crypto_fear_greed():
    """Fetch the Crypto Fear & Greed Index from alternative.me API"""
    url = "https://api.alternative.me/fng/?limit=1"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json().get("data", [])
            if data:
                item = data[0]
                return item.get("value"), item.get("value_classification")
    except Exception as e:
        return None, f"Error: {e}"
    return None, None

@st.cache_data(ttl=3600)  # cache for 1 hour
def get_stocks_above_50dma(tickers):
    """Calculate % of stocks above 50-day moving average"""
    try:
        df = yf.download(tickers, period="6mo")["Close"]
        last = df.iloc[-1]
        ma50 = df.rolling(50).mean().iloc[-1]
        mask = (last > ma50).dropna()
        pct = round((mask.sum() / len(mask)) * 100, 2)
        if pct > 70:
            sentiment = "📈 Bullish"
        elif pct >= 50:
            sentiment = "⚖️ Neutral"
        else:
            sentiment = "📉 Bearish"
        return f"{pct}%", sentiment
    except Exception as e:
        return None, f"Error: {e}"

col1, col2 = st.columns(2)

# Show Fear & Greed Index
fng_value, fng_label = fetch_crypto_fear_greed()
with col1:
    if fng_value:
        st.metric("Fear & Greed Index", fng_value, fng_label)
    else:
        st.metric("Fear & Greed Index", "N/A")

# Show % above 50DMA
sample_tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", "META", "TSLA", "NVDA"]
pct_str, dma_sentiment = get_stocks_above_50dma(sample_tickers)
with col2:
    if pct_str:
        st.metric("Stocks Above 50DMA", pct_str, dma_sentiment)
    else:
        st.metric("Stocks Above 50DMA", "N/A")


st.markdown("---")

# ---- TOP MOVERS (fixed serial numbers & ordering) ----
st.subheader("🚀 Top Movers (Today)")

movers = ["AAPL", "MSFT", "TSLA", "NVDA", "AMZN","GOOGL"]  # sample tickers
data = []
for ticker in movers:
    try:
        df = yf.Ticker(ticker).history(period="5d")
        if len(df) < 2:
            continue
        latest = float(df["Close"].iloc[-1])
        prev = float(df["Close"].iloc[-2])
        change = (latest - prev) / prev * 100
        data.append([ticker, latest, change])
    except Exception:
        continue

df_movers = pd.DataFrame(data, columns=["Ticker", "Price", "% Change"])

if df_movers.empty:
    st.info("No mover data available right now.")
else:
    # create gainers (largest positive % change first)
    gainers = df_movers.sort_values("% Change", ascending=False).reset_index(drop=True)
    gainers["Rank"] = gainers.index + 1

    # create losers (most negative % change first)
    losers = df_movers.sort_values("% Change", ascending=True).reset_index(drop=True)
    losers["Rank"] = losers.index + 1

    n = 3  # how many to show
    show_gainers = gainers.head(n).copy()
    show_losers = losers.head(n).copy()

    # formatting for display
    show_gainers["Price"] = show_gainers["Price"].map(lambda x: f"${x:,.2f}")
    show_gainers["% Change"] = show_gainers["% Change"].map(lambda x: f"{x:+.2f}%")
    show_losers["Price"] = show_losers["Price"].map(lambda x: f"${x:,.2f}")
    show_losers["% Change"] = show_losers["% Change"].map(lambda x: f"{x:+.2f}%")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🔼 Top Gainers**")
        st.table(show_gainers[["Rank", "Ticker", "Price", "% Change"]].set_index("Rank"))
    with col2:
        st.markdown("**🔽 Top Losers**")
        st.table(show_losers[["Rank", "Ticker", "Price", "% Change"]].set_index("Rank"))


st.markdown("---")

# ---- NAVIGATION CARDS ----
st.subheader("📂 Explore the App")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 📊 Market Factors")
    st.write("Explore economic indicators and their impact on assets.")
    if st.button("Go →", key="factors"):
        st.switch_page("pages/Market_Economic_Factors.py")

with col2:
    st.markdown("### 💰 Cryptocurrencies")
    st.write("Track Bitcoin, Ethereum, and more.")
    if st.button("Go →", key="crypto"):
        st.switch_page("pages/Market_Analysis.py")

with col3:
    st.markdown("### 🏭 Commodities")
    st.write("Analyze Gold, Silver, Oil and more.")
    if st.button("Go →", key="commodities"):
        st.switch_page("pages/Market_Analysis.py")

# ---- WATCHLIST PREVIEW ----

show_watchlist(refresh_sec=60)

st.markdown("---")

# ---- LATEST NEWS ----



FINNHUB_API_KEY = "d3ftb4pr01qqbh546isgd3ftb4pr01qqbh546it0"  # your key

# A simple global cache (per session) for news
if "news_items" not in st.session_state:
    st.session_state["news_items"] = []
if "news_last_fetch" not in st.session_state:
    st.session_state["news_last_fetch"] = None

def fetch_news_finnhub(limit=5):
    """Fetch latest market news from Finnhub API."""
    url = "https://finnhub.io/api/v1/news"
    params = {"category": "general", "token": FINNHUB_API_KEY}
    try:
        resp = requests.get(url, params=params, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data[:limit]  # only keep top N
    except Exception as e:
        print(f"⚠️ Error fetching news: {e}")
    return []

def background_fetch_news(limit=5):
    """Run news fetch in the background thread and update session_state."""
    st.session_state["news_items"] = fetch_news_finnhub(limit=limit)
    st.session_state["news_last_fetch"] = datetime.datetime.now()

# ---- Display Section ----
st.subheader("📰 Latest Market News")

# If no news yet, start background fetch
if not st.session_state["news_items"]:
    st.info("Fetching latest news in the background... please wait a moment ⏳")
    thread = threading.Thread(target=background_fetch_news, args=(5,))
    thread.start()
else:
    # Show cached news instantly
    for item in st.session_state["news_items"]:
        timestamp = datetime.datetime.fromtimestamp(item.get("datetime"))
        st.markdown(
            f"**{item.get('headline')}**  \n"
            f"<span style='color:gray; font-size:90%'>{item.get('source')} — {timestamp.strftime('%Y-%m-%d %H:%M')}</span>  \n"
            f"[Read more]({item.get('url')})",
            unsafe_allow_html=True
        )

# Separator
st.markdown("---")

# Footer with last update time
if st.session_state["news_last_fetch"]:
    st.caption(f"⚡ News last updated: {st.session_state['news_last_fetch'].strftime('%Y-%m-%d %H:%M:%S')}")
else:
    st.caption("⚡ News is being fetched...")



