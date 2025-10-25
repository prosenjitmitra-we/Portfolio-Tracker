import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
import json
import os
from typing import Dict, List, Tuple
import plotly.graph_objects as go
import plotly.express as px


class PortfolioTracker:
    def __init__(self, portfolio_file='portfolio.json'):
        self.portfolio_file = portfolio_file
        self.portfolio = self.load_portfolio()

    def load_portfolio(self) -> Dict:
        """Load portfolio from JSON file"""
        if os.path.exists(self.portfolio_file):
            with open(self.portfolio_file, 'r') as f:
                return json.load(f)
        return {'stocks': [], 'bullions': [], 'forex': []}

    def save_portfolio(self):
        """Save portfolio to JSON file"""
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=4)

    def add_stock(self, symbol: str, quantity: float, purchase_price: float):
        """Add stock to portfolio"""
        self.portfolio['stocks'].append({
            'symbol': symbol.upper(),
            'quantity': quantity,
            'purchase_price': purchase_price,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_portfolio()

    def add_bullion(self, metal: str, quantity: float, purchase_price: float):
        """Add bullion to portfolio"""
        symbol_map = {
            'Gold': 'GC=F',
            'Silver': 'SI=F',
            'Platinum': 'PL=F',
            'Palladium': 'PA=F'
        }

        self.portfolio['bullions'].append({
            'metal': metal,
            'symbol': symbol_map[metal],
            'quantity': quantity,
            'purchase_price': purchase_price,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_portfolio()

    def add_forex(self, pair: str, quantity: float, purchase_price: float):
        """Add forex pair to portfolio"""
        if not pair.endswith('=X'):
            pair = pair.upper() + '=X'

        self.portfolio['forex'].append({
            'pair': pair,
            'quantity': quantity,
            'purchase_price': purchase_price,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        self.save_portfolio()

    def get_current_price(self, symbol: str) -> Tuple[float, str]:
        """Fetch current price from Yahoo Finance"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period='1d')
            if not data.empty:
                current_price = data['Close'].iloc[-1]
                return round(current_price, 2), 'Success'
            else:
                return 0.0, 'No data'
        except Exception as e:
            return 0.0, f'Error'

    def get_portfolio_data(self) -> Tuple[pd.DataFrame, float, float, float]:
        """Get portfolio data as DataFrame with calculations"""
        all_holdings = []
        total_invested = 0
        total_current = 0

        # Process stocks
        for stock in self.portfolio['stocks']:
            symbol = stock['symbol']
            qty = stock['quantity']
            buy_price = stock['purchase_price']
            current_price, status = self.get_current_price(symbol)

            if current_price > 0:
                invested = qty * buy_price
                current_value = qty * current_price
                pnl = current_value - invested
                pnl_pct = (pnl / invested) * 100

                total_invested += invested
                total_current += current_value

                all_holdings.append({
                    'Type': '📈 Stock',
                    'Symbol': symbol,
                    'Quantity': qty,
                    'Buy Price': f"${buy_price:.2f}",
                    'Current Price': f"${current_price:.2f}",
                    'Invested': invested,
                    'Current Value': current_value,
                    'P&L': pnl,
                    'P&L %': pnl_pct,
                    'Date Added': stock['date_added']
                })

        # Process bullions
        for bullion in self.portfolio['bullions']:
            metal = bullion['metal']
            symbol = bullion['symbol']
            qty = bullion['quantity']
            buy_price = bullion['purchase_price']
            current_price, status = self.get_current_price(symbol)

            if current_price > 0:
                invested = qty * buy_price
                current_value = qty * current_price
                pnl = current_value - invested
                pnl_pct = (pnl / invested) * 100

                total_invested += invested
                total_current += current_value

                all_holdings.append({
                    'Type': '🥇 Bullion',
                    'Symbol': metal,
                    'Quantity': qty,
                    'Buy Price': f"${buy_price:.2f}",
                    'Current Price': f"${current_price:.2f}",
                    'Invested': invested,
                    'Current Value': current_value,
                    'P&L': pnl,
                    'P&L %': pnl_pct,
                    'Date Added': bullion['date_added']
                })

        # Process forex
        for fx in self.portfolio['forex']:
            pair = fx['pair']
            qty = fx['quantity']
            buy_price = fx['purchase_price']
            current_price, status = self.get_current_price(pair)

            if current_price > 0:
                invested = qty * buy_price
                current_value = qty * current_price
                pnl = current_value - invested
                pnl_pct = (pnl / invested) * 100

                total_invested += invested
                total_current += current_value

                all_holdings.append({
                    'Type': '💱 Forex',
                    'Symbol': pair.replace('=X', ''),
                    'Quantity': qty,
                    'Buy Price': f"{buy_price:.4f}",
                    'Current Price': f"{current_price:.4f}",
                    'Invested': invested,
                    'Current Value': current_value,
                    'P&L': pnl,
                    'P&L %': pnl_pct,
                    'Date Added': fx['date_added']
                })

        df = pd.DataFrame(all_holdings)
        total_pnl = total_current - total_invested if total_invested > 0 else 0

        return df, total_invested, total_current, total_pnl

    def remove_holding(self, category: str, index: int):
        """Remove a holding from portfolio"""
        if category in self.portfolio and 0 <= index < len(self.portfolio[category]):
            self.portfolio[category].pop(index)
            self.save_portfolio()
            return True
        return False

    def clear_portfolio(self):
        """Clear all holdings"""
        self.portfolio = {'stocks': [], 'bullions': [], 'forex': []}
        self.save_portfolio()


# Streamlit Page Configuration
st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .big-font {
        font-size:50px !important;
        font-weight: bold;
    }
    .metric-positive {
        color: #00ff00;
    }
    .metric-negative {
        color: #ff0000;
    }
    </style>
    """, unsafe_allow_html=True)

# Initialize tracker
if 'tracker' not in st.session_state:
    st.session_state.tracker = PortfolioTracker()

tracker = st.session_state.tracker

# Title
st.markdown("<h1 style='text-align: center; color: #4CAF50;'>📊 Portfolio Tracker</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Real-time Stock, Bullion & Forex Price Tracker</p>", unsafe_allow_html=True)
st.markdown("---")

# Sidebar for adding holdings
with st.sidebar:
    st.header("➕ Add Holdings")

    asset_type = st.selectbox("Select Asset Type", ["Stock", "Bullion", "Forex"])

    if asset_type == "Stock":
        st.subheader("📈 Add Stock")
        stock_symbol = st.text_input("Stock Symbol", placeholder="e.g., AAPL, TSLA, GOOGL")
        stock_quantity = st.number_input("Quantity", min_value=0.01, value=1.0, step=0.01)
        stock_price = st.number_input("Purchase Price ($)", min_value=0.01, value=100.0, step=0.01)

        if st.button("Add Stock", type="primary"):
            if stock_symbol:
                tracker.add_stock(stock_symbol, stock_quantity, stock_price)
                st.success(f"✅ Added {stock_quantity} shares of {stock_symbol.upper()}")
                st.rerun()
            else:
                st.error("Please enter a stock symbol")

    elif asset_type == "Bullion":
        st.subheader("🥇 Add Bullion")
        metal = st.selectbox("Select Metal", ["Gold", "Silver", "Platinum", "Palladium"])
        bullion_quantity = st.number_input("Quantity (oz)", min_value=0.01, value=1.0, step=0.01)
        bullion_price = st.number_input("Purchase Price per oz ($)", min_value=0.01, value=2000.0, step=0.01)

        if st.button("Add Bullion", type="primary"):
            tracker.add_bullion(metal, bullion_quantity, bullion_price)
            st.success(f"✅ Added {bullion_quantity} oz of {metal}")
            st.rerun()

    else:  # Forex
        st.subheader("💱 Add Forex")
        forex_pair = st.text_input("Forex Pair", placeholder="e.g., EURUSD, GBPUSD")
        forex_quantity = st.number_input("Quantity", min_value=0.01, value=1000.0, step=0.01)
        forex_price = st.number_input("Purchase Price", min_value=0.0001, value=1.0000, step=0.0001, format="%.4f")

        if st.button("Add Forex", type="primary"):
            if forex_pair:
                tracker.add_forex(forex_pair, forex_quantity, forex_price)
                st.success(f"✅ Added {forex_quantity} units of {forex_pair.upper()}")
                st.rerun()
            else:
                st.error("Please enter a forex pair")

    st.markdown("---")

    # Management section
    st.header("⚙️ Manage Portfolio")

    if st.button("🔄 Refresh Prices", use_container_width=True):
        st.rerun()

    if st.button("🗑️ Clear Portfolio", use_container_width=True, type="secondary"):
        tracker.clear_portfolio()
        st.success("Portfolio cleared!")
        st.rerun()

# Main content area
df, total_invested, total_current, total_pnl = tracker.get_portfolio_data()

if not df.empty:
    # Portfolio Summary Cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("💰 Total Invested", f"${total_invested:,.2f}")

    with col2:
        st.metric("📈 Current Value", f"${total_current:,.2f}")

    with col3:
        pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
        st.metric("💵 Total P&L", f"${total_pnl:,.2f}", f"{pnl_pct:+.2f}%")

    with col4:
        total_holdings = len(df)
        st.metric("📊 Total Holdings", total_holdings)

    st.markdown("---")

    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Holdings", "📊 Charts", "🔍 Details", "🗑️ Remove"])

    with tab1:
        st.subheader("Current Holdings")

        # Display DataFrame with formatted values
        display_df = df[['Type', 'Symbol', 'Quantity', 'Buy Price', 'Current Price', 'P&L %']].copy()


        # Color code P&L %
        def color_pnl(val):
            if isinstance(val, (int, float)):
                color = 'green' if val >= 0 else 'red'
                return f'color: {color}; font-weight: bold'
            return ''


        styled_df = display_df.style.applymap(color_pnl, subset=['P&L %'])
        st.dataframe(styled_df, use_container_width=True, height=400)

    with tab2:
        st.subheader("Portfolio Visualization")

        col1, col2 = st.columns(2)

        with col1:
            # Pie chart for asset allocation
            fig_pie = px.pie(
                df,
                values='Current Value',
                names='Symbol',
                title='Asset Allocation by Value',
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        with col2:
            # Bar chart for P&L
            fig_bar = px.bar(
                df,
                x='Symbol',
                y='P&L',
                title='Profit/Loss by Holding',
                color='P&L',
                color_continuous_scale=['red', 'yellow', 'green'],
                labels={'P&L': 'Profit/Loss ($)'}
            )
            fig_bar.update_layout(showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

        # Asset type distribution
        type_summary = df.groupby('Type')['Current Value'].sum().reset_index()
        fig_type = px.bar(
            type_summary,
            x='Type',
            y='Current Value',
            title='Portfolio Distribution by Asset Type',
            color='Type',
            text_auto='.2f'
        )
        fig_type.update_traces(texttemplate='$%{text:,.0f}', textposition='outside')
        st.plotly_chart(fig_type, use_container_width=True)

    with tab3:
        st.subheader("Detailed Holdings Information")

        # Full detailed table
        detail_df = df.copy()
        detail_df['Invested'] = detail_df['Invested'].apply(lambda x: f"${x:,.2f}")
        detail_df['Current Value'] = detail_df['Current Value'].apply(lambda x: f"${x:,.2f}")
        detail_df['P&L'] = detail_df['P&L'].apply(lambda x: f"${x:,.2f}")
        detail_df['P&L %'] = detail_df['P&L %'].apply(lambda x: f"{x:+.2f}%")

        st.dataframe(detail_df, use_container_width=True, height=500)

        # Download CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download Portfolio as CSV",
            data=csv,
            file_name=f"portfolio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

    with tab4:
        st.subheader("Remove Holdings")

        # Group by category
        categories = {'stocks': '📈 Stocks', 'bullions': '🥇 Bullions', 'forex': '💱 Forex'}

        for cat_key, cat_name in categories.items():
            holdings = tracker.portfolio[cat_key]
            if holdings:
                st.write(f"**{cat_name}**")
                for idx, holding in enumerate(holdings):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        if cat_key == 'stocks':
                            st.write(
                                f"{idx}. {holding['symbol']} - {holding['quantity']} shares @ ${holding['purchase_price']}")
                        elif cat_key == 'bullions':
                            st.write(
                                f"{idx}. {holding['metal']} - {holding['quantity']} oz @ ${holding['purchase_price']}")
                        else:
                            st.write(
                                f"{idx}. {holding['pair']} - {holding['quantity']} units @ {holding['purchase_price']}")
                    with col2:
                        if st.button(f"🗑️ Remove", key=f"remove_{cat_key}_{idx}"):
                            tracker.remove_holding(cat_key, idx)
                            st.success("Removed!")
                            st.rerun()
                st.markdown("---")

else:
    # Empty state
    st.info("👈 Start by adding holdings from the sidebar!")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### 📈 Stocks")
        st.write("Track your stock investments with real-time prices")
    with col2:
        st.markdown("### 🥇 Bullions")
        st.write("Monitor gold, silver, platinum & palladium prices")
    with col3:
        st.markdown("### 💱 Forex")
        st.write("Follow currency pair movements")

# Footer
st.markdown("---")
st.markdown(
    f"<p style='text-align: center; color: gray;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Data from Yahoo Finance</p>",
    unsafe_allow_html=True)