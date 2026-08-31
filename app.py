import streamlit as st
import plotly.express as px
from database import load_history, get_latest_snapshot
import subprocess

st.set_page_config(page_title="PS4 Slim 1TB Price Tracker", page_icon="🎮", layout="wide")

st.title("🎮 PS4 Slim 1TB Price & Inventory Tracker")
st.caption("Live monitoring across GameLoot, GameNation, DACBY, and Cashify | Delivery: Chandigarh (160022)")

# Sidebar Controls
with st.sidebar:
    st.header("⚙️ Dashboard Controls")
    if st.button("🔄 Trigger Live Price Refresh"):
        with st.spinner("Scraping current platform prices..."):
            subprocess.run(["python", "scraper.py"])
        st.success("Prices updated!")
        st.rerun()
    st.markdown("---")
    st.markdown("**Filters**")
    in_stock_only = st.checkbox("Show In-Stock Only", value=True)

# Fetch Data
latest_df = get_latest_snapshot()
history_df = load_history()

if in_stock_only and not latest_df.empty:
    latest_df = latest_df[latest_df["in_stock"] == 1]

# Summary KPI Cards
if not latest_df.empty:
    cheapest = latest_df.loc[latest_df["price"].idxmin()]
    col1, col2, col3 = st.columns(3)
    col1.metric("Lowest Active Price", f"₹{cheapest['price']:,.0f}", f"On {cheapest['platform']}")
    col2.metric("Platforms Monitored", len(latest_df["platform"].unique()))
    col3.metric("Stock Availability", f"{len(latest_df)} listings ready")
    
    st.info(f"🏆 **Best Deal Right Now:** [{cheapest['platform']} - PS4 Slim {cheapest['storage']} ({cheapest['condition']}) at ₹{cheapest['price']:,.0f}]({cheapest['url']}) | *{cheapest['notes']}*")

st.markdown("---")

# Layout: Chart and Table
col_chart, col_table = st.columns([3, 2])

with col_chart:
    st.subheader("📈 Price Trend Over Time")
    if not history_df.empty:
        fig = px.line(
            history_df,
            x="timestamp",
            y="price",
            color="platform",
            markers=True,
            title="Price History by Platform",
            labels={"price": "Price (₹)", "timestamp": "Recorded Time", "platform": "Retailer"}
        )
        fig.update_layout(hovermode="x unified", legend=dict(orientation="h", y=-0.2))
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write("No historical data recorded yet. Run `scraper.py` to populate data.")

with col_table:
    st.subheader("📋 Current Listings")
    if not latest_df.empty:
        display_table = latest_df[["platform", "condition", "price", "in_stock", "notes", "url"]]
        display_table["in_stock"] = display_table["in_stock"].apply(lambda x: "✅ In Stock" if x == 1 else "❌ Out of Stock")
        st.dataframe(
            display_table,
            column_config={
                "url": st.column_config.LinkColumn("Product Link"),
                "price": st.column_config.NumberColumn("Price (₹)", format="₹%d")
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.write("No listings found matching criteria.")