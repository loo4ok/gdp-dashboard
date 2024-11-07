import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
from datetime import date, timedelta

# Initialize the Streamlit app
st.title("Stock Price Simulation App")

# Sidebar inputs
stock_symbol = st.sidebar.text_input("Enter Stock Ticker", "AAPL")
start_date = st.sidebar.date_input("Start Date", date.today())
simulation_days = st.sidebar.number_input("Simulation Period (days)", min_value=1, max_value=365, value=30)

# Set a fixed random seed for reproducibility
random_seed = 0

# Fetch the historical data for the selected stock and start date
try:
    stock_data = yf.download(stock_symbol, start=start_date, end=start_date + timedelta(days=1))
    
    if not stock_data.empty and 'Close' in stock_data.columns:
        initial_price = float(stock_data['Close'].iloc[0])
        st.sidebar.write(f"Starting Price for {stock_symbol} on {start_date}: ${initial_price:.2f}")
    else:
        st.sidebar.warning(f"No data available for {stock_symbol} on {start_date}. Using default initial price of $100.")
        initial_price = 100.0
except Exception as e:
    st.sidebar.error(f"Error fetching stock data: {e}")
    initial_price = 100.0

# Calculate average daily return and volatility over the last 3 months
end_date = date.today()
three_months_ago = end_date - timedelta(days=90)

try:
    recent_data = yf.download(stock_symbol, start=three_months_ago, end=end_date)
    if not recent_data.empty and 'Close' in recent_data.columns:
        daily_returns = recent_data['Close'].pct_change().dropna()
        avg_daily_return = daily_returns.mean() * 100
        avg_daily_volatility = daily_returns.std() * 100
    else:
        avg_daily_return = 0.1
        avg_daily_volatility = 1.0
except Exception as e:
    st.sidebar.error(f"Error calculating average daily metrics: {e}")
    avg_daily_return = 0.1
    avg_daily_volatility = 1.0

# Set sliders for positive scenario
st.sidebar.markdown("### Positive Scenario")
positive_return = st.sidebar.slider(
    "Expected Daily Return (%) for Positive Scenario \n By default Expected Daily Return calculated from the average daily return for last three months", 
    min_value=-5.0, max_value=5.0, value=float(avg_daily_return)
)
positive_volatility = st.sidebar.slider(
    "Daily Volatility (%) for Positive Scenario", 
    min_value=0.0, max_value=5.0, value=float(avg_daily_volatility)
)

# Set sliders for negative scenario
st.sidebar.markdown("### Negative Scenario")
negative_return = st.sidebar.slider(
    "Expected Daily Return (%) for Negative Scenario", 
    min_value=-5.0, max_value=5.0, value=float(avg_daily_return) - 1.0
)
negative_volatility = st.sidebar.slider(
    "Daily Volatility (%) for Negative Scenario", 
    min_value=0.0, max_value=5.0, value=float(avg_daily_volatility)
)

# Set random seed for reproducibility
np.random.seed(random_seed)

# Simulation for positive scenario
random_positive_returns = np.random.normal(positive_return / 100, positive_volatility / 100, simulation_days)
positive_price_path = [initial_price]
for ret in random_positive_returns:
    positive_price_path.append(positive_price_path[-1] * (1 + ret))

# Simulation for negative scenario
random_negative_returns = np.random.normal(negative_return / 100, negative_volatility / 100, simulation_days)
negative_price_path = [initial_price]
for ret in random_negative_returns:
    negative_price_path.append(negative_price_path[-1] * (1 + ret))

# Plot both scenarios
fig, ax = plt.subplots()
ax.plot(positive_price_path, label=f"{stock_symbol} Positive Scenario", color='green')
ax.plot(negative_price_path, label=f"{stock_symbol} Negative Scenario", color='red')
ax.set_xlabel("Days")
ax.set_ylabel("Price")
ax.set_title(f"{stock_symbol} Stock Price Simulation - Positive vs Negative Scenario")
ax.legend()

# Display the plot in Streamlit app
st.pyplot(fig)

# Display the simulated price path data
st.write("### Simulated Price Path Data")
simulated_data = pd.DataFrame({
    "Day": range(simulation_days + 1),
    "Positive Scenario Price": positive_price_path,
    "Negative Scenario Price": negative_price_path
})
st.write(simulated_data)

