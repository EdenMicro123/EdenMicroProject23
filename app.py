
import streamlit as st
import numpy as np
import plotly.graph_objects as go

def calculate_pnl(expiration_price, legs):
    pnl = 0
    for leg in legs:
        direction = leg['direction']
        option_type = leg['option_type']
        strike_price = leg['strike_price']
        premium = leg['premium']
        quantity = leg['quantity']
        contract_size = leg['contract_size']

        if option_type == 'call':
            if direction == 'client buy':
                pnl += quantity * contract_size * (max(0, expiration_price - strike_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, expiration_price - strike_price))
        else:  # put option
            if direction == 'client buy':
                pnl += quantity * contract_size * (max(0, strike_price - expiration_price) - premium)
            else:
                pnl += quantity * contract_size * (premium - max(0, strike_price - expiration_price))

    return pnl

def calculate_max_gain_loss(legs):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 1000)
    pnl = [calculate_pnl(price, legs) for price in expiration_prices]

    max_loss = min(pnl)
    max_gain = max(pnl)

    has_unlimited_loss = False
    has_unlimited_gain = False

    for leg in legs:
        if leg['option_type'] == 'call' and leg['direction'] == 'client sell':
            if not any(other_leg['option_type'] == 'call' and other_leg['direction'] == 'client buy' and other_leg['quantity'] >= leg['quantity'] for other_leg in legs):
                has_unlimited_loss = True
        if leg['option_type'] == 'put' and leg['direction'] == 'client sell':
            if not any(other_leg['option_type'] == 'put' and other_leg['direction'] == 'client buy' and other_leg['quantity'] >= leg['quantity'] for other_leg in legs):
                has_unlimited_loss = True

        if leg['option_type'] == 'call' and leg['direction'] == 'client buy':
            if not any(other_leg['option_type'] == 'call' and other_leg['direction'] == 'client sell' and other_leg['quantity'] >= leg['quantity'] for other_leg in legs):
                has_unlimited_gain = True
        if leg['option_type'] == 'put' and leg['direction'] == 'client buy':
            if not any(other_leg['option_type'] == 'put' and other_leg['direction'] == 'client sell' and other_leg['quantity'] >= leg['quantity'] for other_leg in legs):
                has_unlimited_gain = True

    if has_unlimited_loss:
        max_loss = 'Unlimited'
    if has_unlimited_gain:
        max_gain = 'Unlimited'

    return max_gain, max_loss

def plot_payoff_chart(legs):
    expiration_prices = np.linspace(0, 2 * max(leg['strike_price'] for leg in legs), 500)
    pnl = [calculate_pnl(price, legs) for price in expiration_prices]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=expiration_prices, y=pnl, mode='lines', name='Payoff'))

    for leg in legs:
        fig.add_vline(x=leg['strike_price'], line=dict(color='red', dash='dash'), 
                      annotation_text=f'Strike Price {leg["strike_price"]}')

    fig.update_layout(
        title='Option Strategy Payoff Chart',
        xaxis_title='Expiration Price',
        yaxis_title='P&L',
        showlegend=False
    )

    st.plotly_chart(fig)

st.title('Dynamic Options Strategy Calculator')
# Add a footnote at the bottom of the interface
st.markdown("---")
st.markdown("**Note:** This model calculates P&L and other metrics from the client's perspective. Please ensure that all data inputs are accurate for correct analysis.")

# Increased the max_value for num_legs to 100
num_legs = st.number_input('Enter Number of Legs', min_value=1, max_value=100, value=1)

legs = []
for i in range(num_legs):
    with st.expander(f'Leg {i + 1} Details'):
        direction = st.selectbox(f'Direction for Leg {i + 1}', ['client buy', 'client sell'], key=f'direction_{i}')
        option_type = st.selectbox(f'Option Type for Leg {i + 1}', ['call', 'put'], key=f'option_type_{i}')
        strike_price = st.number_input(f'Strike Price for Leg {i + 1}', value=100.0, key=f'strike_price_{i}')
        premium = st.number_input(f'Premium for Leg {i + 1}', value=1.0, key=f'premium_{i}')
        quantity = st.number_input(f'Quantity for Leg {i + 1}', value=1, key=f'quantity_{i}')
        contract_size = st.number_input(f'Contract Size for Leg {i + 1}', value=100, key=f'contract_size_{i}')

        legs.append({
            'direction': direction,
            'option_type': option_type,
            'strike_price': strike_price,
            'premium': premium,
            'quantity': quantity,
            'contract_size': contract_size
        })

if st.button('Calculate Maximum Gain and Loss'):
    max_gain, max_loss = calculate_max_gain_loss(legs)
    
    st.write(f'Maximum Gain: {max_gain}')
    st.write(f'Maximum Loss: {max_loss}')
    
    plot_payoff_chart(legs)

expiration_price_input = st.number_input('Enter Specific Expiration Price', value=100.0)
pnl_at_expiration = calculate_pnl(expiration_price_input, legs)
st.write(f'Gain/Loss at Given Expiration Price: {pnl_at_expiration:.2f}')
