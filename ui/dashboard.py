import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/netflow"

st.title("📊 Polygon → Binance Net Flow Dashboard")

try:
    response = requests.get(API_URL)
    data = response.json()

    if "net_flow" in data:
        st.metric("Cumulative Inflow", f"{data['cumulative_inflow']:.2f} POL")
        st.metric("Cumulative Outflow", f"{data['cumulative_outflow']:.2f} POL")
        st.metric("Net Flow", f"{data['net_flow']:.2f} POL")
    else:
        st.warning("No data available yet. Start the indexer.")
except Exception as e:
    st.error(f"Error connecting to API: {e}")
