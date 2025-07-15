import streamlit as st
import yfinance as yf
import pandas as pd
import pandas_ta as ta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import requests
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("NEWS_API_KEY")
if not api_key:
    st.error("API NOT FOUND")
    st.stop()
# -------------------- SETTINGS --------------------
st.set_page_config(layout="wide")
st.title("Stock Movement Dashboard: Technicals & News Sentiment")
# -------------------- SIDEBAR ---------------------
with st.sidebar:
    st.header("Select Parameters")
    ticker = st.text_input("Stock Ticker (e.g. TSLA)", value="TSLA").upper()
    period = st.selectbox("History Range", ["1mo", "3mo", "6mo", "1y"], index=2)
    st.info("Tip: Select at least 3-6 months of data for indicators like RSI/MACD/SMA.")
# -------------------- PRICE DATA ------------------
@st.cache_data
def get_price_data(ticker, period):
    try:
        df = yf.download(
            tickers=ticker,
            period=period,
            interval="1d",
            auto_adjust=False,
            actions=False,
            multi_level_index=False,
        )
    except TypeError:
        df = yf.download(ticker, period=period, interval="1d")
    return df
df = get_price_data(ticker, period)
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.reset_index(drop=False)
if "Date" in df.columns:
    df["Date"] = pd.to_datetime(df["Date"])
def get_column_by_substring(df, keyword):
    matches = [col for col in df.columns if keyword.lower() in str(col).lower()]
    return matches[0] if matches else None

close_col = get_column_by_substring(df, "Close")
if not close_col:
    st.error("'Close' column not found.")
    st.stop()
# -------------------- TECHNICALS ------------------
try:
    if len(df) >= 26:  # minimum for MACD
        df["RSI"] = ta.rsi(df["Close"], length=14)
        macd = ta.macd(df["Close"])
        df = pd.concat([df, macd], axis=1)
        df["MACD"] = df["MACD_12_26_9"] if "MACD_12_26_9" in df else pd.NA
    else:
        st.warning("Not enough data points to compute RSI/MACD (need at least 26 days).")
        df["RSI"] = df["MACD"] = pd.NA

    if len(df) >= 50:
        df["SMA_50"] = ta.sma(df["Close"], length=50)
    else:
        df["SMA_50"] = pd.NA

    if len(df) >= 200:
        df["SMA_200"] = ta.sma(df["Close"], length=200)
    else:
        df["SMA_200"] = pd.NA

except Exception as e:
    st.warning(f"Technical analysis error: {e}")
    df["RSI"] = df["MACD"] = df["SMA_50"] = df["SMA_200"] = pd.NA

    st.warning(f"Technical analysis error: {e}")
    df["RSI"] = df["MACD"] = df["SMA_50"] = df["SMA_200"] = pd.NA
# -------------------- METRICS ----------------------
def safe_metric(val, prefix="", na_val="N/A", ndigits=2):
    try:
        if pd.isna(val): return na_val
        return f"{prefix}{float(val):.{ndigits}f}"
    except: return na_val

