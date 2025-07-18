# Investor Sentiment Analysis Dashboard

This Streamlit app visualizes real-time stock performance using technical indicators such as RSI, MACD, SMA, and price trends, combined with live news headlines and VADER-based sentiment analysis. Users can input any stock ticker and view updated metrics, interactive technical charts, and recent news sentiment to support smarter trading insights.

## Key Features

- Calculates and displays technical indicators, including RSI, MACD, SMA-50, and SMA-200, using price data sourced via Yahoo Finance.
- Shows key price metrics (e.g., last close, high, low, volume) and dynamically updates charts for user-selected stocks and timeframes.
- Integrates live news headlines by mapping tickers to company names, improving relevance and retrieval via NewsAPI.
- Analyzes news sentiment using VADER, assigning a sentiment score to each headline and presenting an aggregate sentiment metric for the selected ticker.
- Provides an interactive, user-friendly dashboard for rapid exploration and informed decision-making.

## How It Works

1. **User Input:**  
   - Enter a valid stock ticker (e.g., TSLA, AAPL) and select desired historical range.
2. **Data Retrieval and Processing:**  
   - Fetches historical price data and computes technical indicators.
   - Maps ticker symbols to company names for more accurate news searches.
3. **Visualization:**  
   - Displays interactive charts with selected technical overlays and price trends.
   - Presents real-time metrics and technical values in a metrics bar.
4. **Sentiment Analysis:**  
   - Retrieves recent news headlines using company names.
   - Applies VADER sentiment analysis on headlines, displays scores and calculates an overall sentiment metric.
5. **News Table:**  
   - Renders the most recent headlines alongside their sentiment values.

## Requirements

- Python 3.7+
- `streamlit`, `yfinance`, `pandas`, `pandas_ta`, `requests`, `vaderSentiment`
- NewsAPI key ([https://newsapi.org](https://newsapi.org))  

## Getting Started

1. Install dependencies:
   pip install streamlit yfinance pandas pandas_ta requests vaderSentiment

2. Insert your NewsAPI key:
   - Secure method: add it to `.streamlit/secrets.toml`
   - Or, for local testing, define it directly in the script.
     
3. Run the app:
   streamlit run app.py

4. Use the sidebar to select a ticker and timeframe, then review the dashboard results.

## Example Usage
Ticker: TSLA
Period: 6mo

Displayed:
- Price and technical indicator charts
- Last close: $208.62
- RSI: 55.04
- News sentiment: 0.21 (average of headline scores)
- Latest news headlines with individual sentiment values

## License
This project is licensed under the MIT License.

## Contact
For questions or suggestions, contact: sahar.agarwal_ug2023@ashoka.edu.in 
