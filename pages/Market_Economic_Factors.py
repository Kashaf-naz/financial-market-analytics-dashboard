# pages/Commodity_Economic_Factors.py

from datetime import date
import datetime
import streamlit as st
import pandas as pd
import yfinance as yf
from fredapi import Fred
import plotly.graph_objects as go

# =========================
# Setup
# =========================
FRED_API_KEY = "28e3e32ba4236ab367d580e3b375d4a9"
fred = Fred(api_key=FRED_API_KEY)

st.set_page_config(
    page_title="Commodity & Economic Factors Analysis",
    layout="wide"
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


# =========================
# Assets
# =========================
commodities = {
    "Gold": "GC=F",
    "Silver": "SI=F",
    "Wheat": "ZW=F",
    "Crude Oil": "CL=F",
    "Natural Gas": "NG=F",
    "Copper": "HG=F",
}

cryptos = {
    "Bitcoin": "BTC-USD",
    "Ethereum": "ETH-USD",
    "Binance Coin": "BNB-USD",
    "Solana": "SOL-USD",
    "Cardano": "ADA-USD",
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

# =========================
# Economic Indicators
# =========================
commodity_indicators = {
    "Gold": {
        "Interest Rate (Fed Funds)": "FEDFUNDS",
        "Inflation Rate (CPI)": "CPIAUCSL",
        "Unemployment Rate": "UNRATE",
    },
    "Crude Oil": {
        "WTI Crude Oil Price": "DCOILWTICO",
        "Brent Crude Oil Price": "DCOILBRENTEU",
    },
    "Natural Gas": {"Natural Gas Price (Henry Hub)": "DHHNGSP"},
    "Silver": {"Industrial Production": "INDPRO"},
    "Copper": {
        "Industrial Production": "INDPRO",
        "China GDP (YoY)": "CHNGDPNQDSMEI",
    },
    "Wheat": {"USD Strength (Trade Weighted Index)": "DTWEXBGS"},
}

crypto_indicators = {
    "Bitcoin": {
        "Fed Funds Rate": "FEDFUNDS",
        "Inflation (CPI)": "CPIAUCSL",
        "NASDAQ Composite": "NASDAQCOM",
    },
    "Ethereum": {
        "Fed Funds Rate": "FEDFUNDS",
        "NASDAQ Composite": "NASDAQCOM",
    },
    "Binance Coin": {"M2 Money Supply": "M2SL"},
    "Solana": {"VIX Volatility Index": "VIXCLS"},
    "Cardano": {"Inflation (CPI)": "CPIAUCSL"},
}

company_indicators = {
    "Apple": {"Consumer Confidence": "UMCSENT", "Inflation": "CPIAUCSL"},
    "Tesla": {"Crude Oil Price (WTI)": "DCOILWTICO", "Gasoline Price": "GASREGCOVW"},
    "Microsoft": {"NASDAQ Composite": "NASDAQCOM", "Fed Funds Rate": "FEDFUNDS"},
    "Amazon": {"Retail Sales": "RSAFS", "Consumer Confidence": "UMCSENT"},
    "Google": {"Ad Spend Index": "IPB53100S", "Unemployment Rate": "UNRATE"},
    "NVIDIA": {"Semiconductor Index": "IPB53100S", "NASDAQ Composite": "NASDAQCOM"},
    "Meta": {"Advertising Spend": "IPB53100S", "Consumer Confidence": "UMCSENT"},
}

# =========================
# Core Analysis Function
# =========================
def run_asset_analysis(asset_dict, indicator_dict, asset_type="Commodity"):
    st.title(f"{asset_type} Prices & Key Economic Factors")

    col1, col2, col3 = st.columns(3)
    with col1:
        asset_name = st.selectbox(f"Select a {asset_type}", list(asset_dict.keys()))
        ticker = asset_dict[asset_name]

      # ---- Text Input Dates with Validation ----
    with col2:
        start_date_str = st.text_input("Start Date (YYYY-MM-DD)", "2010-01-01", key=f"{asset_type}_start_date")
    with col3:
        end_date_str = st.text_input("End Date (YYYY-MM-DD)", str(datetime.date.today()), key=f"{asset_type}_end_date")

    def parse_date(date_str, default):
        try:
            # accept both "-" and "/" formats
            return pd.to_datetime(date_str, format="%Y-%m-%d", errors="raise")
        except Exception:
            try:
                return pd.to_datetime(date_str, format="%Y/%m/%d", errors="raise")
            except Exception:
                st.warning(f"⚠️ Invalid date format: `{date_str}`. Please use YYYY-MM-DD or YYYY/MM/DD. Using fallback `{default}`.")
                return pd.to_datetime(default)

    # fallback defaults
    start_date = parse_date(start_date_str, "2010-01-01")
    end_date = parse_date(end_date_str, str(datetime.date.today()))

    # ---- Load Asset Data ----
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_asset_data(ticker, start, end):
        return yf.download(ticker, start=start, end=end, auto_adjust=False)

    asset_df = load_asset_data(ticker, start_date, end_date)

    # ---- Load FRED Data ----
    @st.cache_data(ttl=3600, show_spinner=True)
    def load_fred_data(start, end, asset):
        indicators = indicator_dict.get(asset, {})
        df_list = []
        for name, series_id in indicators.items():
            try:
                series = fred.get_series(series_id, observation_start=start, observation_end=end)
                df_list.append(series.rename(name))
            except Exception as e:
                st.warning(f"Could not load {name} ({series_id}) for {asset}: {e}")
        if df_list:
            econ_df = pd.concat(df_list, axis=1).resample("M").mean()
            return econ_df
        return pd.DataFrame()

    econ_df = load_fred_data(start_date, end_date, asset_name)

    # ---- Merge Data ----
    price_col = f"{asset_name} Price"
    merged_df = econ_df.copy()
    if "Close" in asset_df.columns:
        merged_df[price_col] = asset_df["Close"].resample("M").mean()
    else:
        st.error(f"No 'Close' price found for {asset_name}")
        st.stop()

    # --- Charts ---
    period_options = ['6M', 'YTD', '1Y', '5Y', 'MAX', 'CUSTOM']
    period_map = {
        '6M': '6mo',
        'YTD': 'ytd',
        '1Y': '1y',
        '5Y': '5y',
        'MAX': 'max',
        'CUSTOM': 'cst'
    }

    num_period_label = st.radio("Select Time Period", period_options, horizontal=True, index=1, key=f"{asset_type}_period")
    num_period = period_map[num_period_label]

    ticker_obj = yf.Ticker(ticker)
    if num_period != "cst":
        hist_data = ticker_obj.history(period=num_period)
    else:
        hist_data = ticker_obj.history(start=start_date, end=end_date)

    if hist_data.empty:
        st.warning("No price data available for the selected range.")
        return

    hist_data.index = hist_data.index.tz_localize(None)
    hist_data = hist_data.resample("M").mean()
    hist_data = hist_data.rename(columns={"Close": price_col})

    # ---- Comparison Plot with Checkboxes ----
    factors = list(econ_df.columns)
    if not factors:
        st.error(f"No economic factors found for {asset_name}.")
        st.stop()

    st.subheader(f"{asset_name} Price vs Selected Economic Factors")

    # Default select first factor
    default_factors = [factors[0]]

    # Horizontal checkboxes
    selected_factors = []
    cols = st.columns(len(factors))
    for i, factor in enumerate(factors):
        default_checked = factor in default_factors
        with cols[i]:
            if st.checkbox(factor, key=f"{asset_type}_{asset_name}_{factor}", value=default_checked):
                selected_factors.append(factor)

    if not selected_factors:
        st.warning("Please select at least one factor to display.")
    else:
        plot_df = pd.concat([hist_data[[price_col]], econ_df[selected_factors]], axis=1).dropna()
        fig_compare = go.Figure()

        # Asset Price
        fig_compare.add_trace(go.Scatter(
            x=plot_df.index, y=plot_df[price_col], name=price_col,
            yaxis="y1",
            line=dict(color="gold" if asset_type == "Commodity" and asset_name == "Gold" else "darkorange", width=2),
        ))

        # Selected Factors
        for factor in selected_factors:
            fig_compare.add_trace(go.Scatter(
                x=plot_df.index, y=plot_df[factor], name=factor,
                yaxis="y2", mode="lines"
            ))

        fig_compare.update_layout(
            xaxis=dict(title="Date"),
            yaxis=dict(title=price_col, side="left", showgrid=False),
            yaxis2=dict(title="Economic Factor(s)", overlaying="y", side="right", showgrid=False),
            legend=dict(x=0.01, y=0.99),
            height=500,
            template="plotly_white",
        )
        st.plotly_chart(fig_compare, use_container_width=True)

    # ---- Correlation ----
    st.subheader("Correlation Matrix (Monthly Data)")
    window = st.selectbox("Select Rolling Window (months)", [12, 24, 36, 48], index=2, key=f"{asset_type}_rolling_window")

    df_roll = merged_df.dropna()
    if not df_roll.empty:
        corr_matrix = df_roll.rolling(window).corr().groupby(level=1).last().round(2)
        st.dataframe(corr_matrix.style.background_gradient(cmap="RdBu_r", vmin=-1, vmax=1), use_container_width=True)
    else:
        st.warning("Not enough data to compute rolling correlations.")

    st.subheader(f"🧠 Interpreted Correlations with {asset_name} Price")
    corr_df = merged_df.dropna().corr()
    asset_corr = corr_df[price_col].drop(price_col)

    def interpret_corr(value):
        if value >= 0.75: return "a **strong positive** 🔼"
        elif value >= 0.5: return "a **moderate positive** ⬆️"
        elif value >= 0.25: return "a **weak positive** ☝️"
        elif value <= -0.75: return "a **strong negative** 🔽"
        elif value <= -0.5: return "a **moderate negative** ⬇️"
        elif value <= -0.25: return "a **weak negative** 👇"
        else: return "**no clear** ⚖️"

    for factor, corr_value in asset_corr.items():
        st.markdown(f"- **{factor}** has {interpret_corr(corr_value)} correlation with **{asset_name} Price** (`{corr_value:.2f}`).")

    # ---- Rating & Weighting ----
    st.markdown("---")
    st.subheader(f"🎯 Rating & Weighting Matrix (Impact on {asset_name})")

    factors = asset_corr.index.tolist()
    tab_inputs, tab_results = st.tabs(["⚙️ Adjust Inputs", "📊 Results"])

    weight_inputs, rating_inputs, weighted_data = {}, {}, []
    total_weight = 0

    with tab_inputs:
        for factor in factors:
            col1, col2, col3 = st.columns([2, 4, 2])
            with col1:
                st.markdown(f"**{factor}**")
            with col2:
                weight = st.slider(" ", 0, 100, 25, key=f"{asset_type}_weight_{factor}", label_visibility="collapsed")
            with col3:
                rating = st.selectbox(" ", [1, 2, 3, 4, 5], index=2, label_visibility="collapsed", key=f"{asset_type}_{asset_name}_rating_{factor}")
            weight_inputs[factor], rating_inputs[factor] = weight, rating
            total_weight += weight

    if total_weight != 100:
        st.warning(f"⚠️ Total weight is {total_weight}%. Automatically normalizing weights.")
        for factor in weight_inputs:
            weight_inputs[factor] = (weight_inputs[factor] / total_weight) * 100

    total_score = 0
    for factor in factors:
        weight_pct = weight_inputs[factor]
        rating = rating_inputs[factor]
        weighted_score = (weight_pct / 100) * rating
        total_score += weighted_score
        weighted_data.append({"Factor": factor, "Weight (%)": round(weight_pct, 2), "Rating (1–5)": rating, "Weighted Score": round(weighted_score, 2)})

    score_df = pd.DataFrame(weighted_data)
    with tab_results:
        st.dataframe(score_df, use_container_width=True)
        st.markdown(f"### ✅ Total Weighted Impact Score for {asset_name}: `{total_score:.2f}` / 5.00")

    # ---- Historical Table ----
    st.markdown("---")
    st.subheader("📆 Historical Data Table")
    if not hist_data.empty:
        last_20_df = hist_data.tail(20).sort_index(ascending=False).round(2)
        table_df = pd.concat([last_20_df[[price_col]], econ_df[selected_factors]], axis=1).dropna() if selected_factors else last_20_df
        st.dataframe(table_df, use_container_width=True)
    else:
        st.warning("No historical data available for the selected period.")

# =========================
# Tabs
# =========================
tab1, tab2, tab3 = st.tabs(["📊 Cryptocurrencies", "💰 Commodities", "🏢 Companies"])

with tab1:
    run_asset_analysis(cryptos, crypto_indicators, "Cryptocurrency")

with tab2:
    run_asset_analysis(commodities, commodity_indicators, "Commodity")

with tab3:
    run_asset_analysis(companies, company_indicators, "Company")
