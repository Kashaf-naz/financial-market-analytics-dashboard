import streamlit as st
import yfinance as yf
from datetime import datetime
import pandas as pd
from streamlit_autorefresh import st_autorefresh

def show_watchlist(refresh_sec=60):
    """Production version of Market Watch sidebar (optimized with batch downloads + spinner)"""

    # Auto-refresh
    st_autorefresh(interval=refresh_sec * 1000, key="market_watch")

    groups = {
        "📈 Commodities": {
            "Gold": "GC=F",
            "Silver": "SI=F",
            "Crude Oil": "CL=F",
            "Natural Gas": "NG=F",
            "Copper": "HG=F"
        },
        "📈 Indices": {
            "S&P 500": "^GSPC",
            "Dow Jones": "^DJI",
            "Nasdaq": "^IXIC",
            "VIX": "^VIX"
        },
        "💵 Yields / Rates": {
            "US 10Y Yield": "^TNX",
            "US 2Y Yield": "^IRX"
        }
    }

    st.sidebar.markdown("## 🌍 Market Watch")

    # CSS for clean look
    st.sidebar.markdown("""
        <style>
        .market-row {
            display: flex;
            justify-content: space-between;
            padding: 2px 6px;
            margin: 2px 0;
            border-radius: 6px;
            font-size: 14px;
        }
        .market-row span {
            min-width: 70px;
            text-align: right;
        }
        .market-name {
            flex: 1;
            text-align: left;
            font-weight: 500;
        }
        .chg-pos { background-color: rgba(0, 200, 0, 0.15); color: white; }
        .chg-neg { background-color: rgba(200, 0, 0, 0.15); color: white; }
        .chg-flat { background-color: rgba(128, 128, 128, 0.15); color: #white; }
        </style>
    """, unsafe_allow_html=True)

    for group_name, tickers in groups.items():
        st.sidebar.markdown(f"### {group_name}")

        # 🌀 Spinner while fetching data
        with st.spinner(f"Loading {group_name}..."):
            try:
                # ✅ Batch download all tickers in this group (intraday first)
                symbols = list(tickers.values())
                df = yf.download(
                    symbols, period="1d", interval="1m", group_by="ticker", progress=False
                )

                # Fallback to daily if intraday is empty
                if df.empty:
                    df = yf.download(
                        symbols, period="5d", interval="1d", group_by="ticker", progress=False
                    )

                for display_name, ticker in tickers.items():
                    latest, prev, pct_change = None, None, None

                    try:
                        # Handle multi-index DataFrame
                        if isinstance(df, pd.DataFrame) and not df.empty:
                            if (ticker, "Close") in df.columns:  # intraday multi-index
                                series = df[(ticker, "Close")].dropna()
                            elif ticker in df.columns:  # daily single index
                                series = df[ticker].dropna()
                            else:
                                series = pd.Series()

                            if len(series) >= 2:
                                latest, prev = float(series.iloc[-1]), float(series.iloc[-2])

                        # Compute %
                        if latest is not None and prev is not None and prev != 0:
                            pct_change = ((latest - prev) / prev) * 100

                        # Format display
                        price_text = f"{latest:.2f}" if latest is not None else "—"
                        if pct_change is not None:
                            if pct_change > 0:
                                cls, pct_text = "chg-pos", f"{pct_change:+.2f}%"
                            elif pct_change < 0:
                                cls, pct_text = "chg-neg", f"{pct_change:+.2f}%"
                            else:
                                cls, pct_text = "chg-flat", "0.00%"
                        else:
                            cls, pct_text = "chg-flat", "—"

                        # Render row
                        st.sidebar.markdown(
                            f"<div class='market-row {cls}'>"
                            f"<div class='market-name'>{display_name}</div>"
                            f"<span>{price_text}</span>"
                            f"<span>{pct_text}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                    except Exception as e:
                        st.sidebar.write(f"{display_name}: ⚠️ {e}")

            except Exception as e:
                st.sidebar.write(f"{group_name} fetch error: ⚠️ {e}")

    st.sidebar.caption(f"⏱️ Updated: {datetime.now().strftime('%H:%M:%S')}")