col1, col2, col3, col4 = st.columns(4)
col1.metric("Last Close", safe_metric(df[close_col].iloc[-1], prefix="$"))
col2.metric("RSI", safe_metric(df["RSI"].iloc[-1]))
col3.metric("MACD", safe_metric(df["MACD"].iloc[-1]))
# -------------------- NEWS FETCH ------------------
@st.cache_data(show_spinner=False)
def fetch_news_and_analyze(ticker: str) -> pd.DataFrame:
  
    ticker_map = {
        "TSLA": "Tesla", "AAPL": "Apple", "GOOGL": "Alphabet", "GOOG": "Google", "AMZN": "Amazon",
        "MSFT": "Microsoft", "NFLX": "Netflix", "NVDA": "Nvidia", "META": "Meta Platforms",
        "BRK.B": "Berkshire Hathaway", "UNH": "UnitedHealth", "JPM": "JPMorgan Chase",
        "XOM": "Exxon Mobil", "LLY": "Eli Lilly", "PG": "Procter & Gamble", "JNJ": "Johnson & Johnson",
        "V": "Visa", "MA": "MasterCard", "HD": "Home Depot", "MRK": "Merck", "ABBV": "AbbVie", "CVX": "Chevron",
        "PEP": "PepsiCo", "AVGO": "Broadcom", "COST": "Costco", "KO": "Coca-Cola", "ADBE": "Adobe", "WMT": "Walmart",
        "CSCO": "Cisco Systems", "BAC": "Bank of America", "ACN": "Accenture", "TMO": "Thermo Fisher Scientific",
        "MCD": "McDonald's", "DHR": "Danaher", "TXN": "Texas Instruments", "LIN": "Linde",
        "ABT": "Abbott Laboratories", "PFE": "Pfizer", "INTC": "Intel", "NKE": "Nike", "ORCL": "Oracle",
        "VZ": "Verizon", "NEE": "NextEra Energy", "PM": "Philip Morris", "MS": "Morgan Stanley",
        "BA": "Boeing", "AMD": "Advanced Micro Devices", "BMY": "Bristol-Myers Squibb",
        "UPS": "United Parcel Service", "TMUS": "T-Mobile"
    }

    company_name = ticker_map.get(ticker.upper(), "")
    if company_name:
        st.subheader(f"{ticker} - {company_name}")
    else:
        st.subheader(f"{ticker}")
    query = ticker_map.get(ticker.upper(), ticker.upper())
    if query == ticker:
        query += " stock"
    url = (
        f"https://newsdata.io/api/1/news?apikey={api_key}&q={query}&language=en&country=us&category=business,technology"
    )

    try:
        res = requests.get(url)
        if res.status_code != 200:
            st.error(f"News API error: {res.status_code}: {res.text}")
            return pd.DataFrame(columns=["headline", "compound"])
        data = res.json()
        if not isinstance(data, dict) or "results" not in data:
            st.error("Unexpected response format from Newsdata API.")
            return pd.DataFrame(columns=["headline", "compound"])

        articles = data["results"]
        headlines = [a.get("title") for a in articles if a.get("title")]

        if not headlines:
            return pd.DataFrame(columns=["headline", "compound"])

        analyzer = SentimentIntensityAnalyzer()
        sentiment_data = [
            {"headline": h, "compound": analyzer.polarity_scores(h)["compound"]}
            for h in headlines
        ]
        return pd.DataFrame(sentiment_data)

    except Exception as e:
        st.error(f"Error fetching news: {e}")
        return pd.DataFrame(columns=["headline", "compound"])
      
try:
    latest_sentiment = fetch_news_and_analyze(ticker)
except Exception as e:
    st.warning(f"Sentiment analysis failed: {e}")
    latest_sentiment = pd.DataFrame(columns=["headline", "compound"])

avg_sent = latest_sentiment["compound"].mean() if not latest_sentiment.empty else 0.0
def sentiment_label(score):
    if score >= 0.2:
        return "Positive"
    elif score <= -0.2:
        return "Negative"
    else:
        return "Neutral" 
sentiment_summary = sentiment_label(avg_sent)
col4.metric("News Sentiment", f"{avg_sent:.2f}", sentiment_summary)
# -------------------- CHART ------------------------
valid_cols = []
for col in [close_col, "RSI", "MACD", "SMA_50", "SMA_200"]:
    if col in df.columns:
        try:
            if df[col].notna().any():
                valid_cols.append(col)
        except Exception as e:
            st.warning(f"Could not validate column {col}: {e}")

if "Date" in df.columns and valid_cols:
    chart_df = df[["Date"] + valid_cols].dropna()
    chart_df.set_index("Date", inplace=True)
    if not chart_df.empty:
        st.subheader("Price / Technical Chart")
        st.line_chart(chart_df, use_container_width=True)
    else:
        st.info("No data available for plotting.")
else:
    st.info("Not enough data to chart.")
# -------------------- NEWS TABLE -------------------
st.subheader("Latest News & Sentiment")
if latest_sentiment.empty:
    st.info("No news found.")
else:
    st.dataframe(latest_sentiment.copy(), use_container_width=True)
# -------------------- RAW DATA VIEW ----------------
with st.expander("Show Raw Price Data"):
    cols_to_exclude = ["RSI", "MACD", "SMA_50", "SMA_200"]
    raw_df = df.drop(columns=[col for col in cols_to_exclude if col in df.columns])
    st.dataframe(raw_df, use_container_width=True)

st.caption("""
- Price data from [Yahoo Finance](https://finance.yahoo.com)
- News powered by [Newsdata.io](https://newsdata.io)
- Sentiment via [VADER SentimentIntensityAnalyzer]
""")
